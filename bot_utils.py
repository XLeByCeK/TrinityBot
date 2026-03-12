import api
from datetime import datetime
import pytz

MOSCOW_TZ = pytz.timezone('Europe/Moscow')


def is_working_hours():
    now_msk = datetime.now(MOSCOW_TZ)
    date_str = now_msk.strftime('%Y%m%d')
    

    day_type = api.get_russian_day_type(date_str)
    
    if day_type is None:
        if now_msk.weekday() >= 5:  
            return False
        return 9 <= now_msk.hour < 18

    if day_type == '1':
        return False
    
    if day_type == '2':
        return 9 <= now_msk.hour < 17
    
    return 9 <= now_msk.hour < 18

def api_send(chat_id, body):
    return api.api_request("POST", f"/messages?chat_id={chat_id}", json=body)

def send_message(chat_id, text):
    api_send(chat_id, {"text": str(text)})