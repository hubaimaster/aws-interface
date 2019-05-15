
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str'
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    partition = 'session'
    items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit, reverse=True)
    body['items'] = items
    body['end_key'] = end_key
    return Response(body)
