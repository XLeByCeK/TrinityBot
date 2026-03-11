import get_data
import db
import ui_templates
import bot_utils
import file_service

def _send_ui(data, template_func, *args, **kwargs):
    return bot_utils.api_send(get_data.get_chat_id(data), template_func(*args, **kwargs))

def send_message(chat_id, text):
    bot_utils.send_message(chat_id, text)


def show_menu_btns(data): _send_ui(data, ui_templates.get_main_menu)

def check_authorization(data):
    """
    Проверяет, авторизован ли чат или пользователь.
    Если авторизован — отправляет сообщение об этом и возвращает True.
    """
    actual_user_id = get_data.get_sender_user_id(data)
    chat_type = get_data.get_chat_type(data)
    chat_id = get_data.get_chat_id(data)

    if chat_type == 'chat':
        authorized = db.is_chat_authorized(chat_id)
        msg = "Этот чат уже зарегистрирован за организацией."
    else:
        authorized = db.is_user_authorized(actual_user_id)
        msg = "Вы уже авторизованы."

    if authorized:
        _send_ui(data, ui_templates.get_auth_status_msg, msg)
        return True
    
    return False
def begin_work(data):
    user_id, chat_id = get_data.get_sender_user_id(data), get_data.get_chat_id(data)
    is_auth = db.is_chat_authorized(chat_id) if get_data.get_chat_type(data) == 'chat' else db.is_user_authorized(user_id)
    if is_auth:
        return bot_utils.send_message(chat_id, "Вы уже авторизованы.")
    _send_ui(data, ui_templates.get_begin_work_menu)

def ask_inn(data): 
    if not check_authorization(data): _send_ui(data, ui_templates.get_inn_request_text)

def success_authorization(data, org_name): _send_ui(data, ui_templates.get_success_auth_text, org_name)

def check_authorization(data):
    uid, cid = get_data.get_sender_user_id(data), get_data.get_chat_id(data)
    auth = db.is_chat_authorized(cid) if get_data.get_chat_type(data) == 'chat' else db.is_user_authorized(uid)
    if auth:
        _send_ui(data, ui_templates.get_auth_status_msg, "Авторизация уже пройдена.")
    return auth

# Прокси-методы для UI (одной строкой для экономии места)
def choose_report(data): _send_ui(data, ui_templates.get_report_menu)
def about_trinity(data): _send_ui(data, ui_templates.get_about_trinity_menu)
def instructions(data): _send_ui(data, ui_templates.get_instructions_menu)
def how_it_works(data): _send_ui(data, ui_templates.get_how_it_works_info)
def about_audit_protocol(data): _send_ui(data, ui_templates.get_audit_protocol_info)
def about_audit_TKP(data): _send_ui(data, ui_templates.get_audit_tkp_info)
def consultations(data): _send_ui(data, ui_templates.get_consultations_menu)
def file_question(data): _send_ui(data, ui_templates.get_file_question_info)
def trinity_AI_question(data): _send_ui(data, ui_templates.get_trinity_ai_question_info)

# --- Объекты ---
def obj_mgmt_main(data): _send_ui(data, ui_templates.get_objects_mgmt_menu)

def obj_add_start(data):
    from chatshandler import set_state
    set_state(get_data.get_sender_user_id(data), "awaiting_obj_name")
    bot_utils.send_message(get_data.get_chat_id(data), "Укажите наименование объекта")

def obj_delete_list(data):
    objs = db.get_construction_objects(get_data.get_chat_id(data))
    if not objs:
        bot_utils.send_message(get_data.get_chat_id(data), "Список пуст.")
        return obj_mgmt_main(data)
    _send_ui(data, ui_templates.get_objects_delete_list, objs)

def obj_confirm_delete(data, obj_id):
    obj = db.get_construction_object_by_id(obj_id)
    if obj: _send_ui(data, ui_templates.get_delete_confirmation, obj['name'], obj_id)

def obj_do_delete(data, obj_id):
    obj = db.get_construction_object_by_id(obj_id)
    if obj:
        db.delete_construction_object(obj_id)
        bot_utils.send_message(get_data.get_chat_id(data), f"Удалено: {obj['name']}")
    obj_mgmt_main(data)


def process_file(data, chat_type):
    file_service.handle_file_upload(
        data, chat_type, 
        get_data.get_sender_user_id(data), 
        get_data.get_chat_id(data)
    )

def send_to_api_with_obj(chat_id, batch, obj_name=None, obj_adr=None):
    file_service.send_batch_to_api(chat_id, batch, obj_name, obj_adr)

def chat_error_response(data): bot_utils.send_message(get_data.get_chat_id(data), "Только для групп")
def inn_error_response(data): _send_ui(data, ui_templates.get_inn_error_menu)