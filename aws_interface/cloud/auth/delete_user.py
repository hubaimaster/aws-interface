
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Delete user and delete session'
}


@NeedPermission(Permission.Run.Auth.delete_user)
def do(data, resource):
    body = {}
    params = data['params']
    user_id = params.get('user_id', None)
    item = resource.db_get_item(user_id)
    if item.get('partition', None) != 'user':
        body['error'] = error.NOT_USER_PARTITION
        return body
    success = resource.db_delete_item(user_id)
    body['success'] = success
    return body
