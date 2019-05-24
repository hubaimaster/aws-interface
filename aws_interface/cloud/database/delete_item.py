
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
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Database.delete_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)

    item = resource.db_get_item(item_id)
    if database_can_not_access_to_item(item):
        body['error'] = Error.permission_denied
        return Response(body)

    if has_write_permission(user, item):
        resource.db_delete_item(item_id)
    else:
        body['message'] = Error.permission_denied
    return Response(body)
