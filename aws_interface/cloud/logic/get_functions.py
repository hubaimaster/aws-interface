
from cloud.response import Response
from cloud.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'start_key': 'str?',
        'limit': 'int?',
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str',
    }
}


def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    start_key = params.get('start_key', None)
    limit = params.get('limit', None)

    items, end_key = resource.db_get_items(partition, start_key, limit)

    body['items'] = items
    body['end_key'] = end_key
    return Response(body)
