
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'field': 'str',
        'value?': 'str',
    },
    'output_format': {
        'user_id?': 'str',
    },
    'description': 'Set my information'
}


@NeedPermission(Permission.Run.Auth.set_me)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    if not user:
        body['error'] = error.LOGIN_IS_REQUIRED
        return body

    user_id = user['id']
    field = params.get('field')
    value = params.get('value', None)

    user_to_update = {
        field: value
    }

    # user = resource.db_get_item(user_id)

    # For security
    if field in ['id', 'email', 'password_hash', 'salt', 'groups', 'login_method']:
        body['error'] = error.FORBIDDEN_MODIFICATION
        return body
    elif not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', user, user_to_update):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body
    else:
        resource.db_update_item_v2(user_id, {
            'partition': 'user',
            'updated_date': float(time.time()),
            field: value
        })
        body['user_id'] = user_id
        return body
