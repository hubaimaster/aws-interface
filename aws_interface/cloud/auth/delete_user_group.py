
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'group_name': 'str'
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Delete user group'
}


@NeedPermission(Permission.Run.Auth.delete_user_group)
def do(data, resource):
    body = {}
    params = data['params']
    group_name = params['group_name']

    if group_name in Permission.DEFAULT_USER_GROUPS:
        body['error'] = error.DEFAULT_USER_GROUP_CANNOT_BE_MODIFIED
        return Response(body)

    success = resource.db_delete_item('user-group-{}'.format(group_name))
    body['success'] = success
    return Response(body)
