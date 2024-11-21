def message_response(message, code=None, other_message=None):
    context = {
        'message': message
    }
    if code:
        context.update({'code': code})
    if other_message:
        context.update({'other_message': other_message})
    return context
