import api
import get_data

import db

from ui_creator import (
    message,
    keyboard,
    btn_callback,
    btn_link
)


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

    if check_authorization(data):
        return

    body = message(
        "Чтобы продолжить, мне нужно зарегистрировать вашу организацию. Введите ИНН (10 цифр):",
        keyboard(
            [btn_callback("Ввести ИНН", "enter_inn")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

    _send(get_data.get_chat_id(data), body)

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

def process_file(data):

    authorized= db.is_user_authorized(get_data.get_sender_user_id(data))

    if authorized:
       
        body = message(
            "Спасибо.\n" \
            "Файлы приняты.\n\n" \
            "Выдача заключения (ий) происходит в течение 10-25 минут, последовательно, в зависимости от количества файлов."  
        )

        _send(get_data.get_chat_id(data), body)

        return

    body = message(
        "Ваша организация не прошла регистрацию.",
    )

    _send(get_data.get_chat_id(data), body)

def success_authorization(data, org_name):

    api.api_request('POST', 
                    f'/messages?chat_id={get_data.get_chat_id(data)}', 
                    json={"text": f"Отлично! Ваша организация {org_name}.\n"  
                                    "Теперь ценообразование Ваших закупок будет под надёжной защитой искусственного интеллекта.\n" 
                                    "Пожалуйста, выкладывайте файлы Ваших тендерных протоколов."})

def check_authorization(data):

    authorized= db.is_user_authorized(get_data.get_recipient_user_id(data))

    if authorized:
       
        body = message(
            f"Вы уже авторизованы.",
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

