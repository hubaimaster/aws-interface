
from cloud.response import Response
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

    }
}


@NeedPermission(Permission.Run.Auth.attach_group_permission)
def do(data, resource):
    body = {}
    params = data['params']
    group_name = params['group_name']

    if group_name == 'admin':
        body['error'] = error.ADMIN_GROUP_CANNOT_BE_MODIFIED
        return Response(body)

    permission = params.get('permission', [])

    item = resource.db_get_item('user-group-{}'.format(group_name))
    item_permissions = item.get('permissions', [])
    item_permissions.append(permission)
    item_permissions = list(set(item_permissions))
    item['permissions'] = sorted(item_permissions)

    _ = resource.db_put_item('user_group', item, 'user-group-{}'.format(group_name))
    return Response(body)
