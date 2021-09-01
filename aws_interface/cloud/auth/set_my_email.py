
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'email': 'str',
    },
    'output_format': {
        'user_id?': 'str',
    },
    'description': 'Change my email'
}


@NeedPermission(Permission.Run.Auth.set_my_email)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    user_id = user['id']

    email = params.get('email')

    instructions = [
        [None, 'email', 'eq', email]
    ]
    items, end_key = resource.db_query('user', instructions)
    users = list(items)
    if len(users) > 0:
        body['error'] = error.EXISTING_ACCOUNT
        return body

    # user = resource.db_get_item(user_id)
    if not get_policy_code.match_policy_after_get_policy_code(resource, 'update', 'user', user, {'email': email}):
        body['error'] = error.UPDATE_POLICY_VIOLATION
        return body
    user_to_update = {
        'partition': 'user',
        'updated_date': float(time.time()),
        'email': email
    }
    resource.db_update_item_v2(user_id, user_to_update)
    body['user_id'] = user_id
    return body
