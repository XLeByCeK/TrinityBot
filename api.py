import requests

TOKEN = 'f9LHodD0cOL7zz1wHQSEmtBmHVM8JDoomUKgGOw71Ir5BKRLZ1eSlM94PU8Gq9_MnVUxVKpp1ZeBDdfICPQr'
WEBHOOK_URL = "https://poetless-jamar-overdepressively.ngrok-free.dev/webhook"
API_BASE = "https://platform-api.max.ru"


def clear_subscriptions():
    print("\n=== Получаю список подписок ===")

    resp = requests.get(
        f"{API_BASE}/subscriptions",
        headers={"Authorization": TOKEN}
    )
    data = resp.json()

    subs = data.get("subscriptions", [])

    print("Текущие подписки:", subs)

    if not subs:
        print("Подписок нет.")
        return

    print("\n=== Удаляю подписки по URL ===")

    for sub in subs:
        url = sub["url"]
        del_resp = requests.delete(
            f"{API_BASE}/subscriptions",
            headers={"Authorization": TOKEN},
            params={"url": url}
        )
        print(f"Удаляю подписку URL={url}: {del_resp.status_code} {del_resp.text}")

    print("\n=== Все подписки удалены ===")

def register_webhook():
    data = {
        "url": WEBHOOK_URL,
        "update_types": ["message_created", "message_callback", "message_edited", 'message_removed', 'bot_added', 'bot_removed', 'user_added', 'user_removed', 'chat_title_changed', 'message_chat_created']  
    }
    resp = requests.post(
        f"{API_BASE}/subscriptions",
        headers={"Authorization": TOKEN, "Content-Type": "application/json"},
        json=data
    )
    print("Webhook registration response:", resp.text)

def api_request(method, path, json=None, files=None):
    
    url = f'{API_BASE}{path}'
    headers = {

    'Authorization': TOKEN,

    }

    resp = requests.request(method, url, headers=headers, json=json, files=files)
    resp.raise_for_status()
    return resp.json()