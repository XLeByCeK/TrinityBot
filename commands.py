import api
import getData

def showMenuBtns(data):

    body = {
            "text": "Привет, меня зовут Trinity."
            "Вам предоставлены права администратора. "
            "Пожалуйста, добавляйте коллег в этот чат, если потребуется, чтобы другие участники могли загружать закупочные документы для аудита."
            "Для дальнейшей работы выберите нужный пункт меню:",
            "attachments": [
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [
                            [
                                {
                                    "type": "callback",
                                    "text": "Начать работу",
                                    "payload": "begin_work"  
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "Получить отчет",
                                    "payload": "get_report"  
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "О тринити",
                                    "payload": "about_trinity"  
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "Инструкции",
                                    "payload": "instructions"  
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "Консультации",
                                    "payload": "consultations"  
                                }
                            ],
                            [
                                {
                                    "type": "callback",
                                    "text": "Заключить договор",
                                    "payload": "sign_contract"  
                                }
                            ]
                        ]
                    }
                }
            ]
        }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def showMenu(data):

    body = {
                "text": "Выберите пункт или напишите: "
                "'Отправь файл' для отправки файла. "
                "'Закрепи сообщение' для того чтобы закрепить сообщение. "
                "Отправь картинку чтобы изменить аватарку чата.",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "callback",
                                        "text": "Пункт 1",
                                        "payload": 'menu_1'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Пункт 2",
                                        "payload": "menu_2"
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def responseMenu1(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы нажали Пункт 1"})

def responseMenu2(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы нажали Пункт 2"})

def chooseReport(data):

    body = {
                "text": "Выберете желаемый период отчета: ",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "callback",
                                        "text": "За текущую неделю",
                                        "payload": 'report_current_week'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "За текущий месяц",
                                        "payload": "report_current_month"
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "За прошедшую неделю",
                                        "payload": 'report_last_week'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "За прошедший месяц",
                                        "payload": 'report_last_month'
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def aboutTrinity(data):

    body = {
                "text": "О ТРИНИТИ ",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "link",
                                        "text": "Сайт Тринити",
                                        "url": 'https://dev.max.ru/docs-api'
                                    }
                                ],
                                [
                                    {
                                        "type": "link",
                                        "text": "Видео о ТРИНИТИ",
                                        "url": "https://dev.max.ru/docs-api"
                                    }
                                ],
                                [
                                    {
                                        "type": "link",
                                        "text": "Как работать в тринити",
                                        "url": 'https://dev.max.ru/docs-api'
                                    }
                                ],
                                [
                                    {
                                        "type": "link",
                                        "text": "Презентация ТРИНИТИ",
                                        "url": 'https://dev.max.ru/docs-api'
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def instructions(data):

    body = {
                "text": "Инструкции ",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "callback",
                                        "text": "Как это работает",
                                        "payload": 'how_it_works'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Об аудите протокола",
                                        "payload": "about_audit_protocol"
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Об аудите ТКП / Счета",
                                        "payload": 'about_audit_tkp'
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def howItWorks(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": ""
    "1. Вы направляете в чат закупочные файлы в удобном формате."
    "2. На основании загруженной формы я выдам заключение о согласовании или несогласовании сделки, которое будет направлено в этот чат."
    "3. Все закупки с отрицательным заключением Вы можете отдать на проработку нашим экспертам."
    "Через 1 -3 рабочих дня, мы предоставим альтернативных поставщиков с экономией 5% -25%"})

def aboutAuditProtocol(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Для того, чтобы отправить на аудит тендерный протокол*, убедитесь, пожалуйста, что он содержит следующую информацию:"
    "1. ИНН участников;"
    "2. Номенклатура товара;"
    "3. Единицы измерения;"
    "4. Количество по каждой позиции;"
    "5. Цена по каждой позиции (с указанием с НДС или без НДС); "
    "6. Адрес доставки; "
    "7. Победитель протокола."
    "*Мне может понадобиться некоторое время, чтобы научиться распознавать Вашу форму тендерного протокола."})

def aboutAuditTKP(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Для того, чтобы отправить на аудит ТКП / счёт, убедитесь, пожалуйста, что файл содержит следующую информацию:"
    "1. ИНН поставщика;"
    "2. Номенклатура товара;"
    "3. Единицы измерения;"
    "4. Количество по каждой позиции;"
    "5. Цена по каждой позиции (с указанием с НДС или без НДС);"
    "6. Адрес доставки."
    "Формат загружаемых файлов- любой (pdf, jpeg, excel). Можно загрузить сразу несколько файлов."})

def consultations(data):

    body = {
                "text": "Выберете желаемый период отчета: ",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [
                                    {
                                        "type": "callback",
                                        "text": "Вопрос по выданным файлам",
                                        "payload": 'file_question'
                                    }
                                ],
                                [
                                    {
                                        "type": "callback",
                                        "text": "Вопросы по работе нейросети ТРИНИТИ",
                                        "payload": "trinity_ai_question"
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
    
    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json=body)

def fileQuestion(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы можете задавать Ваши вопросы прямо в чате, куратор проекта ответ на них по первой возможности. "})

def trinityAiQuestion(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Вы можете задавать Ваши вопросы прямо в чате, куратор проекта ответ на них по первой возможности. " })

def send_message_with_file(data):

    file_path = r'D:\Trinity\TrinityBot\TrinityBot\example.txt'
    filename = "example.txt"

    file_token = getData.getFileToken(file_path, filename)

    message_id = getData.getMessageId(data)

    body = {
        "text": "Сообщение с файлом и цитированием",
        "attachments": [
            {
                "type": "file",
                "payload": {
                    "token": file_token
                }
            }
        ],
        "link": {
            "type": 'reply',
            "mid": message_id
        }
    }
        
    api.api_request(
            'POST',
            f"/messages?chat_id={getData.getChatId(data)}",
            json=body
        )
    
def pin_message(data):

    message_id = getData.getMessageId(data)

    body = {
        "message_id": message_id
    }

    api.api_request('PUT', f'/chats/{getData.getChatId(data)}/pin', json=body)

def chat_error_response(data):

    api.api_request('POST', f'/messages?chat_id={getData.getChatId(data)}', json={"text": "Эта функция доступна только  в групповых чатах"})

def update_img(data):

    url = data['message']['body']['attachments'][0]['payload']['url']

    body = {
        'icon': { "url": url }
    }

    api.api_request('PATCH', f'/chats/{getData.getChatId(data)}', json=body)