import shutil
import os
from database import get_all_users
from emailf import send_email
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

token = "**"
chat_id = -1

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Здрасьте")
    await message.answer("all - Все пользователи"
                         "delete_files id - Удаление пользователя с соответствующем id")


# --- Состояния для диалога ---
class DeleteFiles(StatesGroup):
    waiting_for_confirm = State()     # Уверен ли админ?
    waiting_for_notify = State()      # Уведомить пользователя?

# --- Команда /delete_files ---
@dp.message_handler(commands=['delete_files'])
async def delete_user_files(message: types.Message):
    args = message.get_args().strip()

    if not args:
        await message.answer("UsageId: /delete_files <user_id>")
        return

    try:
        target_user_id = int(args)
    except ValueError:
        await message.answer("❌ ID должно быть числом.")
        return

    # Проверяем, существует ли пользователь
    users = get_all_users()
    user_data = None
    for user in users:
        user_id, name, email, is_admin = user
        if user_id == target_user_id:
            user_data = {"id": user_id, "name": name, "email": email}
            break

    if not user_data:
        await message.answer("❌ Пользователь с таким ID не найден.")
        return

    # Сохраняем данные в state
    await DeleteFiles.waiting_for_confirm.set()
    state: FSMContext = dp.current_state()
    await state.update_data(
        target_user_id=target_user_id,
        user_name=user_data["name"],
        user_email=user_data["email"]
    )

    await message.answer(
        f"Вы уверены, что хотите удалить файлы пользователя:\n"
        f"👤 {user_data['name']}\n"
        f"📧 {user_data['email']}?\n\n",
        parse_mode="HTML"
    )

# --- Обработка подтверждения ---
@dp.message_handler(state=DeleteFiles.waiting_for_confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    data = await state.get_data()

    if answer in ("да", "yes", "y", "д"):
        # Удаляем файлы
        user_upload = os.path.join('User_Files', str(data['target_user_id']))
        user_trash = os.path.join('Trash', str(data['target_user_id']))

        try:
            if os.path.exists(user_upload):
                shutil.rmtree(user_upload)
            if os.path.exists(user_trash):
                shutil.rmtree(user_trash)
            os.makedirs(user_upload, exist_ok=True)
            os.makedirs(user_trash, exist_ok=True)

            await message.answer("🗑️ Файлы пользователя успешно удалены.")

            # Переходим к следующему шагу
            await DeleteFiles.waiting_for_notify.set()
            await message.answer(
                f"Хотите отправить уведомление на email: <code>{data['user_email']}</code>?",
                parse_mode="HTML"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка при удалении файлов: {e}")
            await state.finish()

    elif answer in ("нет", "no", "n", "н"):
        await message.answer("✅ Отменено. Файлы не удалены.")
        await state.finish()
    else:
        await message.answer("Пожалуйста, отправьте <b>да</b> или <b>нет</b>.", parse_mode="HTML")

# --- Обработка уведомления ---
@dp.message_handler(state=DeleteFiles.waiting_for_notify)
async def process_notify(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    data = await state.get_data()

    if answer in ("да", "yes", "y", "д"):
        try:
            send_email(to=data['user_email'])
            await message.answer("📧 Уведомление отправлено на email.")
        except Exception as e:
            await message.answer(f"❌ Не удалось отправить email: {e}")

    await message.answer("👋 Операция завершена. Хорошего дня!")
    await state.finish()  # Завершаем состояние

@dp.message_handler(commands=['all'])
async def all_users(message: types.Message):
    try:
        users = get_all_users()  # Предполагается, что возвращает список кортежей (id, name, email, is_admin)

        if not users:
            await message.answer("❌ Нет зарегистрированных пользователей.")
            return

        # Сортируем по id (первый элемент кортежа)
        users.sort(key=lambda x: x[0])

        # Формируем красивое сообщение
        lines = ["📋 Все пользователи (отсортировано по ID):", ""]
        for user in users:
            user_id, name, email, is_admin = user
            admin_status = "✅ Админ" if is_admin else "🔹 Пользователь"
            lines.append(
                f"<b>ID {user_id}</b>\n"
                f"👤 <b>Имя:</b> {name}\n"
                f"📧 <b>Email:</b> {email}\n"
                f"🛡 <i>{admin_status}</i>\n"
            )

        response = "\n".join(lines)

        # Telegram имеет лимит ~4096 символов на сообщение
        if len(response) > 4000:
            # Если слишком длинно — разбиваем
            await message.answer("Слишком много пользователей, отправляю частями...")

            part = []
            for user in users:
                user_id, name, email, is_admin = user
                admin_status = "✅ Админ" if is_admin else "🔹 Пользователь"
                line = (
                    f"<b>ID {user_id}</b>\n"
                    f"👤 <b>Имя:</b> {name}\n"
                    f"📧 <b>Email:</b> {email}\n"
                    f"🛡 <i>{admin_status}</i>\n"
                )
                if len("\n".join(part)) + len(line) > 3500:
                    await message.answer("\n".join(part), parse_mode="HTML")
                    part = [line]
                else:
                    part.append(line)
            if part:
                await message.answer("\n".join(part), parse_mode="HTML")
        else:
            await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer("⚠️ Ошибка при получении списка пользователей.")
        print(f"Ошибка в /all: {e}")



if __name__ == '__main__':
    executor.start_polling(dp)