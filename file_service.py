import json
import threading
from redis_client import redis_conn
import db
import api
import ui_templates
from bot_utils import is_working_hours, send_message, api_send

timer_lock = threading.Lock()
active_timers = {}

def handle_file_upload(data, chat_type, user_id, chat_id):

    is_auth = db.is_chat_authorized(chat_id) if chat_type == 'chat' else db.is_user_authorized(user_id)
    if not is_auth:
        send_message(chat_id, "Сначала зарегистрируйте организацию...")
        return

    body = data.get('message', {}).get('body', {})
    attachments = body.get('attachments', [])
    text = body.get('text', '').strip()
    msg_id = body.get('mid', '0')
    batch_key = f"batch:{user_id}:{chat_id}"


    if not attachments and redis_conn.exists(batch_key):
        _update_batch_data(batch_key, text=text)
        _restart_timer(batch_key, chat_id, user_id)
        return


    files = [{
        "file_id": str(att['payload'].get('fileId')),
        "file_name": str(att.get('filename')),
        "file_url": str(att['payload'].get('url')),
        "message_id": str(msg_id)
    } for att in attachments if att.get('type') == 'file']

    if files:
        _update_batch_data(batch_key, files=files, text=text, msg_id=msg_id)
        _restart_timer(batch_key, chat_id, user_id)

def _update_batch_data(key, files=None, text=None, msg_id='0'):
    raw = redis_conn.get(key)
    try:
        batch = json.loads(raw) if raw else None
    except:
        batch = None

    if not batch:
        batch = {
            "files": [], 
            "comment": "", 
            "has_zayavka": False, 
            "message_id": str(msg_id)
        }
    
    if files:
        batch["files"].extend(files)
        for f in files:
            if f.get("file_name") and "заявка" in f["file_name"].lower():
                batch["has_zayavka"] = True
    
    if text:
        new_text = text.lower()
        if batch["comment"] and new_text not in batch["comment"]:
            batch["comment"] += f" | {new_text}"
        else:
            batch["comment"] = new_text
    
    redis_conn.set(key, json.dumps(batch), ex=120)

def _restart_timer(batch_key, chat_id, user_id):
    with timer_lock:
        if batch_key in active_timers:
            active_timers[batch_key].cancel()
        t = threading.Timer(30.0, finalize_batch, args=[batch_key, chat_id, user_id])
        active_timers[batch_key] = t
        t.start()

def finalize_batch(batch_key, chat_id, user_id):
    with timer_lock:
        active_timers.pop(batch_key, None)
    
    raw = redis_conn.get(batch_key)
    if not raw: return
    try:
        batch = json.loads(raw)
    except:
        return
    
    redis_conn.delete(batch_key)
    
    objects = db.get_construction_objects(chat_id)
    if objects:
        redis_conn.set(f"pending_files:{chat_id}:{user_id}", json.dumps(batch), ex=600)
        api_send(chat_id, ui_templates.get_object_selection_for_file(objects))
    else:
        send_batch_to_api(chat_id, batch)

def send_batch_to_api(chat_id, batch, obj_name=None, obj_adr=None):
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