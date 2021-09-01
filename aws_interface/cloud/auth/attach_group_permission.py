
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'group_name': 'str',
        'permission': 'str'
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Attach permission to group'
}


@NeedPermission(Permission.Run.Auth.attach_group_permission)
def do(data, resource):
    body = {}
    params = data['params']
    group_name = params['group_name']
    permission = params['permission']

    if group_name == 'admin':
        body['error'] = error.ADMIN_GROUP_CANNOT_BE_MODIFIED
        return body

    item = resource.db_get_item('user-group-{}'.format(group_name))
    item_permissions = item.get('permissions', [])
    item_permissions.append(permission)
    item_permissions = [item_permission for item_permission in item_permissions if item_permission]
    item_permissions = list(set(item_permissions))

    item['permissions'] = sorted(item_permissions)

    success = resource.db_put_item('user_group', item, 'user-group-{}'.format(group_name))
    body['success'] = success
    return body
