
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
    },
    'output_format': {
        'success': 'bool'
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    if 'admin' not in user['groups']:
        body['success'] = False
        body['message'] = 'Permission denied'
        return Response(body)
    partition = params.get('partition', None)
    resource.db_create_partition(partition)

    body['success'] = True
    return Response(body)
