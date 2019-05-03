
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'items': 'list',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    partitions = resource.db_get_partitions()
    body['items'] = partitions
    body['success'] = True
    return Response(body)
