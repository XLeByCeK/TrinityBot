from redis_client import redis_conn
import commands
import get_data
import db
import json

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
    'obj_mgmt_main': commands.obj_mgmt_main,
    'obj_add_start': commands.obj_add_start,
    'obj_delete_list': commands.obj_delete_list,
}

def get_state(user_id: int) -> str:

    state = redis_conn.get(f"user:{user_id}:state")

    if state:

        return state.decode('utf-8') if isinstance(state, bytes) else state
    return "default"

def set_state(user_id: int, state: str):
    redis_conn.set(f"user:{user_id}:state", state)

def handle_callback(data):

    callback = data.get('callback', {})
    payload = callback.get('payload', {})
    user_id = callback.get('user', {}).get('user_id')

    chat_id = data.get('message', {}).get('recipient', {}).get('chat_id')

    if payload == "enter_inn":
        set_state(user_id, "awaiting_inn")

    elif payload in ("file_question", "trinity_ai_question"):

        set_state(user_id, "support_chat")
        
        if chat_id:
            db.mark_support_requested(chat_id)

    elif payload == "back_to_main":
        set_state(user_id, "default")

    if payload.startswith("obj_confirm_del_"):

        obj_id = int(payload.split("_")[-1])
        commands.obj_confirm_delete(data, obj_id)

    elif payload.startswith("obj_do_delete_"):

        obj_id = int(payload.split("_")[-1])
        commands.obj_do_delete(data, obj_id)
        

    if payload.startswith("file_target_obj_"):
        obj_id = int(payload.split("_")[-1])
        obj = db.get_construction_object_by_id(obj_id)
        

        pending_key = f"pending_files:{chat_id}:{user_id}"
        pending_raw = redis_conn.get(pending_key)

        if pending_raw and obj:

            batch = json.loads(pending_raw.decode('utf-8') if isinstance(pending_raw, bytes) else pending_raw)
            commands.send_to_api_with_obj(chat_id, batch, obj['name'], obj['address'])
            redis_conn.delete(pending_key)

    if payload in CALLBACK_HANDLERS:
        CALLBACK_HANDLERS[payload](data)

def process_state_logic(data, update_type, msg_text, attachment_type, chat_type):

    user_id = get_data.get_sender_user_id(data)
    chat_id = get_data.get_chat_id(data)
    
    if update_type == 'message_created':
        db.save_incoming_message(data)

    if update_type == 'message_callback':
        handle_callback(data)
        return

    state = get_state(user_id)

    if state == "awaiting_inn" and update_type == "message_created":
        inn = msg_text.strip()
        if len(inn) in (10, 12) and inn.isdigit():

            org_id = db.register_organization(inn, data)

            if org_id:
                db.link_user_to_org(user_id, org_id)
                db.link_org_to_chat(org_id, chat_id)

                org_name = db.get_organization_name(inn)

                commands.success_authorization(data, org_name)
                commands.show_menu_btns(data)
            else:
                commands.inn_error_response(data)
        else:
            commands.send_message(chat_id, "Неверный формат ИНН. Введите 10 или 12 цифр.")
        
        set_state(user_id, "default")
        return
    

    if state == "awaiting_obj_name" and update_type == "message_created":

        name = msg_text.strip()
        redis_conn.set(f"temp_obj_name:{user_id}", name, ex=600)

        set_state(user_id, "awaiting_obj_address")
        commands.send_message(chat_id, f"Укажите адрес {name}")

        return

    if state == "awaiting_obj_address" and update_type == "message_created":
        address = msg_text.strip()
        
        raw_name = redis_conn.get(f"temp_obj_name:{user_id}")
        
        if raw_name:

            name = raw_name.decode('utf-8') if isinstance(raw_name, bytes) else raw_name
            
            db.add_construction_object(chat_id, name, address)
            commands.send_message(chat_id, f"Добавлен объект {name} с адресом {address}")

        else:
            commands.send_message(chat_id, "Ошибка: сессия истекла. Пожалуйста, начните сначала.")
        
        set_state(user_id, "default")
        commands.obj_mgmt_main(data) 

        return

    if state == "support_chat" and update_type == "message_created":

        db.mark_support_requested(chat_id)
        commands.send_message(chat_id, "Запрос на консультацию получен. Администратор с вами свяжется.")

        return

    if state == 'default':

        if update_type == 'message_created':

            is_batching = redis_conn.exists(f"batch:{user_id}:{chat_id}")

            if attachment_type == 'file' or (is_batching and msg_text):

                commands.process_file(data, chat_type)

def private_chats(data, update_type, msg_text, attachment_type, chat_type):
    process_state_logic(data, update_type, msg_text, attachment_type, chat_type)

def group_chats(data, update_type, msg_text, attachment_type, chat_type):
    process_state_logic(data, update_type, msg_text, attachment_type, chat_type)