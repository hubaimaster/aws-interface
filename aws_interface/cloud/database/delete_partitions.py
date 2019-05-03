
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partitions': 'list',
    },
    'output_format': {
        'success': 'bool'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    partitions = params.get('partitions', [])
    for partition in partitions:
        resource.db_delete_partition(partition)

    body['success'] = True
    return Response(body)
