import requests

TOKEN = 'f9LHodD0cOL7zz1wHQSEmtBmHVM8JDoomUKgGOw71Ir5BKRLZ1eSlM94PU8Gq9_MnVUxVKpp1ZeBDdfICPQr'
WEBHOOK_URL = "https://poetless-jamar-overdepressively.ngrok-free.dev/webhook"
API_BASE = "https://platform-api.max.ru"


def register_webhook():
    data = {
        "url": WEBHOOK_URL,
        "update_types": ["message_created", "message_callback"]  
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