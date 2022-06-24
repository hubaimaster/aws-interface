
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.util import has_partition, valid_keys


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
    },
    'output_format': {
        'partition': 'str',
    },
    'description': 'Create item and return result'
}


@NeedPermission(Permission.Run.FastDatabase.create_item)
def do(data, resource):
    body = {}
    params = data['params']

    partition = params['partition']
    item = params['item']

    # 아이템이 딕셔너리 형태가 아닌 경우
    if item is None or not isinstance(item, dict):
        raise errorlist.ITEM_MUST_BE_DICTIONARY

    # 유효한 키가 아닌 경우
    if not valid_keys(item):
        raise errorlist.KEY_CANNOT_START_WITH_UNDER_BAR

    # 파티션이 없는 경우
    if partition is None or not has_partition(resource, partition, use_cache=False):
        raise errorlist.NO_SUCH_PARTITION

    # 생성될 키가 이미 있을 경우
    if resource.fdb_has_pk_sk_by_item(item):
        raise errorlist.ITEM_PK_SK_PAIR_ALREADY_EXIST

    # 생성 정책 위반한 경우


    _id = resource.fdb_put_item(partition, item)

    body['partition'] = partition
    body['_id'] = _id
    return body
