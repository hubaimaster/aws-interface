from datetime import date
from core.recipe_controller import BillRecipeController
from core.service_controller import BillServiceController
from .base import API


def get_current_date():
    today = date.today()
    return today


def get_current_month_date():
    today = date.today()
    date_month = date(today.year, today.month, 1)
    return date_month


class BillAPI(API):
    RC_CLASS = BillRecipeController
    SC_CLASS = BillServiceController

    def get_current_cost(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_cost(start, end)

    def get_current_usage_costs(self):
        start = get_current_month_date().isoformat()
        end = get_current_date().isoformat()
        return self.service_controller.get_usage_costs(start, end)
