
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy_after_get_policy_code, get_policy_code, match_policy
from cloud.database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'join': "{\"user_id\": \"user\", "
                " \"info.user_id\": \"info.user\","
                " \"info_user_id\": \"user\", ...}"
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creation_date': 'float',
            '...': '...'
        },
    },
    'description': 'Get item'
}


@NeedPermission(Permission.Run.Database.get_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    join = params.get('join', {})
    item = resource.db_get_item(item_id)

    # Join 유효성 검사
    policy_code = get_policy_code(resource, item['partition'], 'join')
    if not match_policy(policy_code, user, join):
        body['item'] = None
        body['error'] = error.JOIN_POLICY_VIOLATION
        return body

    if match_policy_after_get_policy_code(resource, 'read', item['partition'], user, item):
        if join:
            util.join_item(resource, user, item, join)
        body['item'] = item
    else:
        body['error'] = error.PERMISSION_DENIED

    return body
