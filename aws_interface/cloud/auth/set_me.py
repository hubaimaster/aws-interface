
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
from cloud.database import util
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
        creation_date = user.get('creation_date', time.time())

        user_to_update = {
            'partition': 'user',
            'updated_date': float(time.time()),
            field: value,
            'creation_date': creation_date,
        }
        # 소트키 존재시 무조건 포함
        sort_keys = util.get_sort_keys(resource)
        for sort_key_item in sort_keys:
            s_key = sort_key_item.get('sort_key', None)
            if s_key and s_key not in user_to_update and user.get(s_key, None) is not None:
                user_to_update[s_key] = user.get(s_key, None)

        resource.db_update_item_v2(user_id, user_to_update)
        body['user_id'] = user_id
        return body
