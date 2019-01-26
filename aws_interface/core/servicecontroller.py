from core.util import *
from cloud.aws import *
import importlib
import os


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
        dynamodb.update_table(table_name, indexes=[{
            'hash_key': 'partition',
            'hash_key_type': 'S',
            'sort_key': 'creationDate',
            'sort_key_type': 'N'
        }])
        return

    def apply(self, recipe_controller):
        self._apply_cloud_api(recipe_controller)
        return

    def _apply_cloud_api(self, recipe_controller):
        role_name = 'auth-{}'.format(self.app_id)
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)
        role_arn = iam.create_role_and_attach_policies(role_name)

        name = 'auth-{}'.format(self.app_id)
        desc = 'aws-interface cloud api'
        runtime = 'python3.6'
        handler = 'cloud.lambda_function.handler'

        module_name = 'cloud'
        module = importlib.import_module(module_name)
        module_path = os.path.dirname(module.__file__)
        zip_file = create_zipfile_bin(module_path)

        try:
            lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file)
        except:
            print('Function might already exist, Try updating function code.')
            lambda_client.update_function_code(name, zip_file)


    def generate_sdk(self, recipe_controller):
        return

    def create_user(self, recipe, email, password, extra):
        import cloud.auth.register as register
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = {
            'params': parmas,
            'recipe': recipe,
        }
        return register.do(data)

    def set_user(self, recipe, user_id, email, password, extra):
        import cloud.auth.set_user as set_user
        parmas = {
            'user_id': user_id,
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = {
            'params': parmas,
            'recipe': recipe,
        }
        return set_user.do(data)

    def delete_user(self, recipe, user_id):
        import cloud.auth.delete_user as delete_user
        parmas = {
            'user_id': user_id,
        }
        data = {
            'params': parmas,
            'recipe': recipe,
            'admin': True
        }
        return delete_user.do(data)

    def get_user(self, recipe, user_id):
        import cloud.auth.get_user as get_user
        parmas = {
            'user_id': user_id,
        }
        data = {
            'params': parmas,
            'recipe': recipe,
            'admin': True
        }
        return get_user.do(data)

    def get_user_count(self, recipe):
        import cloud.auth.get_user_count as get_user_count
        parmas = {}
        data = {
            'params': parmas,
            'recipe': recipe,
            'admin': True
        }
        return get_user_count(data)