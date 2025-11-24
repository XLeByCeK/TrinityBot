import os
from flask import Flask, request, jsonify
import api
import commands


app = Flask(__name__)

@app.route('/webhook', methods=["POST"])
def webhook():

    data = request.json
    print("WEBHOOK:", data)

    update_type = data.get('update_type')

    if update_type == 'message_created':
        
        commands.showMenuBtn(data)

    if update_type == 'message_callback':
        
        callback = data.get('callback', {})
        payload = callback.get('payload', {})

        if payload == 'open_menu':
            
            commands.showMenu(data)

        if payload == 'menu_1':
            
            commands.responseMenu1(data)

        if payload == 'menu_2':
            
            commands.responseMenu2(data)
            
        if payload == 'send_message':

            commands.send_message(data)

    return jsonify({'ok': True})


if __name__ == "__main__":

    api.register_webhook()

    app.run(port=8443, debug=True)