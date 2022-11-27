
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition, valid_keys, pop_ban_keys
from cloud.fast_database.get_policy_code import match_policy_after_get_policy_code


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'item': 'dict',
        'can_overwrite': 'bool'
    },
    'output_format': {
        'item_id': 'str',
    },
    'description': 'Create item and return result'
}


@NeedPermission(Permission.Run.FastDatabase.create_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    partition = params.get('partition', None)
    item = params.get('item', None)
    can_overwrite = params.get('can_overwrite', False)
    return_item = params.get('return_item', False)

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION
    if not item:
        raise errorlist.NEED_ITEM

    # 아이템이 딕셔너리 형태가 아닌 경우
    if item is None or not isinstance(item, dict):
        raise errorlist.ITEM_MUST_BE_DICTIONARY

    # 유효한 키가 아닌 경우
    # if not valid_keys(item):
    #     raise errorlist.KEY_CANNOT_START_WITH_UNDER_BAR
    item = {
        key: value for key, value in item.items() if isinstance(key, str) and not key.startswith('_')
    }

    # 파티션이 없는 경우
    if partition is None or not has_partition(resource, partition, use_cache=True):
        raise errorlist.NO_SUCH_PARTITION

    # 생성 정책 위반한 경우
    if not match_policy_after_get_policy_code(resource, 'create', partition, user, item):
        raise errorlist.CREATE_POLICY_VIOLATION

    # 생성될 키가 이미 있을 경우
    if not can_overwrite:
        if resource.fdb_has_pk_sk_by_item(partition, item):
            raise errorlist.ITEM_PK_SK_PAIR_ALREADY_EXIST

    item = resource.fdb_put_item(partition, item)

    body['partition'] = partition
    body['item_id'] = item['_id']
    if return_item:
        item = pop_ban_keys(item)
        body['item'] = item
    return body


if __name__ == '__main__':
    pass