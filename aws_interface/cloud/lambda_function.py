import importlib
import cloud.auth.get_me as get_me
import cloud.log.create_log as create_log
from resource import get_resource
import sys


CALLABLE_MODULE_WHITE_LIST = {
    # auth
    'cloud.auth.delete_user',
    'cloud.auth.delete_user_group',
    'cloud.auth.get_email_login',
    'cloud.auth.get_guest_login',
    'cloud.auth.get_me',
    'cloud.auth.get_session',
    'cloud.auth.get_user',
    'cloud.auth.get_users',
    'cloud.auth.guest',
    'cloud.auth.login',
    'cloud.auth.logout',
    'cloud.auth.register',
    'cloud.auth.set_user',
    # database
    'cloud.database.create_item',
    'cloud.database.delete_item',
    'cloud.database.delete_items',
    'cloud.database.get_item',
    'cloud.database.get_items',
    'cloud.database.put_item_field',
    'cloud.database.query_items',
    'cloud.database.update_item',
    # log
    'cloud.log.create_log',
    # logic
    'cloud.logic.run_function',
    # storage
    'cloud.storage.delete_b64',
    'cloud.storage.download_b64',
    'cloud.storage.upload_b64',
}


# AWS Lambda handler
def aws_handler(event, context):
    import boto3
    vendor = 'aws'
    params = event
    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()
    resource = get_resource(vendor, None, app_id, boto3.Session())
    return abstracted_handler(params, resource)


def abstracted_handler(params, resource):
    module_name = params.get('module_name', None)
    if module_name not in CALLABLE_MODULE_WHITE_LIST:
        print('module_name: {} not in CALLABLE_MODULE_WHITE_LIST'.format(module_name))
        response = {
            'statusCode': 403,
            'body': {
                'message': 'permission denied'
            }
        }
        return response
    data = {
        'params': params,
        'admin': False,
    }
    user = get_me.do(data, resource).get('body', {}).get('item', None)
    data['user'] = user

    module = importlib.import_module(module_name)
    sys.modules[module_name] = module
    module_response = module.do(data, resource)

    response = {
        'statusCode': module_response.get('statusCode', 200),
        'headers': module_response.get('header', {}),
        'body': module_response.get('body', {}),
    }
    return response
