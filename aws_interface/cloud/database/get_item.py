
from cloud.response import Response
from cloud.permission import has_read_permission
from cloud.permission import Permission, NeedPermission
from cloud.message import Error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'item': 'map',
        'error': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Database.get_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    item = resource.db_get_item(item_id)

    if has_read_permission(user, item):
        body['item'] = item
    else:
        body['error'] = Error.permission_denied

    return Response(body)
