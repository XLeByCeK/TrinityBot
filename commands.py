import api
import get_data
import db
import ui_templates
from datetime import datetime
import pytz
import holidays
from redis_client import redis_conn
import threading
import json

timer_lock = threading.Lock()
active_timers = {}

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
RU_HOLIDAYS = holidays.Russia()

def is_working_hours():
    now_msk = datetime.now(MOSCOW_TZ)
    if now_msk.weekday() >= 5:
        return False
    if now_msk.date() in RU_HOLIDAYS:
        return False
    if not (9 <= now_msk.hour < 18):
        return False
    return True

def _send(chat_id, body):
    api.api_request("POST", f"/messages?chat_id={chat_id}", json=body)

def send_message(chat_id, text):
    _send(chat_id, {"text": str(text)})

def show_menu_btns(data):
    chat_id = get_data.get_chat_id(data)
    _send(chat_id, ui_templates.get_main_menu())

def begin_work(data):
    chat_type = get_data.get_chat_type(data)
    chat_id = get_data.get_chat_id(data)
    user_id = get_data.get_sender_user_id(data)

    if chat_type == 'chat':
        if db.is_chat_authorized(chat_id):
            _send(chat_id, {"text": "Этот чат уже зарегистрирован за организацией."})
            return
    else:
        if db.is_user_authorized(user_id):
            _send(chat_id, {"text": "Вы уже авторизованы."})
            return

    _send(chat_id, ui_templates.get_begin_work_menu())

def ask_inn(data):
    if check_authorization(data):
        return
    _send(get_data.get_chat_id(data), ui_templates.get_inn_request_text())

def choose_report(data):
    _send(get_data.get_chat_id(data), ui_templates.get_report_menu())

def about_trinity(data):
    _send(get_data.get_chat_id(data), ui_templates.get_about_trinity_menu())

def instructions(data):
    _send(get_data.get_chat_id(data), ui_templates.get_instructions_menu())

def how_it_works(data):
    _send(get_data.get_chat_id(data), ui_templates.get_how_it_works_info())

def about_audit_protocol(data):
    _send(get_data.get_chat_id(data), ui_templates.get_audit_protocol_info())

def about_audit_TKP(data):
    _send(get_data.get_chat_id(data), ui_templates.get_audit_tkp_info())

def consultations(data):
    _send(get_data.get_chat_id(data), ui_templates.get_consultations_menu())

def file_question(data):
    _send(get_data.get_chat_id(data), ui_templates.get_file_question_info())

def trinity_AI_question(data):
    _send(get_data.get_chat_id(data), ui_templates.get_trinity_ai_question_info())

def process_file(data, chat_type):
    user_id = get_data.get_sender_user_id(data)
    chat_id = get_data.get_chat_id(data)

    batch_key = f"batch:{user_id}:{chat_id}"


    if chat_type == 'chat':
        if not db.is_chat_authorized(chat_id):
            send_message(chat_id, "Сначала зарегистрируйте организацию...")
            return 
    else:
        if not db.is_user_authorized(user_id):
            send_message(chat_id, "Сначала зарегистрируйтесь...")
            return 

    body = data.get('message', {}).get('body', {})
    attachments = body.get('attachments', [])
    text = body.get('text', '').strip()
    msg_id = body.get('mid', '0')


    if not attachments and redis_conn.exists(batch_key):
        update_batch_comment(batch_key, text)
        restart_timer(batch_key, chat_id, user_id)
        return

    files_to_add = []
    for att in attachments:
        if att.get('type') == 'file':
            files_to_add.append({
                "file_id": att['payload'].get('fileId'),
                "file_name": att.get('filename'),
                "file_url": att['payload'].get('url'),
                "message_id": str(msg_id)
            })

    if files_to_add:
        save_file_to_batch(batch_key, files_to_add, text, msg_id)
        restart_timer(batch_key, chat_id, user_id)

def restart_timer(batch_key, chat_id, user_id):
    with timer_lock:
        if batch_key in active_timers:
            active_timers[batch_key].cancel()


        t = threading.Timer(30.0, finalize_batch, args=[batch_key, chat_id, user_id])
        active_timers[batch_key] = t
        t.start()


def save_file_to_batch(key, new_files, text, msg_id):
    current_data = redis_conn.get(key)
    if current_data:
        try:
            batch = json.loads(current_data)
        except:
            batch = None
    else:
        batch = None

    if not batch:
        batch = {
            "files": [], 
            "comment": "", 
            "has_zayavka": False, 
            "message_id": str(msg_id)
        }

    batch["files"].extend(new_files)

    for f in new_files:
        if f.get("file_name") and "заявка" in f["file_name"].lower():
            batch["has_zayavka"] = True


    if text:
        new_text = text.lower()
        if batch["comment"] and new_text not in batch["comment"]:
            batch["comment"] += f" | {new_text}"
        else:
            batch["comment"] = new_text
    
    redis_conn.set(key, json.dumps(batch), ex=120)

