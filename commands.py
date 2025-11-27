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
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def showMenu(data):

    body = {
                "text": "Выберите пункт или напишите: "
                "'Отправь файл' для отправки файла. "
                "'Закрепи сообщение' для того чтобы закрепить сообщение. "
                "Отправь картинку чтобы изменить аватарку чата.",
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
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def responseMenu1(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы нажали Пункт 1"})

def responseMenu2(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы нажали Пункт 2"})

def send_message_with_file(data):

    file_path = r'D:\Trinity\Bot\example.txt'
    filename = "example.txt"

    file_token = getData.getFileToken(file_path, filename)

    message_id = getData.getMessageId(data)

    body = {
        "text": "Сообщение с файлом и цитированием",
        "attachments": [
            {
                "type": "file",
                "payload": {
                    "token": file_token
                }
            }
        ],
        "link": {
            "type": 'reply',
            "mid": message_id
        }
    }
        
    api.api_request(
            'POST',
            f"/messages?chat_id={getData.getChatId(data)}",
            json=body
        )
    
def pin_message(data):

    message_id = getData.getMessageId(data)

    body = {
        "message_id": message_id
    }

    api.api_request('PUT', f'/chats/{getData.getChatId(data)}/pin', json=body)

def chat_error_response(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Эта функция доступна только  в групповых чатах"})

def update_img(data):

    url = data['message']['body']['attachments'][0]['payload']['url']

    body = {
        'icon': { "url": url }
    }

    api.api_request('PATCH', f'/chats/{getData.getChatId(data)}', json=body)