
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
from cloud.auth import util
from cloud.database import util as database_util
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
        'user': 'dict',
    },
    'output_format': {
        'user_id?': 'str'
    },
    'description': 'Update user information'
}


@NeedPermission(Permission.Run.Auth.update_user)
def do(data, resource):
    body = {}
    params = data['params']
    runner_user = data.get('user', None)  # 작업을 시행하는 유저

    user_id = params.get('user_id', None)
    new_user_fields = params.get('user')

    user_to_update = resource.db_get_item(user_id)
    if user_to_update['partition'] != 'user':
        body['error'] = error.NOT_USER_PARTITION
        body['success'] = False
        return body

    if not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', runner_user, new_user_fields):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body

    # 생성날짜 유지를 위해 기록
    creation_date = user_to_update.get('creation_date', float(time.time()))

    # For security
    new_item = {}
    for field in new_user_fields:
        if field in ['id', 'email', 'password_hash', 'salt', 'groups', 'login_method']:
            body['error'] = error.FORBIDDEN_MODIFICATION
            body.setdefault('forbidden_fields', [])
            body['forbidden_fields'].append(field)
        else:
            new_item[field] = new_user_fields[field]
    new_item = util.simplify_item(user_to_update, new_item)
    new_item['partition'] = 'user'
    new_item['updated_date'] = float(time.time())
    new_item['creation_date'] = creation_date

    # 소트키 존재시 무조건 포함
    sort_keys = database_util.get_sort_keys(resource)
    for sort_key_item in sort_keys:
        s_key = sort_key_item.get('sort_key', None)
        if s_key and s_key not in new_item and user_to_update.get(s_key, None) is not None:
            new_item[s_key] = user_to_update.get(s_key, None)

    resource.db_update_item_v2(user_id, new_item)
    body['user_id'] = user_id
    body['success'] = True
    return body
