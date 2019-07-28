
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
        'field': 'str',
        'value?': 'str',
    },
    'output_format': {
        'user_id?': 'str'
    },
    'description': 'Set user information'
}


@NeedPermission(Permission.Run.Auth.set_user)
def do(data, resource):
    body = {}
    params = data['params']

    user_id = params.get('user_id', None)
    field = params.get('field')
    value = params.get('value', None)

    user = resource.db_get_item(user_id)

    # For security
    if field in ['id', 'email', 'password_hash', 'salt', 'groups', 'login_method']:
        body['error'] = error.FORBIDDEN_MODIFICATION
        return body
    else:
        user[field] = value
        resource.db_update_item(user_id, user)
        body['user_id'] = user_id
        return body
