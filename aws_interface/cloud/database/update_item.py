
from cloud.response import Response
from cloud.permission import has_write_permission, database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.message import Error

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
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Database.update_item)
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
    if database_can_not_access_to_item(item):
        body['error'] = Error.no_such_partition
        return Response(body)

    if has_write_permission(user, item):
        resource.db_update_item(item_id, new_item)
    else:
        body['error'] = Error.no_such_partition
    return Response(body)
