
from cloud.crypto import *
from cloud.auth.get_login_method import do as get_login_method
from secrets import token_urlsafe
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        },
        'session_id': 'str',
    },
    'description': 'Refresh session'
}


def create_session(resource, user):
    user_id = user['id']
    session_id = token_urlsafe(32)
    login_method = user['login_method']
    session_item = {
        'user_id': user_id,
        'session_type': login_method,
    }
    _ = resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


def remove_session(resource, session_id):
    return resource.db_delete_item(Hash.sha3_512(session_id))


@NeedPermission(Permission.Run.Auth.refresh_session)
def do(data, resource):
    body = {}
    params = data['params']
    session_id = params.get('session_id', None)
    user = data.get('user', None)
    if user:
        remove_session(resource, session_id)
        session_id = create_session(resource, user)
        body['session_id'] = session_id
    else:
        body['error'] = error.INVALID_SESSION
    return body
