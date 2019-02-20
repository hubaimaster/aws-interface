from .base import ServiceController
from .utils import lambda_method, make_data
from cloud.aws import *


class BillServiceController(ServiceController):
    RECIPE = 'bill'

    def __init__(self, bundle, app_id):
        super(BillServiceController, self).__init__(bundle, app_id)
        self.cost_explorer = CostExplorer(self.boto3_session)

    def get_cost(self, start, end):
        response = self.cost_explorer.get_cost(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        total = response.get('Total', {})
        blended_cost = total.get('BlendedCost', {})
        amount = blended_cost.get('Amount', -1)
        unit = blended_cost.get('Unit', None)
        result = {'Amount': amount, 'Unit': unit}
        return result

    def get_usage_costs(self, start, end):
        response = self.cost_explorer.get_cost_and_usage(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        groups = response.get('Groups', [])
        groups = [{
            'Service': x.get('Keys', [None])[0],
            'Cost': x.get('Metrics', {}).get('AmortizedCost', {})
        } for x in groups]
        groups.sort(key=lambda x: x['Cost']['Amount'], reverse=True)
        return groups

