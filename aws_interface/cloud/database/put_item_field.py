
from cloud.permission import database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy_after_get_policy_code
from cloud.database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'field_name': 'str',
        'field_value': 'any',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Put field:value to item'
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
        return body

    if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item):
        item[field_name] = field_value
        if field_value is None:
            item.pop(field_name)
        index_keys = util.get_index_keys_to_index(resource, user, item['partition'])
        success = resource.db_update_item(item_id, item, index_keys=index_keys)
        body['success'] = success
    else:
        body['error'] = error.PERMISSION_DENIED
    return body
