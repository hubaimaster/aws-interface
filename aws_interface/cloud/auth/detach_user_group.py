
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import Error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_id': 'str',
        'group_name': 'str',
    },
    'output_format': {

    }
}


@NeedPermission(Permission.Run.Auth.attach_user_group)
def do(data, resource):
    body = {}
    params = data['params']
    user_id = params['user_id']
    group_name = params.get('group_name')

    user = resource.db_get_item(user_id)
    groups = user.get('groups', [])
    if group_name in groups:
        groups.remove(group_name)
    groups = list(set(groups))
    user['groups'] = groups

    _ = resource.db_put_item('user', user, user_id)
    return Response(body)
