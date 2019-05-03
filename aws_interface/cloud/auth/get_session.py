
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str'
    },
    'output_format': {
        'item': {
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'group': 'str',
            'extra': 'map',
        }
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    session_id = params.get('session_id', None)
    item = resource.db_get_item(session_id)
    body['item'] = item
    return Response(body)
