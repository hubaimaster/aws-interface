
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'group_name': 'str',
        'description': 'str',
        'permissions': ['str'],
    },
    'output_format': {

    }
}


@NeedPermission(Permission.Run.Auth.put_user_group)
def do(data, resource):
    body = {}
    params = data['params']
    group_name = params['group_name']
    description = params.get('description', None)
    permissions = params.get('permissions', [])
    if not description:
        description = None

    if group_name in Permission.DEFAULT_USER_GROUPS:
        body['error'] = error.DEFAULT_USER_GROUP_CANNOT_BE_MODIFIED
        return Response(body)
    group_id = 'user-group-{}'.format(group_name)
    group_item = {
        'name': group_name,
        'description': description,
        'permissions': permissions,
    }

    success = resource.db_put_item('user_group', group_item, group_id)
    if success:
        return Response(body)
    else:
        body['error'] = error.PUT_USER_GROUP_FAILED
        return Response(body)
