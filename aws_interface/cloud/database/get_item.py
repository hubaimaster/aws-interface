
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy_after_get_policy_code

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creation_date': 'float',
            '...': '...'
        },
    },
    'description': 'Get item'
}


@NeedPermission(Permission.Run.Database.get_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    item = resource.db_get_item(item_id)

    if match_policy_after_get_policy_code(resource, 'read', item['partition'], user, item):
        body['item'] = item
    else:
        body['error'] = error.PERMISSION_DENIED

    return body
