import requests

from dotenv import load_dotenv
import os
from time import sleep

load_dotenv()
token=os.getenv("TOKEN")

def send_telegram_message(chat_id: int | str, message: str) -> bool:
    """
    Отправляет текстовое сообщение пользователю Telegram через бота.

    :param token: Токен твоего бота (можно получить от @BotFather)
    :param chat_id: ID пользователя или чата
    :param message: Текст сообщения
    :return: True, если сообщение отправлено, иначе False
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',  # можно заменить на 'MarkdownV2' или убрать
        'disable_web_page_preview': True,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return True
            else:
                print("Telegram API error:", result.get('description'))
        else:
            print("HTTP error:", response.status_code, response.text)
    except Exception as e:
        print("Request failed:", e)
    
    return False