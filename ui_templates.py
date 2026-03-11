from ui_creator import (
    message,
    keyboard,
    btn_callback,
    btn_link
)

def get_main_menu():
    return message(
        "Привет, меня зовут Trinity.\n"
        "Вам предоставлены права администратора.\n"
        "Добавляйте коллег — они смогут загружать закупочные документы.\n"
        "Для дальнейшей работы выберите нужный пункт меню:",
        keyboard(
            [btn_callback("Начать работу", "begin_work")],
            [btn_callback("Объекты строительства", "obj_mgmt_main")],
            [btn_callback("Получить отчет", "get_report")],
            [btn_callback("О Тринити", "about_trinity")],
            [btn_callback("Инструкции", "instructions")],
            [btn_callback("Консультации", "consultations")],
            [btn_callback("Заключить договор", "sign_contract")]
        )
    )

def get_begin_work_menu():
    return message(
        "Чтобы продолжить, мне нужно зарегистрировать вашу организацию. Введите ИНН (10 цифр):",
        keyboard(
            [btn_callback("Ввести ИНН", "enter_inn")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_inn_request_text():
    return message("Введите ИНН вашей организации (10 или 12 цифр):")

def get_report_menu():
    return message(
        "Выберите желаемый период отчета:",
        keyboard(
            [btn_callback("За текущую неделю", "report_current_week")],
            [btn_callback("За текущий месяц", "report_current_month")],
            [btn_callback("За прошедшую неделю", "report_last_week")],
            [btn_callback("За прошедший месяц", "report_last_month")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_about_trinity_menu():
    return message(
        "О ТРИНИТИ:",
        keyboard(
            [btn_link("Сайт Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Видео о Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Как работать в Тринити", "https://dev.max.ru/docs-api")],
            [btn_link("Презентация Тринити", "https://dev.max.ru/docs-api")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_instructions_menu():
    return message(
        "Инструкции:",
        keyboard(
            [btn_callback("Как это работает", "how_it_works")],
            [btn_callback("Об аудите протокола", "about_audit_protocol")],
            [btn_callback("Об аудите ТКП / счёта", "about_audit_tkp")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_how_it_works_info():
    return message(
        "1. Вы направляете в чат закупочные файлы.\n"
        "\n2. На основании формы я выдам заключение о согласовании или несогласовании сделки.\n"
        "\n3. Закупки с отрицательным заключением можно отправить экспертам.\n"
        "\nЧерез 1–3 рабочих дня мы предоставим альтернативных поставщиков с экономией 5%–25%.",
        keyboard([btn_callback("Назад", "back_to_instructions")])
    )

def get_audit_protocol_info():
    return message(
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

def get_audit_tkp_info():
    return message(
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

def get_consultations_menu():
    return message(
        "Какой у вас вопрос?",
        keyboard(
            [btn_callback("Вопрос по выданным файлам", "file_question")],
            [btn_callback("Вопрос по работе ТРИНИТИ AI", "trinity_ai_question")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_file_question_info():
    return message(
        "Задавайте вопросы прямо в чате — куратор ответит при первой возможности.",
        keyboard([btn_callback("Назад", "back_to_consultations")])
    )

def get_trinity_ai_question_info():
    return message(
        "Задавайте вопросы по работе нейросети — куратор ответит при первой возможности.",
        keyboard([btn_callback("Назад", "back_to_consultations")])
    )

def get_auth_status_msg(text):
    return message(
        text,
        keyboard([btn_callback("Назад", "back_to_main")])
    )

def get_inn_error_menu():
    return message(
        "Похоже, что ИНН неверный.\n"
        "Пожалуйста, проверьте правильность вводимых данных и попробуйте еще раз.",
        keyboard(
            [btn_callback("Ввести ИНН еще раз", "enter_inn")],
            [btn_callback("Вернуться в главное меню", "back_to_main")]
        )
    )

def get_success_auth_text(org_name):
    return {
        "text": f"Отлично! Ваша организация {org_name}.\n"
                "Теперь ценообразование Ваших закупок будет под надёжной защитой искусственного интеллекта.\n"
                "Пожалуйста, выкладывайте файлы Ваших тендерных протоколов."
    }

def get_objects_mgmt_menu():
    return message(
        "Управление объектами строительства:",
        keyboard(
            [btn_callback("Добавить объект", "obj_add_start")],
            [btn_callback("Удалить объект", "obj_delete_list")],
            [btn_callback("Назад", "back_to_main")]
        )
    )

def get_objects_delete_list(objects):
    buttons = []
    for obj in objects:
        buttons.append([btn_callback(obj['name'], f"obj_confirm_del_{obj['object_id']}")])
    buttons.append([btn_callback("Назад", "obj_mgmt_main")])
    return message("Выберите объект для удаления:", keyboard(*buttons))

def get_delete_confirmation(obj_name, obj_id):
    return message(
        f"Удалить объект {obj_name}?",
        keyboard(
            [btn_callback("Да", f"obj_do_delete_{obj_id}"), btn_callback("Нет", "obj_delete_list")]
        )
    )

def get_object_selection_for_file(objects):
    buttons = []
    for obj in objects:
        buttons.append([btn_callback(obj['name'], f"file_target_obj_{obj['object_id']}")])
    buttons.append([btn_callback("Без объекта", "file_skip_obj")])
    return message("Укажите объект строительства:", keyboard(*buttons))