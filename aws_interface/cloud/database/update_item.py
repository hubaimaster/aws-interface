
from cloud.response import Response
from cloud.database.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'item': 'map',
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    new_item = params.get('item', {})
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    new_item['read_groups'] = read_groups
    new_item['write_groups'] = write_groups

    item = resource.db_get_item(item_id)

    if has_write_permission(user, item):
        resource.db_update_item(item_id, new_item)
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
