import importlib
import cloud.auth.get_me as get_me
from resource import get_resource
import cloud.message.error as error
import sys
import time
import traceback
from cloud.response import AWSResponse
import cloud.libs.simplejson as json
import cloud.logic.run_function as run_function
import cloud.notification.send_slack_message_as_system_notification as slack


CALLABLE_MODULE_WHITE_LIST = {
    # auth
    'cloud.auth.attach_group_permission',
    'cloud.auth.attach_user_group',
    'cloud.auth.change_password',
    'cloud.auth.change_password_admin',
    'cloud.auth.delete_sessions',
    'cloud.auth.delete_user',
    'cloud.auth.delete_user_group',
    'cloud.auth.find_password',
    # 'cloud.auth.get_email_login',
    # 'cloud.auth.get_group_permissions',
    'cloud.auth.get_all_permissions',
    # 'cloud.auth.get_guest_login',
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
    'cloud.auth.login_facebook',
    'cloud.auth.login_kakao',
    'cloud.auth.login_google',
    'cloud.auth.login_naver',
    'cloud.auth.logout',
    'cloud.auth.put_user_group',
    'cloud.auth.register',
    'cloud.auth.register_admin',
    'cloud.auth.delete_my_membership',
    'cloud.auth.refresh_session',
    # 'cloud.auth.set_email_login',
    # 'cloud.auth.set_guest_login',
    'cloud.auth.set_me',
    'cloud.auth.set_user',
    'cloud.auth.update_user',
    # database
    'cloud.database.create_partition',  # admin
    'cloud.database.delete_partition',  # admin
    'cloud.database.delete_partitions',  # admin
    'cloud.database.create_item',
    'cloud.database.delete_item',
    'cloud.database.delete_items',
    'cloud.database.get_item',
    'cloud.database.get_item_count',
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
    'cloud.logic.get_function_file',
    'cloud.logic.get_function_file_paths',
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
    # schedule
    'cloud.schedule.create_schedule',
    'cloud.schedule.delete_schedule',
    'cloud.schedule.get_schedule',
    'cloud.schedule.get_schedules',
    # notification
    'cloud.notification.create_email_provider',
    'cloud.notification.delete_email_provider',
    'cloud.notification.get_email_provider',
    'cloud.notification.get_email_providers',
    'cloud.notification.send_email',
    'cloud.notification.send_email2',
    'cloud.notification.send_sms',
    'cloud.notification.update_email_provider',
    'cloud.notification.send_slack_message'
}


# AWS Lambda handler
def aws_handler(event, context):
    import boto3
    query_params = event.get('queryStringParameters', {})
    if query_params is None:
        query_params = {}

    try:
        params = json.loads('{}'.format(event.get('body', '{}')))
    except Exception as ex:
        print(ex)
        params = event.get('body', {})

    vendor = 'aws'
    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()
    resource = get_resource(vendor, None, app_id, boto3.Session())

    body = abstracted_gateway(params, query_params, resource)
    response = AWSResponse(body)
    return response


def abstracted_gateway(params, query_params, resource):
    try:
        if 'webhook' in query_params:
            webhook_name = query_params['webhook']
            return abstracted_webhook(params, query_params, resource, webhook_name)
        else:
            return abstracted_handler(params, query_params, resource)

    except PermissionError as ex:
        error_traceback = traceback.format_exc()
        print('Exception: [{}]'.format(ex))
        print('error_traceback: [{}]'.format(error_traceback))
        body = {
            'error': error.PERMISSION_DENIED,
            'traceback': '{}'.format(error_traceback)
        }
        slack.send_system_slack_message(resource, str(body).replace('\\', ''))
        return body
    except Exception as ex:
        error_traceback = traceback.format_exc()
        print('Exception: [{}]'.format(ex))
        print('error_traceback: [{}]'.format(error_traceback))
        body = {
            'error': error.INVALID_REQUEST,
            'traceback': '{}'.format(error_traceback)
        }
        slack.send_system_slack_message(resource, str(body).replace('\\', ''))
        return body


def abstracted_webhook(params, query_params, resource, webhook_name):
    item_id = 'webhook-{}'.format(webhook_name)
    webhook = resource.db_get_item(item_id)
    body = {}
    if webhook:
        function_name = webhook['function_name']
        webhook_groups = webhook.get('groups', ['user'])  # TODO
        data = {
            'params': {
                'payload': {
                    'params': params,
                    'query_params': query_params,
                },
                'function_name': function_name,
            },
            'user': {
                'groups': webhook_groups
            },
        }
        body = run_function.do(data, resource)
        return body.get('response', None)
    else:
        body['error'] = error.NO_SUCH_WEBHOOK
        return body


def abstracted_handler(params, query_params, resource):
    current_time = time.time()
    module_name = params.get('module_name', None)
    if module_name not in CALLABLE_MODULE_WHITE_LIST:
        body = {
            'error': error.FORBIDDEN_REQUEST
        }
        return body
    data = {
        'params': params,
        'query_params': query_params,
    }
    user = get_me.do(data, resource).get('item', None)
    data['user'] = user

    module = importlib.import_module(module_name)
    sys.modules[module_name] = module

    # Invoke module
    body = module.do(data, resource)
    body['duration'] = time.time() - current_time
    return body
