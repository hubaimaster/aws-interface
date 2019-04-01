
from cloud.response import Response
from cloud.database.util import has_read_permission
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
        'items': 'list',
        'end_key': 'str'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    partition = params.get('partition', None)
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    if type(start_key) is str:
        start_key = json.loads(start_key)

    items, end_key = resource.db_get_items(partition, start_key, limit, reverse)

    filtered = []
    for item in items:
        if has_read_permission(user, item):
            item.pop('read_groups')
            item.pop('write_groups')
            item.pop('partition')
            filtered.append(item)

    body['items'] = filtered
    body['end_key'] = end_key
    return Response(body)
