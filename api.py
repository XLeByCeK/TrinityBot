import os

from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN =  os.getenv('TOKEN')
FNS_API_KEY = os.getenv("FNS_API_KEY")
PROCESSING_API_KEY = os.getenv("X-API-KEY")
EXTERNAL_API_URL = "http://46.21.247.224:8002/api/v1/process"
WEBHOOK_URL = "https://poetless-jamar-overdepressively.ngrok-free.dev/webhook"
API_BASE = "https://platform-api.max.ru"

session = requests.Session()
session.headers.update({

    "Authorization": TOKEN,
    "Content-Type": "application/json"

})


def clear_subscriptions():

    print("\n=== Получаю список подписок ===")

    resp = session.get(f"{API_BASE}/subscriptions")
    data = resp.json()

    subs = data.get("subscriptions", [])

    print("Текущие подписки:", subs)

    if not subs:
        print("Подписок нет.")
        return

    print("\n=== Удаляю подписки по URL ===")

    for sub in subs:
        url = sub["url"]
        del_resp = session.delete(
            f"{API_BASE}/subscriptions",
            params={"url": url}
        )
        print(f"Удаляю подписку URL={url}: {del_resp.status_code} {del_resp.text}")

    print("\n=== Все подписки удалены ===")

def register_webhook():

    data = {
        "url": WEBHOOK_URL,
        "update_types": [
            "message_created", "message_callback", "message_edited",
            "message_removed", "bot_added", "bot_removed",
            "user_added", "user_removed", "chat_title_changed",
            "message_chat_created"
        ]
    }

    resp = session.post(f"{API_BASE}/subscriptions", json=data)
    print("Webhook registration response:", resp.text)

def api_request(method, path, json=None, files=None):
    
    url = f"{API_BASE}{path}"

    resp = session.request(method, url, json=json, files=files)
    resp.raise_for_status()
    return resp.json()

def fetch_org_from_fns(inn):

    url = f"https://api-fns.ru/api/multinfo?req={inn}&key={FNS_API_KEY}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:

        resp = requests.get(url, timeout=10, headers=headers)
        
  
        resp.raise_for_status() 
        
        data = resp.json()

        if 'items' in data and data['items']:
            item = data['items'][0]

            if 'ЮЛ' in item:
                org_data = item['ЮЛ']
                name = org_data.get('НаимПолнЮЛ') or org_data.get('НаимСокрЮЛ')
                is_active = org_data.get('Статус') == 'Действующее'
            elif 'ИП' in item:
                org_data = item['ИП']
                name = org_data.get('ФИОПолн')
                is_active = org_data.get('Статус') == 'Действующее'
            else:
                return None

            return {'name': name, 'is_active': is_active}
        return None

    except Exception as e:
        print(f"Error fetching from FNS API: {e}")
        return None


def send_to_processing_service(payload):

    headers = {
        "X-API-Key": PROCESSING_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:

        response = requests.post(EXTERNAL_API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            print("Данные успешно отправлены в API")
            return True
        
        else:
            print(f"Ошибка внешнего API ({response.status_code}): {response.text}")
            return False
        
    except Exception as e:
        
        print(f"Ошибка при подключении к внешнему API: {e}")
        return False  
    
def get_russian_day_type(date_str):
    
    url = f'https://isdayoff.ru/{date_str}'
    try:

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Ошибка при запросе к производственному календарю: {e}")
        return None