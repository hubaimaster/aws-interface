
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
    },
    'output_format': {
        'item': {
            'count': 'int'
        }
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    partition = params['partition']

    count = resource.db_get_count(partition)
    body['item'] = {
        'count': count
    }
    return Response(body)
