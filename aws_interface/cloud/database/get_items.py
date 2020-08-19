
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from concurrent.futures import ThreadPoolExecutor
from cloud.database import util
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'start_key': 'dict',
        'limit': 'int=100',
        'reverse': 'bool=False',
        'join': "{\"user_id\": \"user\", "
                " \"info.user_id\": \"info.user\","
                " \"info_user_id\": \"user\", ...}"
    },
    'output_format': {
        'items?': [{
            'id': 'str',
            'creation_date': 'float',
            '...': '...',
        }],
        'end_key?': 'str',
    },
    'description': 'Get items and its end_key to iterate'
}


@NeedPermission(Permission.Run.Database.get_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    partition = params.get('partition', None)
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)
    join = params.get('join', {})

    if not limit:
        limit = 100

    if type(start_key) is str:
        start_key = json.loads(start_key)
    if resource.db_has_partition(partition):
        items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit, reverse=reverse)
        policy_code = get_policy_code(resource, partition, 'read')
        filtered = []
        for item in items:
            if match_policy(policy_code, user, item):
                filtered.append(item)

        if join:
            util.join_items(resource, user, filtered, join)

        body['items'] = filtered
        body['end_key'] = end_key
        return body
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.PERMISSION_DENIED
        return body
