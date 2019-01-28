from django import template
import datetime
register = template.Library()


def to_date(time_value):
    try:
        ts = int(time_value)
    except ValueError:
        return time_value
    return datetime.datetime.fromtimestamp(ts)


register.filter(to_date)