
from cloud.crypto import Hash
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str'
    },
    'output_format': {
        'item?': {
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'groups': ['str'],
        },
    },
    'description': 'Get my information via session'
}


@NeedPermission(Permission.Run.Auth.get_me)
def do(data, resource):
    body = {}
    params = data['params']
    session_id = params.get('session_id', None)
    try:
        item = resource.db_get_item(Hash.sha3_512(session_id))
    except BaseException as ex:
        print(ex)
        body['error'] = error.PERMISSION_DENIED
        return body
    print('session_item:', item)
    if item:
        user_id = item.get('user_id', None)
    else:
        user_id = None

    if user_id:
        user = resource.db_get_item(user_id)
        body['item'] = user
    else:
        body['item'] = None
    return body
