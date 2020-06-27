
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
        'user': 'dict',
    },
    'output_format': {
        'user_id?': 'str'
    },
    'description': 'Update user information'
}


@NeedPermission(Permission.Run.Auth.update_user)
def do(data, resource):
    body = {}
    params = data['params']

    user_id = params.get('user_id', None)
    user = params.get('user')

    user_to_update = resource.db_get_item(user_id)

    # For security
    for field in user:
        if field in ['id', 'email', 'password_hash', 'salt', 'groups', 'login_method']:
            body['error'] = error.FORBIDDEN_MODIFICATION
            body.setdefault('forbidden_fields', [])
            body['forbidden_fields'].append(field)
        user_to_update[field] = user[field]

    resource.db_update_item(user_id, user_to_update)
    body['user_id'] = user_id
    body['success'] = True
    return body
