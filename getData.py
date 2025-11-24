
def getSenderUserId(data):

    msg = data.get('message', {})
    sender =msg.get('sender', {})
    user_id = sender.get('user_id')

    return user_id

def getRecipientUserId(data):


    msg = data.get('message', {})
    recipient =msg.get('recipient', {})
    user_id = recipient.get('user_id')

    return user_id

