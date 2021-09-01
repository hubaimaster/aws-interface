
from cloud.permission import Permission, NeedPermission, database_can_not_access_to_item
from cloud.message import error
from cloud.database.get_policy_code import match_policy_after_get_policy_code
from cloud.shortuuid import uuid
from cloud.database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item': 'dict',
        'partition': 'str',
    },
    'output_format': {
        'item_id?': 'str',
    },
    'description': 'Create item and return id of item'
}


@NeedPermission(Permission.Run.Database.create_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    if user:
        user_id = user.get('id', None)
    else:
        user_id = None

    partition = params.get('partition', None)
    item = params.get('item', {})

    item['id'] = uuid()
    if 'owner' not in item:
        item['owner'] = user_id

    item = {key: value for key, value in item.items() if value != '' and value != {} and value != []}

    # 시스템 파티션 접근 제한
    if database_can_not_access_to_item(partition):
        body['error'] = error.PERMISSION_DENIED
        return body
    # Check partition has been existed
    if resource.db_has_partition(partition):
        if match_policy_after_get_policy_code(resource, 'create', partition, user, item):
            index_keys = util.get_index_keys_to_index(resource, user, partition, 'w')
            resource.db_put_item(partition, item, item_id=item['id'], index_keys=index_keys)
            body['item_id'] = item.get('id', None)
            return body
        else:
            body['error'] = error.PERMISSION_DENIED
            return body

    body['error'] = error.NO_SUCH_PARTITION
    return body
