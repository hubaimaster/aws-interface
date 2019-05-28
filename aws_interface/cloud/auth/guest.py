
from cloud.response import Response
import cloud.shortuuid as shortuuid
import cloud.auth.get_guest_login as get_guest_login
from cloud.permission import Permission, NeedPermission
from cloud.message import error


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'guest_id?': 'str',
    },
    'output_format': {
        'guest_id': 'str',
        'session_id': 'str',
        'error?': {
            'code': 'int',
            'message': 'str'
        }
    }
}


@NeedPermission(Permission.Run.Auth.guest)
def do(data, resource):
    body = {}
    params = data['params']

    guest_id = params.get('guest_id', None)

    login_conf = get_guest_login.do(data, resource)['body']['item']
    default_group_name = login_conf['default_group_name']
    enabled = login_conf['enabled']
    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    if not enabled:
        body['error'] = error.GUEST_LOGIN_INVALID
        return Response(body)

    if guest_id:
        item = resource.db_get_item(guest_id)
        if item:
            session_item = {
                'user_id': guest_id,
                'session_type': 'guest_login',
            }
            resource.db_put_item('session', session_item)
            return Response(body)
        else:
            body['error'] = error.NO_SUCH_GUEST
            return Response(body)
    else:
        guest_id = shortuuid.uuid()
        email = '{}@guest.com'.format(shortuuid.uuid())
        item = {
            'email': email,
            'groups': [default_group_name],
            'extra': {},
            'login_method': 'guest_login',
        }
        resource.db_put_item('user', item, item_id=guest_id)
        session_id = shortuuid.uuid()
        session_item = {
            'user_id': guest_id,
            'session_type': 'guest_login',
        }
        resource.db_put_item('session', session_item, item_id=session_id)
        body['session_id'] = session_id
        body['guest_id'] = guest_id
        return Response(body)

