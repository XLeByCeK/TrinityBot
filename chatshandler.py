import commands

CALLBACK_HANDLERS = {

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

def handle_callback(data):

    callback = data.get('callback', {})

    payload = callback.get('payload', {})

    if payload in CALLBACK_HANDLERS:

        CALLBACK_HANDLERS[payload](data)

def private_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created':

        if attachment_type == 'image':

            commands.chat_error_response(data)

        elif msg_text == 'Отправь файл':

            commands.send_message_with_file(data)

        elif msg_text == 'Закрепи сообщение':

            commands.chat_error_response(data)
            
        else:
            
            commands.showMenuBtns(data)
    
    elif update_type == 'message_callback':
        handle_callback(data)

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
        