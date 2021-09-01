
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
        'field': 'str',
        'value?': 'str',
    },
    'output_format': {
        'user_id?': 'str'
    },
    'description': 'Set user information'
}


@NeedPermission(Permission.Run.Auth.set_user)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    user_id = params.get('user_id', None)
    field = params.get('field')
    value = params.get('value', None)
    user_to_update = {
        field: value,
        'updated_date': float(time.time())
    }

    item = resource.db_get_item(user_id)
    if item.get('partition', None) != 'user':
        body['error'] = error.NOT_USER_PARTITION
        body['success'] = False
        return body

    # For security
    if field in ['id', 'password_hash', 'salt', 'groups', 'login_method']:
        body['error'] = error.FORBIDDEN_MODIFICATION
        return body
    elif not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', user, user_to_update):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body
    else:
        # for field, value in user_to_update.items():
        #     item[field] = value
        user_to_update['partition'] = 'user'
        resource.db_update_item_v2(user_id, user_to_update)
        body['user_id'] = user_id
        return body
