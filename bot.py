import chatshandler
from flask import Flask, request, jsonify
import api


app = Flask(__name__)

@app.route('/webhook', methods=["POST"])
def webhook():

    data = request.json
    print("WEBHOOK:", data)

    update_type = data.get('update_type')
    msg_text = data['message']['body']['text']
    chat_type = data['message']['recipient']['chat_type']

    attachments = data['message']['body'].get('attachments', [])
    attachment_type = None

    if attachments:
        attachment_type = attachments[0].get('type')

    
    if chat_type == 'chat':
        
        chatshandler.group_chats(data, update_type, msg_text, attachment_type)
    else:

        chatshandler.private_chats(data, update_type, msg_text, attachment_type)
            

    return jsonify({'ok': True})


if __name__ == "__main__":

   api.register_webhook()

   app.run(port=8443, debug=True)