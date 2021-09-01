
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
from cloud.auth import util
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
    old_user = data.get('user', None)

    user_id = params.get('user_id', None)
    new_user_fields = params.get('user')

    user_to_update = resource.db_get_item(user_id)
    if user_to_update['partition'] != 'user':
        body['error'] = error.NOT_USER_PARTITION
        body['success'] = False
        return body

    if not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', old_user, new_user_fields):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body

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
    resource.db_update_item_v2(user_id, new_item)
    body['user_id'] = user_id
    body['success'] = True
    return body
