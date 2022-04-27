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
    # 시스템 파티션 접근 제한
    if database_can_not_access_to_item(item['partition']):
        body['error'] = error.PERMISSION_DENIED
        return body
    if not resource.db_has_partition(item['partition']):
        body['error'] = error.NO_SUCH_PARTITION
        return body

    new_item = {
        'id': item_id,
        field_name: field_value,
        'partition': item['partition'],
        'creation_date': item.get('creation_date', 0)
    }

    if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item, new_item=new_item):
        index_keys = util.get_index_keys_to_index(resource, user, item['partition'], 'w')

        # 소트키는 무조건 업데이트시 포함해야함.
        sort_keys = util.get_sort_keys(resource)
        for sort_key in sort_keys:
            s_key = sort_key.get('sort_key', None)
            if s_key and s_key not in new_item and item.get(s_key, None) is not None:
                new_item[s_key] = item.get(s_key, None)

        success = resource.db_update_item_v2(item_id, new_item, index_keys=index_keys, sort_keys=sort_keys)
        body['success'] = success
    else:
        body['error'] = error.PERMISSION_DENIED
    return body
