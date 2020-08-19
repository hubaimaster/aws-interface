
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'email': 'str',
    },
    'output_format': {
        'user_id?': 'str',
    },
    'description': 'Change my email'
}


@NeedPermission(Permission.Run.Auth.set_my_email)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    user_id = user['id']

    email = params.get('email')

    user = resource.db_get_item(user_id)

    user['email'] = email
    resource.db_update_item(user_id, user)
    body['user_id'] = user_id
    return body
