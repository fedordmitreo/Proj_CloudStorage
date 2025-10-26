import requests

token = "**"
chat_id = -1

def log(message: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_to_message_id": 1
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"[LOG ERROR] Не удалось отправить в Telegram: {e}")


