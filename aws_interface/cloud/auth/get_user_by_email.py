
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str'
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
    'description': 'Return user by email'
}


@NeedPermission(Permission.Run.Auth.get_user_by_email)
def do(data, resource):
    body = {}
    params = data['params']
    email = params.get('email', None)

    items, end_key = resource.db_query('user', [{'option': None, 'field': 'email', 'value': email, 'condition': 'eq'}])
    if items:
        body['item'] = items[0]
    else:
        body['item'] = None
    return body
