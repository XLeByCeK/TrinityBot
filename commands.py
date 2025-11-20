import api
import getData

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
                                ]
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