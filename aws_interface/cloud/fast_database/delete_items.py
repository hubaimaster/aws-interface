
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.get_policy_code import get_policy_code, match_policy
from cloud.fast_database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'item_ids': '[str]',
        'consistent_read': 'bool'
    },
    'output_format': {
        'item_ids_deleted': '[str]',
    },
    'description': 'Delete items'
}


@NeedPermission(Permission.Run.FastDatabase.delete_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_ids = params.get('item_ids', [])
    consistent_read = params.get('consistent_read', True)

    # 필수 파라메터 체크
    if not item_ids:
        raise errorlist.NEED_ITEM_IDS

    # 파라메터 속성 체크
    for item_id in item_ids:
        if not isinstance(item_id, str):
            raise errorlist.ITEM_ID_MUST_BE_STRING

    items = resource.fdb_get_items(item_ids, consistent_read=consistent_read)
    item_ids_to_delete = []
    policy_code_by_partition = {}
    for item in items:
        # 못가져온 경우 패스
        if not item:
            continue
        partition = item['_partition']
        # 등록된 파티션이 아닌경우
        if not partition or not util.has_partition(resource, partition, use_cache=True):
            raise errorlist.UNREGISTERED_PARTITION

        # 삭제 정책 검사
        if partition in policy_code_by_partition:
            policy_code = policy_code_by_partition[partition]
        else:
            policy_code = get_policy_code(resource, partition, 'delete', use_cache=True)
            policy_code_by_partition[partition] = policy_code

        # 삭제 권한 검사
        if match_policy(policy_code, user, item):
            item_ids_to_delete.append(item['_id'])

    resource.fdb_delete_items(item_ids_to_delete)
    body['item_ids_deleted'] = item_ids_to_delete
    return body
