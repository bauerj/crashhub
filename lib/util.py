import datetime


def get_greeting():
    now = datetime.datetime.now()
    if now.hour < 12:
        return "Good morning"
    if now.hour < 17:
        return "Good afternoon"
    return "Good evening"
