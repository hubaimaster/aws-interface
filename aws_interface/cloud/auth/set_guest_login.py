
from cloud.response import Response
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'enabled': 'bool',
        'default_group_name': 'str',
    },
    'output_format': {

    }
}


@NeedPermission(Permission.Run.Auth.set_guest_login)
def do(data, resource):
    body = {}
    params = data['params']
    enabled = params['enabled']
    default_group_name = params['default_group_name']

    item = {
        'enabled': enabled,
        'default_group_name': default_group_name
    }

    if not resource.db_put_item('meta-info', item, 'guest_login'):
        resource.db_update_item('guest_login', item)

    return Response(body)
