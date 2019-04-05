
from cloud.response import Response
from cloud.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': 'list',
    },
    'output_format': {
        'success': 'bool',
        'message': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    success = True

    item_ids = params.get('item_ids', [])
    for item_id in item_ids:
        item = resource.db_get_item(item_id)
        if item and has_write_permission(user, item):
            resource.db_delete_item(item_id)
            success &= True
        else:
            success &= False
    if not success:
        body['message'] = 'permission denied'
    body['success'] = success
    return Response(body)
