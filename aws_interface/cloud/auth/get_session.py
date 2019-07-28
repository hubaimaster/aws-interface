
from cloud.crypto import Hash
from cloud.permission import Permission, NeedPermission

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
        },
    },
    'description': 'Return session item'
}


@NeedPermission(Permission.Run.Auth.get_session)
def do(data, resource):
    body = {}
    params = data['params']
    session_id = params.get('session_id', None)
    item = resource.db_get_item(Hash.sha3_512(session_id))
    body['item'] = item
    return body
