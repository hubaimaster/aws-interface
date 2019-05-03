
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'enabled': 'bool',
        'default_group_name': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    enabled = params['enabled']
    default_group_name = params['default_group_name']

    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    item = {
        'enabled': enabled,
        'default_group_name': default_group_name
    }

    if not resource.db_put_item('meta-info', item, 'email_login'):
        resource.db_update_item('email_login', item)

    body['success'] = True
    return Response(body)
