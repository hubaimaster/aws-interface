
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
        'item': 'dict',
        'prevent_loss': 'bool // True일 경우 업데이트가 필요 없으면 하지 않음.'
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
    prevent_loss = params.get('prevent_loss', True)  # 필요 없는 업데이트 방지

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
    # if not valid_keys(item):
    #     raise errorlist.KEY_CANNOT_START_WITH_UNDER_BAR
    # 아이템에 있는 값 중 key 가 언더바로 시작하는건 제외
    item = {
        key: value for key, value in item.items() if isinstance(key, str) and not key.startswith('_')
    }

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
    update_field_count = 0
    for key, value in item.items():
        if key in new_item:
            if new_item[key] == value:
                # 이미 있기 때문에 update_field_count++ 하지 않음.
                new_item[key] = value
                pass
            else:
                new_item[key] = value
                update_field_count += 1
        else:
            # 키가 없으면 삽입
            new_item[key] = value
            update_field_count += 1

    # 생성 정책 위반한 경우
    if not match_policy_after_get_policy_code(resource, 'update', partition, user, old_item, new_item=item):
        raise errorlist.UPDATE_POLICY_VIOLATION

    if update_field_count == 0 and prevent_loss:
        # 업데이트할 필요가 없는 경우
        # TODO 나중에 이부분을 통해 Read 하지 않아도 업데이트로 읽을 수 있는 문제가 발생할 수 있음.
        new_item = util.pop_ban_keys(new_item)
        body['item'] = new_item
        return body

    # 업데이트 진행, pk, sk 겹치는 경우 에러 발생함
    result = resource.fdb_update_item(partition, item_id, new_item)

    # 노출 필요 없는 키 제거
    # TODO 나중에 이부분을 통해 Read 하지 않아도 업데이트로 읽을 수 있는 문제가 발생할 수 있음.
    result = util.pop_ban_keys(result)
    body['item'] = result
    return body
