import requests

from api import TOKEN


def get_sender_user_id(data):

    return (

        data.get('message', {})
            .get('sender', {})
            .get('user_id')

    )


def get_recipient_user_id(data):

    return (

        data.get('message', {})
            .get('recipient', {})
            .get('user_id')

    )


def get_file_token(filepath, filename):

    upload_url_response = requests.post(
        "https://platform-api.max.ru/uploads?type=file",
        headers={"Authorization": TOKEN}
    )

    upload_url = upload_url_response.json().get("url")

    if not upload_url:
        return None  

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

    return upload_response.json().get("token")  


def get_message_id(data):

    return (

        data.get('message', {})
            .get('body', {})
            .get('mid')

    )


def get_chat_id(data):

    return (

        data.get('message', {})
            .get('recipient', {})
            .get('chat_id')
            
    )
