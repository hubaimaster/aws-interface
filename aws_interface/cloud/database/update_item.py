
from cloud.permission import database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.database.get_policy_code import match_policy_after_get_policy_code
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'item': 'map',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Update item'
}


@NeedPermission(Permission.Run.Database.update_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    new_item = params.get('item', {})

    item = resource.db_get_item(item_id)
    if database_can_not_access_to_item(item):
        body['error'] = error.NO_SUCH_PARTITION
        return body

    if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item):
        # Put the value in the previous item that is not in the new field
        for key in item:
            if key not in new_item:
                new_item[key] = item[key]
        # Remove field if value is None
        for key, value in new_item.copy().items():
            if value is None:
                new_item.pop(key)

        new_item = {key: value for key, value in new_item.items() if value or value is False}
        success = resource.db_update_item(item_id, new_item)
        body['success'] = success
    else:
        body['error'] = error.NO_SUCH_PARTITION
    return body
