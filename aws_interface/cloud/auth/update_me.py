
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
        'item': 'dict',
        'ignore_error': 'bool?=False'
    },
    'output_format': {
        'user_id?': 'str',
    },
    'description': 'Update my information'
}


@NeedPermission(Permission.Run.Auth.update_me)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    user_id = user['id']
    ignore_error = params.get('ignore_error', False)

    user_item = params.get('item', {})
    user_to_update = {}

    # user = resource.db_get_item(user_id)
    # For security
    for field, value in user_item.items():
        if field in ['id', 'email', 'password_hash', 'salt', 'groups', 'login_method']:
            body['error'] = error.FORBIDDEN_MODIFICATION
            if not ignore_error:  # 에러 무시하는 경우
                return body
        else:
            user_to_update[field] = value

    if not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', user, user_to_update):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body
    else:
        creation_date = user.get('creation_date', time.time())
        user_to_update['partition'] = 'user'
        user_to_update['updated_date'] = float(time.time())
        user_to_update['creation_date'] = creation_date

        # 소트키 존재시 무조건 포함
        sort_keys = util.get_sort_keys(resource)
        for sort_key_item in sort_keys:
            s_key = sort_key_item.get('sort_key', None)
            if s_key and s_key not in user_to_update and user.get(s_key, None) is not None:
                user_to_update[s_key] = user.get(s_key, None)

        resource.db_update_item_v2(user_id, user_to_update)
        body['user_id'] = user_id
        return body
