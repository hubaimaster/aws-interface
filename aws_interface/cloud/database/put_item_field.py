
from cloud.response import Response
from cloud.permission import has_write_permission, database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'field_name': 'str',
        'field_value?': 'any',
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Database.put_item_field)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    field_name = params.get('field_name', None)
    field_value = params.get('field_value', None)

    item = resource.db_get_item(item_id)
    if database_can_not_access_to_item(item):
        body['error'] = error.PERMISSION_DENIED
        return Response(body)

    if has_write_permission(user, item):
        item[field_name] = field_value
        if field_value is None:
            item.pop(field_name)
        resource.db_update_item(item_id, item)
    else:
        body['error'] = error.PERMISSION_DENIED
    return Response(body)
