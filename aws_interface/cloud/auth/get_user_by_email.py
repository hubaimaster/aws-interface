
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth import get_policy_code

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
    user = data.get('user', None)
    email = params.get('email', None)

    items, end_key = resource.db_query('user', [{'option': None, 'field': 'email', 'value': email, 'condition': 'eq'}])
    if items:
        if not get_policy_code.match_policy_after_get_policy_code(resource, 'read', 'user', user, items[0]):
            body['item'] = None
            body['error'] = error.READ_POLICY_VIOLATION
            return body
        body['item'] = items[0]
    else:
        body['item'] = None
    return body
