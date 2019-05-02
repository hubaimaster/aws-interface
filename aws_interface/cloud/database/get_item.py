
from cloud.response import Response
from cloud.util import has_read_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'item': 'map',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    item = resource.db_get_item(item_id)

    if has_read_permission(user, item):
        body['item'] = item
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
