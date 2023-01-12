
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition, valid_keys
from cloud.fast_database.get_policy_code import match_policy, get_policy_code
from cloud.fast_database import util
from concurrent.futures import ThreadPoolExecutor


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'item_id_pairs': '{item_id: item}',
        'prevent_loss': 'bool // True일 경우 업데이트가 필요 없으면 하지 않음.',
    },
    'output_format': {
        'success_pairs': 'dict',
        'error_pairs': 'dict'
    },
    'description': 'Update items and return result'
}


@NeedPermission(Permission.Run.FastDatabase.update_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    partition = params.get('partition', None)
    item_id_pairs = params.get('item_id_pairs', None)
    prevent_loss = params.get('prevent_loss', True)  # 필요 없는 업데이트 방지

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION

    if not item_id_pairs:
        raise errorlist.ITEM_ID_PAIRS

    # 파티션이 없는 경우
    if partition is None or not has_partition(resource, partition, use_cache=True):
        raise errorlist.NO_SUCH_PARTITION

    # 아이템 쌍이 딕셔너리 형태가 아닌 경우
    if item_id_pairs is None or not isinstance(item_id_pairs, dict):
        raise errorlist.ITEM_ID_PAIRS_MUST_BE_DICTIONARY

    # 아이템 일단 다 가져오기
    old_items = resource.fdb_get_items([it_id for it_id, _ in item_id_pairs.items()], consistent_read=True)
    if not old_items:
        raise errorlist.NO_SUCH_ITEM

    # 정책 코드 가져오기
    policy_code = get_policy_code(resource, partition, 'update')

    old_items_by_id = {old_item['_id']: old_item for old_item in old_items}
    new_items_to_update = {}
    success_pairs = {}
    error_pairs = {}
    for item_id, item in item_id_pairs.items():
        try:
            # 아이템이 딕셔너리 형태가 아닌 경우
            if item is None or not isinstance(item, dict):
                raise errorlist.ITEM_MUST_BE_DICTIONARY

            # 유효한 키가 아닌 경우
            # if not valid_keys(item):
            #     raise errorlist.KEY_CANNOT_START_WITH_UNDER_BAR
            # key 가 _ 로 시작하지 않는것만 허용
            item = {
                key: value for key, value in item.items() if isinstance(key, str) and not key.startswith('_')
            }

            old_item = old_items_by_id.get(item_id, None)
            if not old_item:
                continue

            # 선언한 파티션과 다른 경우
            if old_item['_partition'] != partition:
                raise errorlist.ITEM_PARTITION_NOT_MATCH

            # 새로 생성할 것
            new_item = old_item.copy()
            # 만약 이미 같은 필드로, 업데이트가 필요 없는 경우 에러 레이즈
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
            if update_field_count == 0 and prevent_loss:
                # 업데이트할 필요가 없는 경우
                raise errorlist.ITEM_ALREADY_HAS_KEY_VALUE

            # 생성 정책 위반한 경우
            if not match_policy(policy_code, user, old_item, new_item=item):
                raise errorlist.UPDATE_POLICY_VIOLATION

            # 생성할 목록에 추가
            new_items_to_update[item_id] = new_item

        except errorlist.CloudLogicError as ex:
            error_pairs[item_id] = {
                'code': ex.code,
                'message': ex.message
            }
        except Exception as ex:
            error_pairs[item_id] = {
                'code': -1,
                'message': str(ex)
            }

    def _update(_item_id, _new_item):
        try:
            result = resource.fdb_update_item(partition, _item_id, _new_item)
            # 노출 필요 없는 키 제거
            result = util.pop_ban_keys(result)
            success_pairs[_item_id] = result
        except errorlist.CloudLogicError as _ex:
            error_pairs[_item_id] = {
                'code': _ex.code,
                'message': _ex.message
            }
        except Exception as _ex:
            error_pairs[_item_id] = {
                'code': -1,
                'message': str(_ex)
            }

    # 실제 업데이트 진행, 병렬로 작업해야 함.
    with ThreadPoolExecutor(max_workers=min(16, max(1, len(new_items_to_update)))) as worker:
        for __item_id, __new_item in new_items_to_update.items():
            # 업데이트 진행, pk, sk 겹치는 경우 에러 발생함
            worker.submit(_update, __item_id, __new_item)

    body['success_pairs'] = success_pairs
    body['errors'] = error_pairs
    return body
