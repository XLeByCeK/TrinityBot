import api
import get_data

import db

from redis_client import redis_conn

import threading
import json

from ui_creator import (
    message,
    keyboard,
    btn_callback,
    btn_link
)

active_timers = {}

def _send(chat_id, body):
    api.api_request("POST", f"/messages?chat_id={chat_id}", json=body)

def show_menu_btns(data):

    body = message(
        "Привет, меня зовут Trinity."
        "\nВам предоставлены права администратора."
        "\nДобавляйте коллег — они смогут загружать закупочные документы."
        "\nДля дальнейшей работы выберите нужный пункт меню:",

        keyboard(
            [btn_callback("Начать работу", "begin_work")],
            [btn_callback("Получить отчет", "get_report")],
            [btn_callback("О Тринити", "about_trinity")],
            [btn_callback("Инструкции", "instructions")],
            [btn_callback("Консультации", "consultations")],
            [btn_callback("Заключить договор", "sign_contract")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def begin_work(data):

    chat_type = get_data.get_chat_type(data)
    chat_id = get_data.get_chat_id(data)
    user_id = get_data.get_sender_user_id(data)

    if chat_type =='chat':

        if db.is_chat_authorized(chat_id):

            _send(chat_id, message("Этот чат уже зарегистрирован за организацией."))

            return
    else:

        if db.is_user_authorized(user_id):

            _send(chat_id, message("Вы уже авторизованы."))

            return

    body = message(
        "Чтобы продолжить, мне нужно зарегистрировать вашу организацию. Введите ИНН (10 цифр):",
        keyboard(
            [btn_callback("Ввести ИНН", "enter_inn")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(chat_id, body)

def ask_inn(data):
    
    if check_authorization(data):
        return

    body = message("Введите ИНН вашей организации (10 или 12 цифр):")

    _send(get_data.get_chat_id(data), body)

def choose_report(data):

    body = message(
        "Выберите желаемый период отчета:",
        keyboard(
            [btn_callback("За текущую неделю", "report_current_week")],
            [btn_callback("За текущий месяц", "report_current_month")],
            [btn_callback("За прошедшую неделю", "report_last_week")],
            [btn_callback("За прошедший месяц", "report_last_month")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def about_trinity(data):

    body = message(
        "О ТРИНИТИ:",
        keyboard(
            [btn_link("Сайт Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Видео о Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Как работать в Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Презентация Тринити", "https://dev.max.ru/docs-api")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def instructions(data):

    body = message(
        "Инструкции:",

        keyboard(
            [btn_callback("Как это работает", "how_it_works")],
            [btn_callback("Об аудите протокола", "about_audit_protocol")],
            [btn_callback("Об аудите ТКП / счёта", "about_audit_tkp")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def how_it_works(data):

    body = message(
        "1. Вы направляете в чат закупочные файлы.\n"
        "\n2. На основании формы я выдам заключение о согласовании или несогласовании сделки.\n"
        "\n3. Закупки с отрицательным заключением можно отправить экспертам.\n"
        "\nЧерез 1–3 рабочих дня мы предоставим альтернативных поставщиков с экономией 5%–25%.",
        keyboard([btn_callback("Назад", "back_to_instructions")])
    )

    _send(get_data.get_chat_id(data), body)

def about_audit_protocol(data):

    body = message(
        "Чтобы отправить на аудит тендерный протокол, убедитесь, что он содержит:\n"
        "1. ИНН участников\n"
        "2. Номенклатуру товара\n"
        "3. Единицы измерения\n"
        "4. Количество\n"
        "5. Цены (с/без НДС)\n"
        "6. Адрес доставки\n"
        "7. Победителя протокола\n\n"
        "*Возможно потребуется время, чтобы я обучился вашей форме протокола.",
        keyboard([btn_callback("Назад", "back_to_instructions")])
    )

    _send(get_data.get_chat_id(data), body)

def about_audit_TKP(data):

    body = message(
        "Чтобы отправить на аудит ТКП / счёт, убедитесь, что файл содержит:\n"
        "1. ИНН поставщика\n"
        "2. Номенклатуру товара\n"
        "3. Единицы измерения\n"
        "4. Количество\n"
        "5. Цены (с/без НДС)\n"
        "6. Адрес доставки\n\n"
        "Формат файлов — любой (pdf, jpeg, excel), можно загружать несколько.",
        keyboard([btn_callback("Назад", "back_to_instructions")])
    )

    _send(get_data.get_chat_id(data), body)

def consultations(data):

    body = message(
        "Какой у вас вопрос?",
        keyboard(
            [btn_callback("Вопрос по выданным файлам", "file_question")],
            [btn_callback("Вопрос по работе ТРИНИТИ AI", "trinity_ai_question")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def file_question(data):

    body = message(
        "Задавайте вопросы прямо в чате — куратор ответит при первой возможности.",
        keyboard([btn_callback("Назад", "back_to_consultations")])
    )

    _send(get_data.get_chat_id(data), body)

def trinity_AI_question(data):

    body = message(
        "Задавайте вопросы по работе нейросети — куратор ответит при первой возможности.",
        keyboard([btn_callback("Назад", "back_to_consultations")])
    )

    _send(get_data.get_chat_id(data), body)

def process_file(data, chat_type):

    user_id = get_data.get_sender_user_id(data)
    chat_id = get_data.get_chat_id(data)
    batch_key = f"batch:{user_id}:{chat_id}"
    
    if chat_type == 'chat':

        if not db.is_chat_authorized(chat_id):

            send_message(chat_id, "Сначала зарегистрируйте организацию в чате, введя ИНН.")

            return 
    else:

        if not db.is_user_authorized(user_id):

            send_message(chat_id, "Сначала зарегистрируйтесь, введя ИНН.")

            return 

    body = data.get('message', {}).get('body', {})
    attachments = body.get('attachments', [])
    text = body.get('text', '').strip()

    msg_id = body.get('mid', '0')


    if not attachments and redis_conn.exists(batch_key):

        update_batch_comment(batch_key, text)
        restart_timer(batch_key, data)

        return


    files_to_add = []

    for att in attachments:

        if att.get('type') == 'file':

            files_to_add.append({
                "file_id": att['payload'].get('fileId'),
                "file_name": att.get('filename'),
                "file_url": att['payload'].get('url'),
                "message_id": str(msg_id) # сохраняем как строку
            })
    
    if files_to_add:

        save_file_to_batch(batch_key, files_to_add, text, msg_id)
        restart_timer(batch_key, data)

def restart_timer(batch_key, data):

    if batch_key in active_timers:

        active_timers[batch_key].cancel()
    
    t = threading.Timer(30.0, finalize_batch, args=[batch_key, data])
    active_timers[batch_key] = t

    t.start()

def save_file_to_batch(key, new_files, text, msg_id):
    current_data = redis_conn.get(key)

    if current_data:

        batch = json.loads(current_data)
    else:

        batch = {
            "files": [], 
            "comment": "", 
            "has_zayavka": False, 
            "message_id": str(msg_id)
        }

    batch["files"].extend(new_files)
    

    for f in new_files:

        if "заявка" in f["file_name"].lower():

            batch["has_zayavka"] = True
    

    if text:

        batch["comment"] = text.lower()

    redis_conn.set(key, json.dumps(batch), ex=120)

def update_batch_comment(key, text):

    current_data = redis_conn.get(key)

    if current_data:

        batch = json.loads(current_data)
        batch["comment"] = text.lower()

        redis_conn.set(key, json.dumps(batch), ex=120)

def finalize_batch(batch_key, original_data):
    raw_data = redis_conn.get(batch_key)

    if not raw_data:

        return
    
    batch = json.loads(raw_data)
    user_id = get_data.get_sender_user_id(original_data)
    chat_id = get_data.get_chat_id(original_data)

    inn_value = db.get_inn_by_chat(chat_id)

    if not inn_value:
        inn_value = db.get_user_inn(user_id)

    files = batch.get("files", [])
    comment_text = batch.get("comment", "").lower()
    has_zayavka = batch.get("has_zayavka", False)
    

    final_chat_comment = None
    

    if "победитель всеинструменты" in comment_text:
        final_chat_comment = "Победитель ВсеИнструменты"

    elif any(word in comment_text for word in ["сводная", "свод", "сформируй сводную"]):
        final_chat_comment = "Сформирую сводную таблицу для списка КП. Ожидайте результат."

    elif len(files) > 1 and has_zayavka:
        final_chat_comment = "Сформирую сводную таблицу для списка КП. Ожидайте результат."


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
        "message_id": str(batch.get("message_id", "0")), # mid из первого сообщения
        "topic_id": 0,
        "inn": str(inn_value) if inn_value else "123456789",
        "report_types": [4]
    }

    if final_chat_comment:
        payload["chat_comment"] = final_chat_comment

    success = api.send_to_processing_service(payload)

    if success:
        mode = final_chat_comment if final_chat_comment else "Файлы приняты!\n\nВыдача заключений происходит в течение 10-25 минут, последовательно, в зависимости от количества файлов."
        send_message(chat_id, mode)
    

    redis_conn.delete(batch_key)
    active_timers.pop(batch_key, None)

def success_authorization(data, org_name):

    api.api_request('POST', 
                    f'/messages?chat_id={get_data.get_chat_id(data)}', 
                    json={"text": f"Отлично! Ваша организация {org_name}.\n"  
                                    "Теперь ценообразование Ваших закупок будет под надёжной защитой искусственного интеллекта.\n" 
                                    "Пожалуйста, выкладывайте файлы Ваших тендерных протоколов."})

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
        
        body = message(
            msg,
            keyboard(
                [btn_callback("Назад", "back_to_main")]
            )
        )

        _send(get_data.get_chat_id(data), body)
        return True
    
    return False


def chat_error_response(data):

    _send(get_data.get_chat_id(data), {"text": "Эта функция доступна только в групповых чатах"})

def inn_error_response(data):

    body = message(
        "Похоже, что ИНН неверный.\n" 
        "Пожалуйста, проверьте правильность вводимых данных и попробуйте еще раз.",
        keyboard(
            [btn_callback("Ввести ИНН еще раз", "enter_inn")],
            [btn_callback("Вернуться в главное меню", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

def send_message(chat_id, text):

    _send(chat_id, {"text": f"{text}"})