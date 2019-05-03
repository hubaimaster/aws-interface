
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str'
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creationDate': 'int',
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
    try:
        item = resource.db_get_item(session_id)
    except BaseException as ex:
        print(ex)
        body['message'] = 'permission denied'
        return Response(body)

    user_id = item.get('userId', None)
    if user_id:
        user = resource.db_get_item(user_id)
        body['item'] = user
    else:
        body['item'] = None
    return Response(body)
