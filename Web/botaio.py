from database import get_all_users
from aiogram import Bot, Dispatcher, types, executor


token = "TOKEN"
chat_id = 555

bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Здрасьте")



@dp.message_handler(commands=['all'])
async def all_user(message: types.Message):
    users = get_all_users()
    for name in users:
        await message.answer(name)




if __name__ == '__main__':
    executor.start_polling(dp)