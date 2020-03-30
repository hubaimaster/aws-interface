
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Delete my membership'
}


@NeedPermission(Permission.Run.Auth.delete_my_membership)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    user_id = user.get('id')
    success = resource.db_delete_item(user_id)
    body['success'] = success
    return body
