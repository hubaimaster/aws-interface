
from cloud.crypto import *
import cloud.shortuuid as shortuuid
from cloud.auth.get_login_method import do as get_login_method
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from secrets import token_urlsafe

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id?': 'str',
    },
    'output_format': {
        'session_id': 'str',
        'error?': {
            'code': 'int',
            'message': 'str'
        }
    },
    'description': 'Guest login. If you save guest_id after login '
                   'and send it as a parameter after logout, you can keep your guest status.'
}


def put_guest_session(resource, guest_id):
    session_id = token_urlsafe(32)
    session_item = {
        'user_id': guest_id,
        'session_type': 'guest_login',
    }
    resource.db_put_item('session', session_item, Hash.sha3_512(session_id))
    return session_id


@NeedPermission(Permission.Run.Auth.guest)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)
    session_id = params.get('session_id', None)

    data['params']['login_method'] = 'guest_login'
    login_conf = get_login_method(data, resource)['item']

    default_group_name = login_conf['default_group_name']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.GUEST_LOGIN_INVALID
        return body

    if user:
        body['session_id'] = session_id
        body['guest_id'] = user['id']
        return body
    else:
        guest_id = shortuuid.uuid()
        email = '{}@guest.com'.format(shortuuid.uuid())
        item = {
            'email': email,
            'groups': [default_group_name],
            'login_method': 'guest_login',
        }
        resource.db_put_item('user', item, item_id=guest_id)
        session_id = put_guest_session(resource, guest_id)
        body['session_id'] = session_id
        body['guest_id'] = guest_id
        return body
