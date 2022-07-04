
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.get_policy_code import match_policy_after_get_policy_code
from cloud.fast_database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'item_id': 'str',
        'consistent_read': 'bool'
    },
    'output_format': {
        'item': {
            '_id': 'str',
            '_created_at': 'int',
            '_partition': 'str',
            '...': '...'
        },
    },
    'description': 'Get item'
}


@NeedPermission(Permission.Run.FastDatabase.get_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    consistent_read = params.get('consistent_read', False)

    # 필수 파라메터 체크
    if not item_id:
        raise errorlist.NEED_ITEM_ID

    items = resource.fdb_get_items([item_id], consistent_read=consistent_read)

    # No Item
    if not items:
        raise errorlist.NO_SUCH_ITEM

    item = items[0]
    partition = item['_partition']
    # 등록된 파티션이 아닌경우
    if not partition or not util.has_partition(resource, partition, use_cache=True):
        raise errorlist.UNREGISTERED_PARTITION

    # 필요 없는 키 지우기
    item = util.pop_ban_keys(item)

    # 읽기 권한 검사
    if match_policy_after_get_policy_code(resource, 'read', partition, user, item):
        body['item'] = item
        return body
    else:
        raise errorlist.READ_POLICY_VIOLATION
