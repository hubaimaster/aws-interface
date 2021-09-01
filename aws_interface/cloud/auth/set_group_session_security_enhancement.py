
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'group_name': 'str',
        'enabled': 'bool'
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Enables the session security function of the user group'
}


@NeedPermission(Permission.Run.Auth.set_group_session_security_enhancement)
def do(data, resource):
    body = {}
    params = data['params']
    group_name = params['group_name']
    enabled = params['enabled']

    if group_name == 'admin':
        body['error'] = error.ADMIN_GROUP_CANNOT_BE_MODIFIED
        return body

    item = resource.db_get_item('user-group-{}'.format(group_name))
    item['session_security_enhancement'] = enabled

    success = resource.db_put_item('user_group', item, 'user-group-{}'.format(group_name))
    body['success'] = success
    return body
