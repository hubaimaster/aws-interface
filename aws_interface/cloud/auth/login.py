
from cloud.crypto import *
from cloud.response import Response
import cloud.auth.get_email_login as get_email_login
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import Error

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
        'session_id': 'str',
    }
}


@NeedPermission(Permission.Run.Auth.login)
def do(data, resource):
    body = {}
    params = data['params']

    email = params.get('email', None)
    password = params.get('password', None)

    login_conf = get_email_login.do(data, resource)['body']['item']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = Error.email_login_invalid
        return Response(body)

    instructions = [
        (None, ('email', 'eq', email))
    ]
    items, end_key = resource.db_query('user', instructions)
    if len(items) > 0:
        user = items[0]
        password_hash = user['password_hash']
        salt = user['salt']
        if password_hash == hash_password(password, salt):
            user_id = user['id']
            session_id = token_urlsafe(32)
            session_item = {
                'user_id': user_id,
                'session_type': 'email_login',
            }
            _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
            body['session_id'] = session_id
        else:
            body['error'] = Error.wrong_password
    else:
        body['error'] = Error.no_such_account
    return Response(body)
