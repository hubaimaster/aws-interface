
from cloud.permission import database_can_not_access_to_item
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
        'success': 'bool'
    },
    'description': 'Delete item'
}


@NeedPermission(Permission.Run.Database.delete_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)

    item = resource.db_get_item(item_id)
    if item is None:
        body['error'] = error.NO_SUCH_ITEM
        return body

    # 시스템 파티션 제한
    if database_can_not_access_to_item(item['partition']):
        body['error'] = error.PERMISSION_DENIED
        return body

    # 등록된 파티션이 아닌경우
    if not resource.db_has_partition(item['partition']):
        body['item'] = None
        body['error'] = error.UNREGISTERED_PARTITION
        return body

    if match_policy_after_get_policy_code(resource, 'delete', item['partition'], user, item):
        success = resource.db_delete_item(item_id)
        body['success'] = success
    else:
        body['message'] = error.PERMISSION_DENIED
    return body
