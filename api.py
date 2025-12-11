import os

from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN =  os.getenv('TOKEN')
FNS_API_KEY = os.getenv("FNS_API_KEY")
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

    try:

        resp = session.get(url, timeout=10)
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
    