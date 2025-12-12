from redis_client import redis_conn

import commands
import get_data

import db

import api

CALLBACK_HANDLERS = {

    'begin_work': commands.begin_work,
    'enter_inn': commands.ask_inn,
    'get_report': commands.choose_report,
    'about_trinity': commands.about_trinity,
    'instructions': commands.instructions,
    'how_it_works': commands.how_it_works,
    'about_audit_protocol': commands.about_audit_protocol,
    'about_audit_tkp': commands.about_audit_TKP,
    'consultations': commands.consultations,
    'file_question': commands.file_question,
    'trinity_ai_question': commands.trinity_AI_question,
    'back_to_main': commands.show_menu_btns,
    'back_to_instructions': commands.instructions,
    'back_to_consultations': commands.consultations,
}

def get_state(user_id: int) -> str:

    state = redis_conn.get(f"user:{user_id}:state")

    return state or "default"

def set_state(user_id: int, state: str):

    redis_conn.set(f"user:{user_id}:state", state)

def handle_callback(data):

    callback = data.get('callback', {})
    payload = callback.get('payload', {})
    user_id = callback.get('user', {}).get('user_id')

    
    if payload == "enter_inn":

        set_state(user_id, "awaiting_inn")

    elif payload in ("file_question", "trinity_ai_question"):

        set_state(user_id, "support_chat")

    elif payload == "back_to_main":

        set_state(user_id, "default")

    
    if payload in CALLBACK_HANDLERS:

        CALLBACK_HANDLERS[payload](data)
        

def private_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created':

        db.save_incoming_message(data)

    state = get_state(get_data.get_sender_user_id(data))

    if update_type == 'message_callback':
            
        handle_callback(data)


    if state == "awaiting_inn":

        if update_type == "message_created":

            inn = msg_text.strip()

            if len(inn) in (10, 12) and inn.isdigit():

                org_id = db.register_organization(inn, data)

                if org_id:

                    db.link_user_to_org(get_data.get_sender_user_id(data), org_id)
                    db.link_org_to_chat(org_id, get_data.get_chat_id(data))

                    org_name = db.get_organization_name(inn)

                    commands.success_authorization(data, org_name)
                    commands.show_menu_btns(data)

                else:

                    commands.inn_error_response(data)
            else:

                api.api_request('POST', f'/messages?chat_id={get_data.get_chat_id(data)}', json={"text": "Неверный формат ИНН. Введите 10 или 12 цифр."})

            set_state(get_data.get_sender_user_id(data), "default")
            
        return
    

    if state == "support_chat":

        if update_type == "message_created":

            commands.chat_error_response(data)

        return
    

    if state == 'default':

        if update_type == 'message_created':

            if attachment_type == 'file':

                commands.process_file(data)   
    
def group_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created':

        if attachment_type == 'image':

            commands.update_img(data)

        elif msg_text == 'Отправь файл':

            commands.process_file(data)

        elif msg_text == 'Закрепи сообщение':

            commands.pin_message(data)

        else:

            commands.show_menu_btns(data)
    
    elif update_type == 'message_callback':
        
        handle_callback(data)
        