def update_batch_comment(key, text):

    current_data = redis_conn.get(key)

    if current_data:
        
        try:

            batch = json.loads(current_data)
            new_text = text.lower()

            if batch["comment"] and new_text not in batch["comment"]:
                batch["comment"] += f" | {new_text}"

            else:
                batch["comment"] = new_text

            redis_conn.set(key, json.dumps(batch), ex=120)

        except:
            pass

def obj_mgmt_main(data):

    _send(get_data.get_chat_id(data), ui_templates.get_objects_mgmt_menu())

def obj_add_start(data):

    chat_id = get_data.get_chat_id(data)
    user_id = get_data.get_sender_user_id(data)

    from chatshandler import set_state

    set_state(user_id, "awaiting_obj_name")
    send_message(chat_id, "Укажите наименование объекта")

def obj_delete_list(data):

    chat_id = get_data.get_chat_id(data)
    objs = db.get_construction_objects(chat_id)

    if not objs:

        send_message(chat_id, "Список объектов пуст.")

        return obj_mgmt_main(data)
    
    _send(chat_id, ui_templates.get_objects_delete_list(objs))

def obj_confirm_delete(data, obj_id):

    obj = db.get_construction_object_by_id(obj_id)

    if obj:
        _send(get_data.get_chat_id(data), ui_templates.get_delete_confirmation(obj['name'], obj_id))

def obj_do_delete(data, obj_id):

    obj = db.get_construction_object_by_id(obj_id)

    if obj:
        db.delete_construction_object(obj_id)
        send_message(get_data.get_chat_id(data), f"Удалил объект {obj['name']}")

    obj_mgmt_main(data)

def finalize_batch(batch_key, chat_id, user_id):
    with timer_lock:
        active_timers.pop(batch_key, None)
    
    raw_data = redis_conn.get(batch_key)

    if not raw_data: 
        return
    
    try:
        batch = json.loads(raw_data)
    except:
        return
    
    redis_conn.delete(batch_key)
    objects = db.get_construction_objects(chat_id)

    if objects:
 
        pending_key = f"pending_files:{chat_id}:{user_id}"
        redis_conn.set(pending_key, json.dumps(batch), ex=600)
        

        dummy_data = {'chat_id': chat_id} 
        _send(chat_id, ui_templates.get_object_selection_for_file(objects))
        return

    send_to_api_with_obj(chat_id, batch)

def send_to_api_with_obj(chat_id, batch, obj_name=None, obj_adr=None):

    files = batch.get("files", []) 
    comment_text = batch.get("comment", "").lower()
    has_zayavka = batch.get("has_zayavka", False)
    report_type = db.get_chat_report_type(chat_id)
    inn_value = db.get_inn_by_chat(chat_id)

    payload = {
        "source": "max",
        "chat_id": int(chat_id),
        "files": [
            {
                "file_id": str(f['file_id']),
                "file_name": str(f['file_name']),
                "file_url": str(f['file_url']),
                "message_id": str(f.get('message_id', '0'))
            } for f in files
        ],
        "message_id": str(batch.get("message_id", "0")),
        "topic_id": 0,
        "inn": str(inn_value) if inn_value else "123456789",
        "report_types": [report_type] if report_type else [],
        "object_name": obj_name,
        "object_adr": obj_adr
    }


    final_chat_comment = None

    if "победитель всеинструменты" in comment_text:
        final_chat_comment = "Файлы отправлены на Победитель ВсеИнструменты. Ожидайте результат."
    elif any(word in comment_text for word in ["сводная", "свод", "сформируй сводную"]):
        final_chat_comment = "Сформирую сводную таблицу для списка КП. Ожидайте результат."
    elif len(files) > 1 and has_zayavka:
        final_chat_comment = "Сформирую сводную таблицу для списка КП. Ожидайте результат."

    if final_chat_comment:
        payload["chat_comment"] = final_chat_comment

    print(f"DEBUG: Sending payload to API: {json.dumps(payload, ensure_ascii=False)}")
    success = api.send_to_processing_service(payload)

    if success:

        if not is_working_hours():

            mode = ("Файл принят!\n\nЯ пока обучаюсь выдавать заключения самостоятельно. "
                    "На данном этапе мою работу должен проверить эксперт. Все заявки, "
                    "поступившие до 9.00, проверяются после начала рабочего дня с 9.00 МСК.")
            
        else:

            mode = final_chat_comment if final_chat_comment else "Файлы приняты!\n\nВыдача заключений происходит в течение 10-25 минут."

        send_message(chat_id, mode)
    else: 
        send_message(chat_id, "Произошла ошибка при отправке файлов. Попробуйте позже.")

def success_authorization(data, org_name):
    _send(get_data.get_chat_id(data), ui_templates.get_success_auth_text(org_name))

def check_authorization(data):

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

        _send(chat_id, ui_templates.get_auth_status_msg(msg))
        return True
    
    return False

def chat_error_response(data):
    send_message(get_data.get_chat_id(data), "Эта функция доступна только в групповых чатах")

def inn_error_response(data):
    _send(get_data.get_chat_id(data), ui_templates.get_inn_error_menu())