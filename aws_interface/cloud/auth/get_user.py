
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_id': 'str'
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'groups': 'list',
            '...': '...',
        }
    },
    'description': 'Return user item by user_id'
}


@NeedPermission(Permission.Run.Auth.get_user)
def do(data, resource):
    body = {}
    params = data['params']
    user_id = params.get('user_id', None)

    item = resource.db_get_item(user_id)
    body['item'] = item
    return body
