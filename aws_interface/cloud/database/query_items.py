
from cloud.response import Response
from cloud.permission import has_read_permission
from cloud.permission import Permission, NeedPermission
from cloud.message import error
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'query': 'list',
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


@NeedPermission(Permission.Run.Database.query_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    partition = params.get('partition', None)
    query_instructions = params.get('query', None)
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    if type(start_key) is str:
        start_key = json.loads(start_key)

    if resource.db_get_item(partition):
        items, end_key = resource.db_query(partition, query_instructions, start_key, limit, reverse)

        filtered = []
        for item in items:
            if has_read_permission(user, item):
                filtered.append(item)

        body['items'] = filtered
        body['end_key'] = end_key
        return Response(body)
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.NO_SUCH_PARTITION
        return Response(body)
