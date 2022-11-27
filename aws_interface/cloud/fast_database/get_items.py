
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.get_policy_code import get_policy_code, match_policy
from cloud.fast_database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': '[str]',
        'consistent_read': 'bool',
    },
    'output_format': {
        'items': [{
            '_id': 'str',
            '_created_at': 'int',
            '_partition': 'str',
            '...': '...'
        }],
    },
    'description': 'Get items, If more than one items have policy violation, None type objects will return.'
}


@NeedPermission(Permission.Run.FastDatabase.get_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_ids = params.get('item_ids', [])
    consistent_read = params.get('consistent_read', True)

    # 필수 파라메터 체크
    if not item_ids:
        raise errorlist.NEED_ITEM_IDS

    items = resource.fdb_get_items(item_ids, consistent_read=consistent_read)
    items_to_return = []
    policy_code_by_partition = {}
    for item in items:
        partition = item['_partition']
        # 등록된 파티션이 아닌경우
        if not partition or not util.has_partition(resource, partition, use_cache=True):
            raise errorlist.UNREGISTERED_PARTITION

        # 읽기 정책 검사
        if partition in policy_code_by_partition:
            policy_code = policy_code_by_partition[partition]
        else:
            policy_code = get_policy_code(resource, partition, 'read', use_cache=True)
            policy_code_by_partition[partition] = policy_code

        # 노출 필요 없는 키 제거
        item = util.pop_ban_keys(item)

        # 읽기 권한 검사
        if match_policy(policy_code, user, item):
            items_to_return.append(item)
        else:
            items_to_return.append(None)

    body['items'] = items_to_return
    return body
