from cloud.aws import *
import importlib
import shutil
import json
import boto3
import os
import tempfile
from abc import ABCMeta, abstractmethod


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    region_name = bundle.get('region_name', 'ap-northeast-2')  # TODO
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
    )
    return session


def create_lambda_zipfile_bin(app_id, recipe, dir_name, root_name='cloud'):
    output_filename = tempfile.mktemp()
    # Make tmp_dir
    tmp_dir = tempfile.mkdtemp()

    # Copy lambda dir into temp/root_name folder
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


def create_sdk_zipfile_bin(recipe_controller, rest_api_url):
    packages = [
        'core.sdk.java',
        'core.sdk.javascript',
        'core.sdk.python3',
        'core.sdk.swift'
    ]
    output_filename = tempfile.mktemp()

    # Make tmp_dir
    tmp_dir = tempfile.mkdtemp()

    for package in packages:
        sdk_name = package.split('.')[-1]
        module = importlib.import_module(package)
        module_path = os.path.dirname(module.__file__)

        # Copy module_path into temp/sdk_name folder
        shutil.copytree(module_path, os.path.join(tmp_dir, sdk_name))

        # Remove __init__.py and __pycache__
        try:
            os.remove(os.path.join(tmp_dir, sdk_name, '__init__.py'))
            shutil.rmtree(os.path.join(tmp_dir, sdk_name, '__pycache__'))
        except BaseException as ex:
            print(ex)

        # Write txt file included app_id
        cloud_apis = recipe_controller.get_cloud_apis()
        info = {
            'rest_api_url': rest_api_url,
            'cloud_apis': list(cloud_apis)
        }

        with open(os.path.join(tmp_dir, sdk_name, 'info.json'), 'w+') as fp:
            json.dump(info, fp)

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
        'user': {
            'id': 'admin-{}'.format(app_id),
            'group': 'admin',
            'creationDate': 0,
            'extra': {}
        }
    }
    return data


def response_body(func):
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.get('body', {})
    return wrap


class ServiceController(metaclass=ABCMeta):
    def __init__(self, bundle, app_id):
        self.bundle = bundle
        self.app_id = app_id
        self.common_init()

    @abstractmethod
    def common_init(self):
        # init object here .. assign boto3 session
        pass

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
        rest_api_url = self.get_rest_api_url(recipe_controller)
        sdk_bin = create_sdk_zipfile_bin(recipe_controller, rest_api_url)
        return sdk_bin

    def apply(self, recipe_controller):
        self.apply_cloud_api(recipe_controller)
        self.deploy_cloud_api(recipe_controller)
        self.common_apply(recipe_controller)

    @abstractmethod
    def common_apply(self, recipe_controller):
        pass


class BillServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self.cost_explorer = CostExplorer(self.boto3_session)

    def common_apply(self, recipe_controller):
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

    def common_apply(self, recipe_controller):
        return

    @response_body
    def create_user(self, recipe, email, password, extra):
        import cloud.auth.register as register
        parmas = {
            'email': email,
            'password': password,
            'extra': extra,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return register.do(data, boto3)['body']

    @response_body
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

    @response_body
    def delete_user(self, recipe, user_id):
        import cloud.auth.delete_user as delete_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return delete_user.do(data, boto3)

    @response_body
    def get_user(self, recipe, user_id):
        import cloud.auth.get_user as get_user
        parmas = {
            'user_id': user_id,
        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user.do(data, boto3)

    @response_body
    def get_user_count(self, recipe):
        import cloud.auth.get_user_count as get_user_count
        parmas = {

        }
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_user_count.do(data, boto3)

    @response_body
    def get_users(self, recipe, start_key, limit):
        import cloud.auth.get_users as get_users
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_users.do(data, boto3)

    @response_body
    def create_session(self, recipe, email, password):
        import cloud.auth.login as login
        params = {
            'email': email,
            'password': password
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return login.do(data, boto3)

    @response_body
    def delete_session(self, recipe, session_id):
        import cloud.auth.logout as logout
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return logout.do(data, boto3)

    @response_body
    def get_session(self, recipe, session_id):
        import cloud.auth.get_session as get_session
        params = {
            'session_id': session_id
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_session.do(data, boto3)

    @response_body
    def get_sessions(self, recipe, start_key, limit):
        import cloud.auth.get_sessions as get_sessions
        params = {'start_key': start_key,
                  'limit': limit}
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return get_sessions.do(data, boto3)

    @response_body
    def get_session_count(self, recipe):
        import cloud.auth.get_session_count as get_session_count
        parmas = {}
        data = make_data(self.app_id, parmas, recipe)
        boto3 = self.boto3_session
        return get_session_count.do(data, boto3)


class DatabaseServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self._init_table()

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'database-{}'.format(self.app_id)
        dynamodb.init_table(table_name)
        return

    def common_apply(self, recipe_controller):
        return

    @response_body
    def create_item(self, recipe, partition, item, read_permissions, write_permissions):
        import cloud.database.create_item as method
        params = {
            'partition': partition,
            'item': item,
            'read_permissions': read_permissions,
            'write_permissions': write_permissions,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def update_item(self, recipe, item_id, item, read_permissions, write_permissions):
        import cloud.database.update_item as method
        params = {
            'item_id': item_id,
            'item': item,
            'read_permissions': read_permissions,
            'write_permissions': write_permissions,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def put_item_field(self, recipe, item_id, field_name, field_value):
        import cloud.database.put_item_field as method
        params = {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def get_item(self, recipe, item_id):
        import cloud.database.get_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def delete_item(self, recipe, item_id):
        import cloud.database.delete_item as method
        params = {
            'item_id': item_id,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def get_items(self, recipe, partition, reverse):
        import cloud.database.get_items as method
        params = {
            'partition': partition,
            'reverse': reverse,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def get_item_count(self, recipe, partition):
        import cloud.database.get_item_count as method
        params = {
            'partition': partition,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)


class StorageServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self._init_bucket()
        self._init_table()

    def _init_bucket(self):
        s3 = S3(self.boto3_session)
        bucket_name = 'storage-{}'.format(self.app_id)
        s3.init_bucket(bucket_name)

    def _init_table(self):
        dynamodb = DynamoDB(self.boto3_session)
        table_name = 'storage-{}'.format(self.app_id)
        dynamodb.init_table(table_name)

    def common_apply(self, recipe_controller):
        return

    @response_body
    def create_folder(self, recipe, parent_path, folder_name, read_groups, write_groups):
        import cloud.storage.create_folder as method
        params = {
            'parent_path': parent_path,
            'folder_name': folder_name,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def upload_file(self, recipe, parent_path, file_name, file_bin, read_groups, write_groups):
        import cloud.storage.upload_file as method
        params = {
            'parent_path': parent_path,
            'file_name': file_name,
            'file_bin': file_bin,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def delete_folder(self, recipe, folder_path):
        import cloud.storage.delete_folder as method
        params = {
            'folder_path': folder_path,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def delete_file(self, recipe, file_path):
        import cloud.storage.delete_file as method
        params = {
            'file_path': file_path,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def download_file(self, recipe, file_path):
        import cloud.storage.download_file as method
        params = {
            'file_path': file_path,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)

    @response_body
    def get_folder_list(self, recipe, folder_path, start_key):
        import cloud.storage.get_folder_list as method
        params = {
            'folder_path': folder_path,
            'start_key': start_key,
        }
        data = make_data(self.app_id, params, recipe)
        boto3 = self.boto3_session
        return method.do(data, boto3)