
from cloud.response import Response
from cloud.database.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'field_name': 'str',
        'field_value': '?',
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
    field_name = params.get('field_name', None)
    field_value = params.get('field_value', None)

    item = resource.db_get_item(item_id)

    if has_write_permission(user, item):
        item[field_name] = field_value
        if field_value is None:
            item.pop(field_name)
        resource.db_update_item(item_id, item)
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
