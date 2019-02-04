from datetime import date


def get_current_date():
    today = date.today()
    return today


def get_current_month_date():
    today = date.today()
    datem = date(today.year, today.month, 1)
    return datem
