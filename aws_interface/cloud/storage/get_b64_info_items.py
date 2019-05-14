
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'start_key': 'str',
        'limit': 'int',
        'reverse': 'bool',
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str',
        'success': 'bool'
    }
}


def do(data, resource):  # This is for admins
    body = {}
    params = data['params']

    partition = 'files'
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit, reverse=reverse)

    body['items'] = list(filter(lambda x: x.get('next_file_id', None) is None, items))
    body['end_key'] = end_key
    body['success'] = True
    return Response(body)

