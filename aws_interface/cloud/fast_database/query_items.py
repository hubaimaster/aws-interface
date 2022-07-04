from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.get_policy_code import match_policy, get_policy_code
from cloud.fast_database import util
from resource import util as resource_util
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'pk_group': 'str',
        'pk_field': 'str',
        'pk_value': 'str',
        'sort_condition': 'str?',

        'sk_group': 'str?',
        'partition': 'str?',
        'sk_field': 'str?',
        'sk_value': 'str?',
        'sk_second_value': 'str?',

        'filters': "[ \
                            { \
                                'field': 'str', \
                                'value': 'str', \
                                'second_value': 'str?', \
                                'condition': 'eq' | 'neq' | 'lte' | 'lt' | 'gte' | 'gt' | 'btw' | 'stw' | \
                                             'is_in' | 'contains' | 'exist' | 'not_exist' \
                            } \
                    ]",
        'start_key': 'str?',
        'limit': 'int',
        'reverse': 'bool',
        'consistent_read': 'bool',
        'index_name': 'str?',

        'projection_keys': '[str]'
    },
    'output_format': {
        'items?': [
            {
                '_id': 'str',
                '_created_at': 'float',
                '_partition': 'str',
                '...': '...'
            }
        ],
        'end_key?': 'str',
    },
    'description': 'Query items'
}


def filter_projection_keys(item, projection_keys):
    """
    projection_keys 에 표현된 키만 필터링합니다.
    :param item:
    :param projection_keys:
    :return:
    """
    if projection_keys is None or not isinstance(projection_keys, list):
        return item
    new_item = {}
    projection_keys.extend(['id', 'partition', 'creation_date'])
    for projection_key in projection_keys:
        if projection_key in item:
            new_item[projection_key] = item.get(projection_key, None)
    return new_item


@NeedPermission(Permission.Run.FastDatabase.query_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    pk_group = params.get('pk_group', None)
    pk_field = params.get('pk_field', None)
    pk_value = params.get('pk_value', None)

    # 필수 파라메터 체크
    if not pk_group:
        raise errorlist.NEED_PK_GROUP

    if not pk_field:
        raise errorlist.NEED_PK_FIELD

    if not pk_value:
        raise errorlist.NEED_PK_VALUE

    # 시스템 내부에서 사용하는 group 에 cloud 로직단에서 접근할 수 없음.
    if not util.valid_pk_group(pk_group):
        raise errorlist.INVALID_PK_GROUP

    sort_condition = params.get('sort_condition', None)
    sk_group = params.get('sk_group', None)
    partition = params.get('partition', None)
    sk_field = params.get('sk_field', None)
    sk_value = params.get('sk_value', None)
    sk_second_value = params.get('sk_second_value', None)

    # 차례대로 위의 변수들이 먼저 할당되어야 쿼리할 수 있음.
    if sk_group is not None and sort_condition is None:
        raise errorlist.NEED_SORT_CONDITION

    if partition is not None and sk_group is None:
        raise errorlist.NEED_SK_GROUP

    if sk_field is not None and partition is None:
        raise errorlist.NEED_PARTITION

    if sk_value is not None and sk_field is None:
        raise errorlist.NEED_SK_FIELD

    if sk_second_value is not None and sk_value is None:
        raise errorlist.NEED_SK_VALUE

    # sk_group 이 실제 파티션 중에 존재하는 값인지 체크, 실수 방지 차원임.
    current_partitions = resource.fdb_get_partitions(use_cache=True)
    available_sk_groups = [current_partition.get('_sk_group', None) for current_partition in current_partitions]
    if sk_group and sk_group not in available_sk_groups:
        raise Exception(f'<sk_group> must be one of {available_sk_groups}')

    # 존재하는 파티션인지 확인
    if partition and not util.has_partition(resource, partition, use_cache=True):
        raise errorlist.NO_SUCH_PARTITION

    # sk_field 가 실제 파티션 중에 존재하는 값인지 체크, 실수 방지 차원임.
    can_use_sk_field = False
    partition_sk_field = None  # 파티션에서 정해진 sk_field, 고정이지만 변수로 받음.
    if sk_field:
        for current_partition in current_partitions:
            _partition_name = current_partition.get('_partition_name', None)
            _sk_field = current_partition.get('_sk_field', None)
            # sk_field 가 존재했을때는 partition 도 무조건 있음.
            if _partition_name == partition:
                partition_sk_field = _sk_field
                # 두개가 같은게 있으면 통과.
                if _sk_field == sk_field:
                    can_use_sk_field = True
    else:  # sk_field 가 안왔으면 어차피 사용이 안됨. 즉 없거나 있는게 오거나 둘 중 하나임.
        can_use_sk_field = True

    if not can_use_sk_field:
        raise errorlist.CloudLogicError(
            10001, f'<sk_field> should be [{partition_sk_field}]'
        )

    filters = params.get('filters', [])
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    consistent_read = params.get('consistent_read', False)
    index_name = params.get('index_name', None)

    projection_keys = params.get('projection_keys', None)

    # 파티션 존재 체크하지 않아도 됨. 쿼리는 조인 가능한 설계를 가지고 있음. (조인은 아니지만 동등한 효과)

    # start_key json 변환
    if type(start_key) is str:
        start_key_pk, start_key_sk = resource_util.split_pk_sk(start_key)
        start_key = {
            '_pk': start_key_pk,
            '_sk': start_key_sk,
        }

    items, end_key = resource.fdb_query_items(
        pk_group=pk_group, pk_field=pk_field, pk_value=pk_value,
        sort_condition=sort_condition, sk_group=sk_group, partition=partition,
        sk_field=sk_field, sk_value=sk_value, sk_second_value=sk_second_value,
        start_key=start_key, filters=filters, limit=limit, reverse=reverse,
        consistent_read=consistent_read, index_name=index_name,
    )
    policy_code_by_partition = {}
    filtered = []
    items = [item for item in items if item.get('_id', None) and item.get('_partition', None)]

    # 권한에 맞는 아이템만 노출
    for item in items:
        # 읽기 정책 검사
        item_partition = item['_partition']
        if item_partition in policy_code_by_partition:
            policy_code = policy_code_by_partition[item_partition]
        else:
            policy_code = get_policy_code(resource, item_partition, 'read', use_cache=True)
            policy_code_by_partition[item_partition] = policy_code

        if match_policy(policy_code, user, item):
            filtered.append(item)

    filtered = [filter_projection_keys(item, projection_keys) for item in filtered]
    filtered = [util.pop_ban_keys(item) for item in filtered]
    if end_key:
        end_key = resource_util.merge_pk_sk(end_key['_pk'], end_key['_sk'])
    body['items'] = filtered
    body['end_key'] = end_key
    return body
