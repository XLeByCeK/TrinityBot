def btn_callback(text: str, payload: str):

    return {

        "type": "callback",
        "text": text,
        "payload": payload

    }


def btn_link(text: str, url: str):
    
    return {

        "type": "link",
        "text": text,
        "url": url

    }


def keyboard(*rows):

    return {

        "type": "inline_keyboard",
        "payload": {"buttons": list(rows)}
    }


def message(text: str, *attachments):

    body = {"text": text}

    if attachments:

        body["attachments"] = list(attachments)

    return body