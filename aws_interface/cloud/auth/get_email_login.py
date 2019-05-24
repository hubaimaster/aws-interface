
from cloud.response import Response
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'item': {
            'enabled': 'bool',
            'default_group_name': 'str'
        },
    }
}


def do(data, resource):
    body = {}
    params = data['params']

    item = resource.db_get_item('email_login')
    if not item:
        item = {
            'enabled': True,
            'default_group_name': 'user'
        }
        resource.db_put_item('meta-info', item, 'email_login')

    body['item'] = item
    return Response(body)
