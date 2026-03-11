import api
from datetime import datetime
import pytz
import holidays

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
RU_HOLIDAYS = holidays.Russia()

def is_working_hours():
    now_msk = datetime.now(MOSCOW_TZ)
    if now_msk.weekday() >= 5 or now_msk.date() in RU_HOLIDAYS:
        return False
    return 9 <= now_msk.hour < 18

def api_send(chat_id, body):
    return api.api_request("POST", f"/messages?chat_id={chat_id}", json=body)

def send_message(chat_id, text):
    api_send(chat_id, {"text": str(text)})