from core.util import *
from cloud.aws import *


class ServiceController:
    def __init__(self, bundle, app_id):
        self.bundle = bundle
        self.app_id = app_id
        self.common_init()

    def common_init(self):
        #  init object here .. assign boto3 session
        return

    def apply(self, recipe_controller):
        raise NotImplementedError()

    def generate_sdk(self, recipe_controller):
        raise NotImplementedError()


class BillServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self.cost_explorer = CostExplorer(self.boto3_session)

    def apply(self, recipe):
        return

    def generate_sdk(self, recipe):
        return None

    def get_cost(self, start, end):
        response = self.cost_explorer.get_cost(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        total = response.get('Total', {})
        blendedCost = total.get('BlendedCost', {})
        amount = blendedCost.get('Amount', -1)
        unit = blendedCost.get('Unit', None)
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


class AuthServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self._init_table()

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'auth-' + self.app_id
        dynamodb.create_table(table_name)
        #dynamodb.update_table(table_name, )
        return

    def apply(self, recipe_controller):
        self._apply_user_group(recipe_controller)
        self._apply_cloud_api(recipe_controller)
        return

    def _apply_cloud_api(self, recipe_controller):
        role_name = 'auth-' + self.app_id
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)
        role_arn = iam.create_role_and__attach_policies(role_name)

        cloud_apis = recipe_controller.get_cloud_apis()
        for cloud_api in cloud_apis:
            name = cloud_api['name']
            desc = cloud_api['description']
            runtime = 'python3.6'
            handler = 'cloud.lambda_function.handler'
            try:
                lambda_client.create_function(name, desc, runtime, role_arn, handler)
            except:
                print('Function already exists')

    def generate_sdk(self, recipe_controller):
        return


