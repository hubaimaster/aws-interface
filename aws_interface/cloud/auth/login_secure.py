
from cloud.crypto import *
from cloud.auth.get_login_method import do as get_login_method
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import error
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str',
        'password': 'str'
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        },
        'user_id': 'str',
        'session_id': 'str',
        '__spk': 'str'
    },
    'description': 'Secure Login: When you request to server from client, '
                   'you should insert key name "__est": SHA3_512(<str(int(time.time()))> + __spk) in payload'
                   'time.time() must be seconds (NOT MS) '
}


@NeedPermission(Permission.Run.Auth.login_secure)
def do(data, resource):
    body = {}
    params = data['params']

    email = params.get('email', None)
    password = params.get('password', None)
    client_timestamp = params.get('client_timestamp', time.time())
    client_timestamp = int(client_timestamp)

    data['params']['login_method'] = 'email_login'
    login_conf = get_login_method(data, resource)['item']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.EMAIL_LOGIN_INVALID
        return body

    instructions = [
        (None, ('email', 'eq', email)),
        ('and', ('login_method', 'eq', 'email_login')),
    ]
    items, end_key = resource.db_query('user', instructions)
    if len(items) > 0:
        user = items[0]
        password_hash = user['password_hash']
        salt = user['salt']
        if password_hash == hash_password(password, salt):
            user_id = user['id']
            session_id = token_urlsafe(32)
            session_public_key = token_urlsafe(32)

            session_item = {
                'use_secure': True,  # 세션 보안 사용
                '__spk': session_public_key,
                'user_id': user_id,
                'session_type': 'email_login',
                'client_ip': data.get('client_ip', None),
                'timestamp_offset': client_timestamp - int(time.time())
            }
            _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
            body['session_id'] = session_id
            body['__spk'] = session_public_key
            body['user_id'] = user_id
        else:
            body['error'] = error.WRONG_PASSWORD
    else:
        body['error'] = error.NO_SUCH_ACCOUNT
    return body
