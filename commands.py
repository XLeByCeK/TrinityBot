import api
import getData
import requests
import urllib
def showMenuBtn(data):

    body = {
            "text": "Нажмите кнопку для открытия меню",
            "attachments": [
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "callback",
                                    "text": "Открыть меню",
                                    "payload": "open_menu"  
                                }
                            ]
                        ]
                    }
                }
            ]
        }
    
    api.api_request('POST', f'/messages?user_id={getData.getSenderUserId(data)}', json=body)

def showMenu(data):

    body = {
                "text": "Меню:",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "callback",
                                        "text": "Пункт 1",
                                        "payload": 'menu_1'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Пункт 2",
                                        "payload": "menu_2"
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Отправить сообщение",
                                        "payload": 'send_message'
                                    }
                                ],
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?user_id={getData.getRecipientUserId(data)}', json=body)

def responseMenu1(data):

    api.api_request('POST', f'/messages?user_id={getData.getRecipientUserId(data)}', json={"text": "Вы нажали Пункт 1"})

def responseMenu2(data):

    api.api_request('POST', f'/messages?user_id={getData.getRecipientUserId(data)}', json={"text": "Вы нажали Пункт 2"})

def send_message(data):


    TOKEN = 'f9LHodD0cOL7zz1wHQSEmtBmHVM8JDoomUKgGOw71Ir5BKRLZ1eSlM94PU8Gq9_MnVUxVKpp1ZeBDdfICPQr'
    upload_url_response = requests.post("https://platform-api.max.ru/uploads?type=file", headers={"Authorization": TOKEN})

    file_path = r'D:\Trinity\Bot\example.txt'
    filename = "example.txt"
    upload_url = upload_url_response.json()["url"]
    print(upload_url)

    with open(file_path, "rb") as file:
        file_content = file.read()
    
    file_size = len(file_content)
    headers = {
        'Content-Type': 'application/octet-stream',  # Для resumable
        'Content-Length': str(file_size),
        'Content-Range': f'bytes 0-{file_size-1}/{file_size}',  # Полный диапазон — фикс для 412
        'Content-Disposition': f'attachment; filename="{filename}"'  # Для имени файла
    }
    
    upload_response = requests.post(
        upload_url,
        data=file_content,
        headers=headers
    )

    file_token = upload_response.json()["token"]




    body = {
        "text": "Сообщение с файлом",
        "attachments": [
            {
                "type": "file",
                "payload": {
                    "token": file_token
                }
            }
        ]
    }
        
    api.api_request(
            'POST',
            f"/messages?user_id={getData.getRecipientUserId(data)}",
            json=body
        )