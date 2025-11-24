from api import TOKEN
import requests
def getSenderUserId(data):

    sender_user_id = data['message']['sender']['user_id']

    return sender_user_id

def getRecipientUserId(data):

    recipient_user_id = data['message']['recipient']['user_id']

    return recipient_user_id

def getFileToken(filepath, filename):

    upload_url_response = requests.post("https://platform-api.max.ru/uploads?type=file", headers={"Authorization": TOKEN})

    upload_url = upload_url_response.json()["url"]

    with open(filepath, "rb") as file:
        file_content = file.read()
    
    file_size = len(file_content)
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(file_size),
        'Content-Range': f'bytes 0-{file_size-1}/{file_size}',  
        'Content-Disposition': f'attachment; filename="{filename}"'  
    }
    
    upload_response = requests.post(
        upload_url,
        data=file_content,
        headers=headers
    )

    file_token = upload_response.json()["token"]

    return file_token

def getMessageId(data):


    message_id = data['message']['body']['mid']

    return message_id

def getChatId(data):

    chat_id = data['message']['recipient']['chat_id']
    
    return chat_id
