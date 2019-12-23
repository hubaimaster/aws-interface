from datetime import date
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
    def get_cost(self):
        start = get_prev_month_date().isoformat()
        end = get_current_date().isoformat()

        response = self.resource.cost_for(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        total = response.get('Total', {})
        blended_cost = total.get('BlendedCost', {})
        amount = blended_cost.get('Amount', -1)
        unit = blended_cost.get('Unit', None)
        result = {'Amount': amount, 'Unit': unit}
        return result

    def get_usage_costs(self):
        start = get_prev_month_date().isoformat()
        end = get_current_date().isoformat()

        response = self.resource.cost_and_usage_for(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        groups = response.get('Groups', [])
        groups = [{
            'Service': x.get('Keys', [None])[0],
            'Cost': x.get('Metrics', {}).get('AmortizedCost', {})
        } for x in groups]
        groups.sort(key=lambda x: x['Cost']['Amount'], reverse=True)
        return groups
