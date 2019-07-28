
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_ids': ['str'],
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Delete users'
}


@NeedPermission(Permission.Run.Auth.delete_users)
def do(data, resource):
    body = {}
    params = data['params']

    user_ids = params.get('user_ids', [])
    success = resource.db_delete_item_batch(user_ids)
    body['success'] = success
    return body
