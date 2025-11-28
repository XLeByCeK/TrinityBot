import commands

def private_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created' and attachment_type == 'image':
        
        commands.chat_error_response(data)

    if update_type == 'message_created' and msg_text == 'Отправь файл':
        
        commands.send_message_with_file(data)

    if update_type == 'message_created' and msg_text == 'Закрепи сообщение':

        commands.chat_error_response(data)

    if update_type == 'message_created' and msg_text != 'Отправь файл' and msg_text != 'Закрепи сообщение' and attachment_type != 'image':

        commands.showMenuBtns(data)

    if update_type == 'message_callback':
        
        callback = data.get('callback', {})
        payload = callback.get('payload', {})

        if payload == 'begin_work':
            
            commands.showMenu(data)

        if payload == 'menu_1':
            
            commands.responseMenu1(data)

        if payload == 'menu_2':
            
            commands.responseMenu2(data)

        if payload == 'get_report':
            
            commands.chooseReport(data)

        if payload == 'about_trinity':
            
            commands.aboutTrinity(data)

        if payload == 'instructions':
            
            commands.instructions(data)

        if payload == 'how_it_works':
            
            commands.howItWorks(data)

        if payload == 'about_audit_protocol':
            
            commands.aboutAuditProtocol(data)

        if payload == 'about_audit_tkp':
            
            commands.aboutAuditTKP(data)

        if payload == 'consultations':
            
            commands.consultations(data)

        if payload == 'file_question':
            
            commands.fileQuestion(data)

        if payload == 'trinity_ai_question':
            
            commands.trinityAiQuestion(data)

def group_chats(data, update_type, msg_text, attachment_type):

    if update_type == 'message_created' and attachment_type == 'image':
        
        commands.update_img(data)

    if update_type == 'message_created' and msg_text == 'Отправь файл':
        
        commands.send_message_with_file(data)

    if update_type == 'message_created' and msg_text == 'Закрепи сообщение':

        commands.pin_message(data)

    if update_type == 'message_created' and msg_text != 'Отправь файл' and msg_text != 'Закрепи сообщение' and attachment_type != 'image':

        commands.showMenuBtns(data)

    if update_type == 'message_callback':
        
        callback = data.get('callback', {})
        payload = callback.get('payload', {})

        if payload == 'begin_work':
            
            commands.showMenu(data)

        if payload == 'menu_1':
            
            commands.responseMenu1(data)

        if payload == 'menu_2':
            
            commands.responseMenu2(data)

        if payload == 'get_report':
            
            commands.chooseReport(data)

        if payload == 'about_trinity':
            
            commands.aboutTrinity(data)

        if payload == 'instructions':
            
            commands.instructions(data)

        if payload == 'how_it_works':
            
            commands.howItWorks(data)

        if payload == 'about_audit_protocol':
            
            commands.aboutAuditProtocol(data)

        if payload == 'about_audit_tkp':
            
            commands.aboutAuditTKP(data)

        if payload == 'consultations':
            
            commands.consultations(data)

        if payload == 'file_question':
            
            commands.fileQuestion(data)

        if payload == 'trinity_ai_question':
            
            commands.trinityAiQuestion(data)

        