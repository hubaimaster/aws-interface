
from cloud.response import Response
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.permission import Permission, NeedPermission
from cloud.message import error
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
    },
    'output_format': {
        'items?': [{'str': 'any'}],
        'end_key?': 'str',
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
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
        body['items'] = filtered
        body['end_key'] = end_key
        return Response(body)
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.PERMISSION_DENIED
        return Response(body)
