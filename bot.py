import chatshandler
from flask import Flask, request, jsonify
import api
import commands


app = Flask(__name__)

@app.route('/webhook', methods=["POST"])
def webhook():

    data = request.json
    print("WEBHOOK:", data)

    update_type = data.get('update_type')
    msg_text = data['message']['body']['text']
    chat_type = data['message']['recipient']['chat_type']
    user_id = data['message']['sender']['user_id']
    

    if msg_text == "/start":

        chatshandler.set_state(user_id, "default")

        commands.showMenuBtns(data)

        return jsonify({'ok': True})



    attachments = data['message']['body'].get('attachments', [])
    attachment_type = attachments[0].get('type') if attachments else None

    
    if chat_type == 'chat':
        
        chatshandler.group_chats(data, update_type, msg_text, attachment_type)
    else:

        chatshandler.private_chats(data, update_type, msg_text, attachment_type)
            

    return jsonify({'ok': True})


if __name__ == "__main__":

   api.register_webhook()

   app.run(port=8443, debug=True)