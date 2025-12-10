import commands
import getData
from redis_client import redis_conn
import db
import api

CALLBACK_HANDLERS = {

    'begin_work': commands.beginWork,
    'enter_inn': commands.askInn,
    'get_report': commands.chooseReport,
    'about_trinity': commands.aboutTrinity,
    'instructions': commands.instructions,
    'how_it_works': commands.howItWorks,
    'about_audit_protocol': commands.aboutAuditProtocol,
    'about_audit_tkp': commands.aboutAuditTKP,
    'consultations': commands.consultations,
    'file_question': commands.fileQuestion,
    'trinity_ai_question': commands.trinityAiQuestion,
    'back_to_main': commands.showMenuBtns,
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

    state = get_state(getData.getSenderUserId(data))

    if update_type == 'message_callback':
            
        handle_callback(data)


    if state == "awaiting_inn":

        if update_type == "message_created":

            inn = msg_text.strip()

            if len(inn) in (10, 12) and inn.isdigit():

                org_id = db.register_organization(inn, data)

                if org_id:

                    user_id = getData.getSenderUserId(data)
                    chat_id = getData.getChatId(data)

                    db.link_user_to_org(user_id, org_id)
                    db.link_org_to_chat(org_id, chat_id)

                    api.api_request('POST', f'/messages?chat_id={chat_id}', json={"text": "Организация успешно зарегистрирована!"})

                    commands.showMenuBtns(data)
                else:

                    commands.inn_error_response(data)
            else:

                api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Неверный формат ИНН. Введите 10 или 12 цифр."})

            set_state(getData.getSenderUserId(data), "default")
            
        return
    

    if state == "support_chat":

        if update_type == "message_created":

            commands.chat_error_response(data)

        return
    

    if state == 'default':

        if update_type == 'message_created':

            if attachment_type == 'image':

                commands.chat_error_response(data)

            elif msg_text == 'Отправь файл':

                commands.send_message_with_file(data)

            elif msg_text == 'Закрепи сообщение':

                commands.chat_error_response(data)       
    
def group_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created':

        if attachment_type == 'image':

            commands.update_img(data)

        elif msg_text == 'Отправь файл':

            commands.send_message_with_file(data)

        elif msg_text == 'Закрепи сообщение':

            commands.pin_message(data)

        else:

            commands.showMenuBtns(data)
    
    elif update_type == 'message_callback':
        
        handle_callback(data)
        