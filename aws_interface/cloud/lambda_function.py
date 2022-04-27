import importlib
import cloud.auth.get_me as get_me
from resource import get_resource
import cloud.message.error as error
import sys
import time
import traceback
from cloud.response import AWSResponse, AWSImageResponse
import cloud.libs.simplejson as json
import cloud.logic.run_function as run_function
import cloud.notification.send_slack_message_as_system_notification as slack

# Localhost server, Internal gate to make logic call fast
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from socketserver import ThreadingMixIn, ForkingMixIn
from cloud import env


# Imports AWS related resources
try:
    import boto3
    with open('./cloud/app_id.txt', 'r') as file:
        app_id = file.read()
    resource = get_resource('aws', None, app_id, boto3.Session())
except Exception as e:
    print(e)


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        # print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #         str(self.path), str(self.headers), post_data.decode('utf-8'))
        body = post_data.decode('utf-8')
        body_json = json.loads(body)
        client_address = None
        if self.client_address:
            client_address = self.client_address[0]
        response = abstracted_gateway(body_json, {}, resource, client_ip=client_address)
        json_response = json.dumps(response)
        json_response = json_response.encode('utf-8')
        self._set_response()
        self.wfile.write(json_response)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class ServerThread(Thread):
    def __init__(self):
        super().__init__()
        port = 20131
        server_address = ('', port)
        self.can_run_subprocess = False
        self.httpd = ThreadingSimpleServer(server_address, S)

    def run(self) -> None:
        print('Starting httpd...\n')
        try:
            self.can_run_subprocess = True
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        self.httpd.server_close()
        print('Stopping httpd...')

    def stop(self):
        self.httpd.server_close()


if env.safe_to_run_code():
    server_thread = ServerThread()
    server_thread.start()
else:
    print('NOT SAFE TO RUN LOCAL SERVER TO RUN CODE')

# --- end of localhost server ---


CALLABLE_MODULE_WHITE_LIST = {
    # auth
    'cloud.auth.attach_group_permission',
    'cloud.auth.attach_user_group',
    'cloud.auth.detach_user_group',
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
    'cloud.auth.has_account',
    'cloud.auth.login',
    'cloud.auth.login_facebook',
    'cloud.auth.login_kakao',
    'cloud.auth.login_google',
    'cloud.auth.login_naver',
    'cloud.auth.login_secure',
    'cloud.auth.logout',
    'cloud.auth.put_user_group',
    'cloud.auth.register',
    'cloud.auth.register_admin',
    'cloud.auth.delete_my_membership',
    'cloud.auth.refresh_session',
    # 'cloud.auth.set_email_login',
    # 'cloud.auth.set_guest_login',
    'cloud.auth.set_me',
    'cloud.auth.set_my_email',
    'cloud.auth.set_user',
    'cloud.auth.set_user_email',
    'cloud.auth.update_user',
    'cloud.auth.update_me',
    # database
    'cloud.database.create_partition',  # admin
    'cloud.database.delete_partition',  # admin
    'cloud.database.delete_partitions',  # admin
    'cloud.database.batch_get_items',
    'cloud.database.create_item',
    'cloud.database.create_items',
    'cloud.database.delete_item',
    'cloud.database.delete_items',
    'cloud.database.get_item',
    'cloud.database.get_item_count',
    'cloud.database.get_items',
    'cloud.database.get_partitions',
    'cloud.database.put_item_field',
    'cloud.database.query_items',
    'cloud.database.update_item',
    'cloud.database.update_item_v2',
    'cloud.database.update_items',
    'cloud.database.update_items_v2',
    # log
    'cloud.log.create_log',
    'cloud.log.get_logs',
    # logic
    'cloud.logic.create_function',
    'cloud.logic.create_function_test',
    'cloud.logic.create_packages_zip',
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
    'cloud.logic.set_function_metadata',
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
    'cloud.notification.send_slack_message',

    # trigger
    'cloud.trigger.create_trigger',
    'cloud.trigger.delete_trigger',
    'cloud.trigger.get_triggers',
}


def print_log(event, response):
    # try:
    #     print({
    #         'event': event,
    #         'response': response
    #     })
    # except Exception as e:
    #     print({
    #         'Exception': str(e)
    #     })
    pass


# AWS Lambda handler
def aws_handler(event, context):
    client_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', None)
    query_params = event.get('queryStringParameters', {})
    if query_params is None:
        query_params = {}
    try:
        params = json.loads('{}'.format(event.get('body', '{}')))
    except Exception as ex:
        print(ex)
        params = event.get('body', {})

    body = abstracted_gateway(params, query_params, resource, client_ip)
    if '__html__' in body:
        html_response = body['__html__']
        response = AWSResponse(html_response, content_type='text/html')
        print_log(event, response)
        return response
    elif '__image__' in body:
        image_base_64 = body['__image__']
        content_type = body.get('content_type', 'image/gif')
        response = AWSImageResponse(image_base_64, content_type)
        print_log(event, response)
        return response
    else:
        response = AWSResponse(body)
        print_log(event, response)
        return response


def abstracted_gateway(params, query_params, resource, client_ip):
    try:
        if 'webhook' in query_params:
            webhook_name = query_params['webhook']
            return abstracted_webhook(params, query_params, resource, webhook_name, client_ip)
        else:
            return abstracted_handler(params, query_params, resource, client_ip)

    except PermissionError as ex:
        error_traceback = traceback.format_exc()
        print('Exception: [{}]'.format(ex))
        print('error_traceback: [{}]'.format(error_traceback))
        body = {
            'error': error.PERMISSION_DENIED
        }
        if params and params.get('show_traceback', False):
            body['traceback'] = '{}'.format(error_traceback)
        slack.send_system_slack_message(resource, str(error_traceback).replace('\\', ''))
        return body
    except Exception as ex:
        error_traceback = traceback.format_exc()
        print('Exception: [{}]'.format(ex))
        print('error_traceback: [{}]'.format(error_traceback))
        body = {
            'error': error.INVALID_REQUEST
        }
        if params and params.get('show_traceback', False):
            body['traceback'] = '{}'.format(error_traceback)
        slack.send_system_slack_message(resource, str(error_traceback).replace('\\', ''))
        return body


def abstracted_webhook(params, query_params, resource, webhook_name, client_ip):
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
            'client_ip': client_ip
        }
        body = run_function.do(data, resource)
        return body.get('response', None)
    else:
        body['error'] = error.NO_SUCH_WEBHOOK
        return body


def abstracted_handler(params, query_params, resource, client_ip):
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
        'client_ip': client_ip,
    }
    user_response = get_me.do(data, resource, system_call=True)
    user = user_response.get('item', None)
    user_error = user_response.get('error', None)
    if user_error:
        body = {
            'error': user_error
        }
    else:
        data['user'] = user
        module = importlib.import_module(module_name)
        sys.modules[module_name] = module
        # Invoke module
        body = module.do(data, resource)
    body['duration'] = time.time() - current_time
    return body
