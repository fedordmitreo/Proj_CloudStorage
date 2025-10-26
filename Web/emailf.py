import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Словарь SMTP-настроек по домену
SMTP_SERVERS = {
    "gmail.com": {
        "server": "smtp.gmail.com",
        "port": 587,
        "tls": True
    },
    "yandex.ru": {
        "server": "smtp.yandex.ru",
        "port": 587,
        "tls": True
    },
    "yandex.com": {
        "server": "smtp.yandex.ru",
        "port": 587,
        "tls": True
    },
    "mail.ru": {
        "server": "smtp.mail.ru",
        "port": 587,
        "tls": True
    },
    "bk.ru": {
        "server": "smtp.mail.ru",
        "port": 587,
        "tls": True
    },
    "list.ru": {
        "server": "smtp.mail.ru",
        "port": 587,
        "tls": True
    },
    "inbox.ru": {
        "server": "smtp.mail.ru",
        "port": 587,
        "tls": True
    },
    "outlook.com": {
        "server": "smtp-mail.outlook.com",
        "port": 587,
        "tls": True
    },
    "hotmail.com": {
        "server": "smtp-mail.outlook.com",
        "port": 587,
        "tls": True
    }
}


def get_smtp_config(email: str):
    """
    Определяет SMTP-настройки по email-адресу
    """
    # Извлекаем домен
    match = re.search(r"@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", email)
    if not match:
        raise ValueError("Неверный формат email")

    domain = match.group(1).lower()

    # Проверяем известные домены
    for known_domain, config in SMTP_SERVERS.items():
        if domain.endswith(known_domain):  # Поддержка поддоменов
            return config

    # Если домен не найден
    raise ValueError(f"SMTP-сервер для домена '{domain}' не поддерживается")


def send_email(
        to: str,
        html: bool = False
):
    """
    Отправляет email. Автоматически определяет SMTP по адресу отправителя.

    :param to: Кому (email)
    :param subject: Тема письма
    :param body: Текст письма
    :param sender: Email отправителя (обязательно с доменом)
    :param password: Пароль приложения (App Password)
    :param html: Если True — трактует body как HTML
    """

    subject = "Удаление ваших данных с сайта ВШП"

    body = """
Здравствуйте!

Мы информируем вас о том, что файлы, размещённые вами на нашем сайте, были удалены. 
Причина — использование нецензурной лексики в содержимом загруженных материалов.

Наш сервис придерживается правил, направленных на поддержание уважительной и безопасной среды для всех пользователей. 
Согласно этим правилам, публикация контента с оскорбительными или ненормативными выражениями запрещена.

Просим вас учитывать данное требование при дальнейшем использовании платформы. 
Вы можете загрузить обновлённые версии файлов, соответствующие правилам использования.

Если у вас возникли вопросы, свяжитесь с нами — мы готовы помочь.

С уважением, {company_name}
"""
    company_name = "Администрация"
    final_message = body.format(company_name=company_name)

    sender = "**"

    password = "**"


    if not sender:
        raise ValueError("Не указан EMAIL_USER (в аргументе или .env)")
    if not password:
        raise ValueError("Не указан EMAIL_PASSWORD (в аргументе или .env)")

    try:
        # Определяем SMTP-сервер
        smtp_config = get_smtp_config(sender)
        server_addr = smtp_config["server"]
        port = smtp_config["port"]

        # Создаём сообщение
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(final_message, content_type, "utf-8"))

        # Подключаемся и отправляем
        with smtplib.SMTP(server_addr, port) as server:
            server.starttls()  # Включаем шифрование
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())

        print(f"✅ Письмо отправлено на {to} через {smtp_config['server']}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Ошибка аутентификации: неверный логин или пароль")
        return False
    except smtplib.SMTPRecipientsRefused:
        print("❌ Ошибка: получатель отклонён")
        return False
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False