
from cloud.response import Response
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
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        },
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
        body['error'] = error.NO_SUCH_PARTITION
        return Response(body)

    if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item):
        # 새로운 필드에 없는 값은 이전 아이템에 있는값을 넣어줌
        for key in item:
            if key not in new_item:
                new_item[key] = item[key]
        # value 가 None 이면 필드에서 제거
        for key, value in new_item.items():
            if value is None:
                new_item.pop(key)
        resource.db_update_item(item_id, new_item)
    else:
        body['error'] = error.NO_SUCH_PARTITION
    return Response(body)
