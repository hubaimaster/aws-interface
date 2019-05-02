from datetime import date
from core.service_controller import BillServiceController
from .base import API


def get_current_date():
    today = date.today()
    return today


def get_prev_month_date():
    today = date.today()
    if today.day == 1:
        if today.month == 1:
            date_month = date(today.year - 1, 12, 1)
        else:
            date_month = date(today.year, today.month - 1, 1)
    else:
        date_month = date(today.year, today.month, 1)
    return date_month


class BillAPI(API):
    SC_CLASS = BillServiceController

    def get_current_cost(self):
        start = get_prev_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_cost(start, end)

    def get_current_usage_costs(self):
        start = get_prev_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_usage_costs(start, end)
