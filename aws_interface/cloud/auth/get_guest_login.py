
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {

    }
}


def do(data, resource):
    body = {}
    params = data['params']

    item = resource.db_get_item('guest_login')
    if not item:
        item = {
            'enabled': True,
            'default_group_name': 'user'
        }
        resource.db_put_item('meta-info', item, 'guest_login')

    body['item'] = item
    return Response(body)
