import importlib
import cloud.auth.get_me as get_me
from resource import get_resource
import cloud.message.error
import sys
import time


CALLABLE_MODULE_WHITE_LIST = {
    # auth
    'cloud.auth.attach_group_permission',
    'cloud.auth.attach_user_group',
    'cloud.auth.delete_sessions',
    'cloud.auth.delete_user',
    'cloud.auth.delete_user_group',
    'cloud.auth.get_email_login',
    'cloud.auth.get_group_permissions',
    'cloud.auth.get_all_permissions',
    'cloud.auth.get_guest_login',
    'cloud.auth.get_me',
    'cloud.auth.get_session',
    'cloud.auth.get_session_count',
    'cloud.auth.get_sessions',
    'cloud.auth.get_user',
    'cloud.auth.get_user_by_email',
    'cloud.auth.get_user_count',
    'cloud.auth.get_user_groups',
    'cloud.auth.get_users',
    'cloud.auth.guest',
    'cloud.auth.login',
    'cloud.auth.logout',
    'cloud.auth.put_user_group',
    'cloud.auth.register',
    'cloud.auth.register_admin',
    'cloud.auth.set_email_login',
    'cloud.auth.set_guest_login',
    'cloud.auth.set_me',
    'cloud.auth.set_user',
    # database
    'cloud.database.create_partition',  # admin
    'cloud.database.delete_partition',  # admin
    'cloud.database.delete_partitions',  # admin
    'cloud.database.create_item',
    'cloud.database.delete_item',
    'cloud.database.delete_items',
    'cloud.database.get_item',
    'cloud.database.get_items',
    'cloud.database.get_items',
    'cloud.database.put_item_field',
    'cloud.database.query_items',
    'cloud.database.update_item',
    # log
    'cloud.log.create_log',
    'cloud.log.get_logs',
    # logic
    'cloud.logic.create_function',
    'cloud.logic.create_function_test',
    'cloud.logic.create_trigger',
    'cloud.logic.delete_function',
    'cloud.logic.delete_function_test',
    'cloud.logic.delete_trigger',
    'cloud.logic.get_function',
    'cloud.logic.get_function_tests',
    'cloud.logic.get_functions',
    'cloud.logic.get_trigger',
    'cloud.logic.get_triggers',
    'cloud.logic.run_function',
    'cloud.logic.update_function',
    'cloud.logic.update_trigger',
    # storage
    'cloud.storage.delete_b64',
    'cloud.storage.download_b64',
    'cloud.storage.get_b64_info_items',
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
    current_time = time.time()
    module_name = params.get('module_name', None)
    if module_name not in CALLABLE_MODULE_WHITE_LIST:
        response = {
            'statusCode': 403,
            'body': {
                'error': cloud.message.error.FORBIDDEN_REQUEST
            },
            'error': cloud.message.error.FORBIDDEN_REQUEST
        }
        return response
    data = {
        'params': params,
    }
    user = get_me.do(data, resource).get('body', {}).get('item', None)
    data['user'] = user

    module = importlib.import_module(module_name)
    sys.modules[module_name] = module

    # Invoke module
    try:
        module_response = module.do(data, resource)
    except PermissionError as ex:
        print(ex)
        response = {
            'statusCode': 401,
            'body': {
                'error': cloud.message.error.PERMISSION_DENIED
            },
            'error': cloud.message.error.PERMISSION_DENIED
        }
        return response
    except Exception as ex:
        print('Exception: [{}]'.format(ex))
        response = {
            'statusCode': 400,
            'body': {
                'error': cloud.message.error.INVALID_REQUEST
            },
            'error': cloud.message.error.INVALID_REQUEST
        }
        return response

    response = {
        'statusCode': module_response.get('statusCode', 200),
        'headers': module_response.get('header', {}),
        'body': module_response.get('body', {}),
    }
    error = module_response.get('error', None)
    if error:
        response['error'] = error
    response['duration'] = time.time() - current_time
    return response
