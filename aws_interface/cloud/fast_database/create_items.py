
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition, valid_keys
from cloud.fast_database.get_policy_code import match_policy, get_policy_code
from concurrent.futures import ThreadPoolExecutor

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'items': 'list(dict)',
        'can_overwrite': 'bool'
    },
    'output_format': {
        'item_ids': 'list(str)',
        'failed_items': '[{item, error: {code, message}}]'
    },
    'description': 'Create items and return item ids'
}


@NeedPermission(Permission.Run.FastDatabase.create_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    partition = params.get('partition', None)
    items = params.get('items', [])
    can_overwrite = params.get('can_overwrite', False)

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION
    if not items:
        raise errorlist.NEED_ITEMS

    # 파티션이 없는 경우
    if partition is None or not has_partition(resource, partition, use_cache=True):
        raise errorlist.NO_SUCH_PARTITION

    policy_code = get_policy_code(resource, partition, mode='create')
    items_to_create = []

    def _can_create(_item):
        # 아이템이 딕셔너리 형태가 아닌 경우
        if _item is None or not isinstance(_item, dict):
            return errorlist.ITEM_MUST_BE_DICTIONARY, _item

        # 유효한 키가 아닌 경우
        if not valid_keys(_item):
            return errorlist.KEY_CANNOT_START_WITH_UNDER_BAR, _item

        # 생성 정책 위반한 경우
        if not match_policy(policy_code, user, _item):
            return errorlist.CREATE_POLICY_VIOLATION, _item

        # 생성될 키가 이미 있을 경우 (Networking)
        if not can_overwrite:
            if resource.fdb_has_pk_sk_by_item(partition, _item):
                return errorlist.ITEM_PK_SK_PAIR_ALREADY_EXIST, _item

        return True, _item

    futures = []
    with ThreadPoolExecutor(max_workers=max(1, len(items))) as worker:
        for item in items:
            future = worker.submit(_can_create, item)
            futures.append(future)

    fail_list = []
    for future in futures:
        status, item = future.result()
        if status is True:
            items_to_create.append(item)
        else:
            fail_list.append({
                'item': item,
                'error': {
                    'code': status.code,
                    'message': status.message
                }
            })

    _ids = resource.fdb_put_items(partition, items_to_create)

    body['item_ids'] = _ids
    body['failed_items'] = fail_list
    return body
