from cloud.aws import *
import importlib
import shutil
import json
import boto3
import uuid
import os


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session


def create_lambda_zipfile_bin(app_id, recipe, dir_name, root_name='cloud'):
    output_filename = str(uuid.uuid4())
    # Make tmp_dir
    tmp_dir = str(uuid.uuid4())
    if os.path.isdir(tmp_dir):
        os.remove(tmp_dir)
    os.mkdir(tmp_dir)

    # Copy temp dir into root_name folder
    shutil.copytree(dir_name, '{}/{}'.format(tmp_dir, root_name))

    # Copy recipe from recipe_controller
    with open('{}/{}/{}'.format(tmp_dir, root_name, 'recipe.json'), 'w+') as file:
        file.write(recipe)

    # Write txt file included app_id
    with open('{}/{}/{}'.format(tmp_dir, root_name, 'app_id.txt'), 'w+') as file:
        file.write(app_id)

    # Archive all files
    shutil.make_archive(output_filename, 'zip', tmp_dir)
    zip_file_name = '{}.zip'.format(output_filename)
    zip_file = open(zip_file_name, 'rb')
    zip_file_bin = zip_file.read()
    zip_file.close()

    # Remove temp files
    os.remove(zip_file_name)
    shutil.rmtree(tmp_dir)
    return zip_file_bin


def make_data(app_id, parmas, recipe_json, admin=True):
    recipe = json.loads(recipe_json)
    data = {
        'params': parmas,
        'recipe': recipe,
        'app_id': app_id,
        'admin': admin,
    }
    return data


class ServiceController:
    def __init__(self, bundle, app_id):
        self.bundle = bundle
        self.app_id = app_id
        self.common_init()

    def common_init(self):
        #  init object here .. assign boto3 session
        return

    def apply_cloud_api(self, recipe_controller):
        recipe_type = recipe_controller.get_recipe_type()
        role_name = '{}-{}'.format(recipe_type, self.app_id)
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)
        role_arn = iam.create_role_and_attach_policies(role_name)

        name = '{}-{}'.format(recipe_type, self.app_id)
        desc = 'aws-interface cloud API'
        runtime = 'python3.6'
        handler = 'cloud.lambda_function.handler'

        module_name = 'cloud'
        module = importlib.import_module(module_name)
        module_path = os.path.dirname(module.__file__)

        recipe = recipe_controller.to_json()
        zip_file = create_lambda_zipfile_bin(self.app_id, recipe, module_path)

        try:
            lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file)
        except:
            print('Function might already exist, Try updating function code.')
            try:
                lambda_client.update_function_code(name, zip_file)
            except:
                print('Update function failed')

    def deploy_cloud_api(self, recipe_controller):
        recipe_type = recipe_controller.get_recipe_type()
        api_name = '{}-{}'.format(recipe_type, self.app_id)
        func_name = '{}-{}'.format(recipe_type, self.app_id)
        api_gateway = APIGateway(self.boto3_session)
        api_gateway.connect_with_lambda(api_name, func_name)

    def get_rest_api_url(self, recipe_controller):
        api_client = APIGateway(self.boto3_session)
        recipe_type = recipe_controller.get_recipe_type()
        api_name = '{}-{}'.format(recipe_type, self.app_id)
        func_name = '{}-{}'.format(recipe_type, self.app_id)
        api_url = api_client.get_rest_api_url(api_name, func_name)
        return api_url

    def get_rest_api_sdk(self, recipe_controller):
        api_url = self.get_rest_api_url(recipe_controller)
        raise NotImplementedError()

    def apply(self, recipe_controller):
        raise NotImplementedError()




class BillServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self.cost_explorer = CostExplorer(self.boto3_session)

    def apply(self, recipe):
        return

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
        dynamodb.init_table(table_name)
        dynamodb.update_table(table_name, indexes=[{
            'hash_key': 'partition',
            'hash_key_type': 'S',
            'sort_key': 'email',
            'sort_key_type': 'S',
        }])
        return

    def apply(self, recipe_controller):
        self.apply_cloud_api(recipe_controller)
        self.deploy_cloud_api(recipe_controller)

    def create_user(self, recipe, email, password, extra):
        import cloud.auth.register as register
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return register.do(data, boto3)

    def set_user(self, recipe, user_id, email, password, extra):
        import cloud.auth.set_user as set_user
        parmas = {
            'user_id': user_id,
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return set_user.do(data, boto3)

    def delete_user(self, recipe, user_id):
        import cloud.auth.delete_user as delete_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return delete_user.do(data, boto3)

    def get_user(self, recipe, user_id):
        import cloud.auth.get_user as get_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user.do(data, boto3)

    def get_user_count(self, recipe):
        import cloud.auth.get_user_count as get_user_count
        parmas = {

        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user_count.do(data, boto3)

    def get_users(self, recipe, start_key, limit):
        import cloud.auth.get_users as get_users
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_users.do(data, boto3)

    def create_session(self, recipe, email, password):
        import cloud.auth.login as login
        params = {
            'email': email,
            'password': password
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return login.do(data, boto3)

    def delete_session(self, recipe, session_id):
        import cloud.auth.logout as logout
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return logout.do(data, boto3)

    def get_session(self, recipe, session_id):
        import cloud.auth.get_session as get_session
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_session.do(data, boto3)

    def get_sessions(self, recipe, start_key, limit):
        import cloud.auth.get_sessions as get_sessions
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_sessions.do(data, boto3)

    def get_session_count(self, recipe):
        import cloud.auth.get_session_count as get_session_count
        parmas = {}
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_session_count.do(data, boto3)