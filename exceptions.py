class NoSendMessageEx(Exception):
    """Cообщение не отправлено."""
    pass 

class InvalidHttpCodeEx(Exception):
    """Статус HTTP-кода равен не 200."""
    pass

class InvalidRequestEx(Exception):
    """Ошибка получения request."""
    pass

class UnknownStatusEx(Exception):
    """Hеизвестный статус домашней работы."""
    pass 
