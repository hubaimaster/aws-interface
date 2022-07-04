
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition, valid_keys
from cloud.fast_database.get_policy_code import match_policy_after_get_policy_code
from cloud.fast_database import util


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'item_id': 'str',
        'item': 'dict'
    },
    'output_format': {
        'item': 'dict',
    },
    'description': 'Update item and return result'
}


@NeedPermission(Permission.Run.FastDatabase.update_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    partition = params.get('partition', None)
    item_id = params.get('item_id', None)
    item = params.get('item', None)

    # 파라메터 체크 필수
    if not partition:
        raise errorlist.NEED_PARTITION

    if not item_id:
        raise errorlist.NEED_ITEM_ID

    if not item:
        raise errorlist.NEED_ITEM

    # 아이템이 딕셔너리 형태가 아닌 경우
    if item is None or not isinstance(item, dict):
        raise errorlist.ITEM_MUST_BE_DICTIONARY

    # 유효한 키가 아닌 경우
    if not valid_keys(item):
        raise errorlist.KEY_CANNOT_START_WITH_UNDER_BAR

    # 파티션이 없는 경우
    if partition is None or not has_partition(resource, partition, use_cache=True):
        raise errorlist.NO_SUCH_PARTITION

    # 아이템 없는 경우
    old_items = resource.fdb_get_items([item_id], consistent_read=True)
    if not old_items:
        raise errorlist.NO_SUCH_ITEM

    old_item = old_items[0]

    # 선언한 파티션과 다른 경우
    if old_item['_partition'] != partition:
        raise errorlist.ITEM_PARTITION_NOT_MATCH

    # 새로 생성할 것
    new_item = old_item.copy()
    for key, value in item.items():
        new_item[key] = value

    # 생성 정책 위반한 경우
    if not match_policy_after_get_policy_code(resource, 'update', partition, user, old_item, new_item=new_item):
        raise errorlist.UPDATE_POLICY_VIOLATION

    # 업데이트 진행, pk, sk 겹치는 경우 에러 발생함
    result = resource.fdb_update_item(partition, item_id, new_item)

    # 노출 필요 없는 키 제거
    result = util.pop_ban_keys(result)
    body['item'] = result
    return body
