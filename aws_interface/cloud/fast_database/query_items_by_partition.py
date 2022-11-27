import json

from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist
from cloud.fast_database.get_policy_code import match_policy, get_policy_code
from cloud.fast_database import util
from resource import util as resource_util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'pk_field': 'str',
        'pk_value': 'str',
        'sk_field': 'str?',
        'sk_condition': 'str?',
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
        'max_scan_rep': 'int?',
        'start_key': 'str?',
        'limit': 'int',
        'reverse': 'bool',
        'consistent_read': 'bool',

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


def _find_proper_index_name(partition_object, pk_field, sk_field=None):
    """
    적절한 index 를 찾아 반환합니다.
    sk_field 가 None 인 경우에는 pk_field 가 일치하는 가장 빠른 인덱스를 반환합니다.
    sk_field 가 존재하는 경우 엄격하게 탐색해야합니다.
    :param partition_object:
    :param pk_field:
    :param sk_field:
    :return:
    """
    index_name = None
    pk_name = '_pk'
    sk_name = '_sk'
    if sk_field:
        # 엄격하게 탐색
        # 메인 파티션 먼저 검색
        if pk_field == partition_object['_pk_field'] and sk_field == partition_object['_sk_field']:
            index_name = None
        else:
            indexes = partition_object.get('indexes', [])
            for index in indexes:
                if pk_field == index['_pk_field'] and sk_field == index['_sk_field']:
                    # 완벽히 일치하면
                    index_name = index['index_name']
                    pk_name = index['pk_name']
                    sk_name = index['sk_name']
                    break
            if not index_name:
                # 인덱스가 안나올 경우, 매치되는게 없는 경우라..
                message = f'pk_field & sk_field pair must be one of \n'
                message += f"0. pk: <{partition_object['_pk_field']}> & sk: <{partition_object['_sk_field']}>\n"
                field_pairs = [f"{idx + 1}. pk: <{index['_pk_field']}> & sk: <{index['_sk_field']}>" for idx, index in enumerate(indexes)]
                message += '\n'.join(field_pairs)
                raise errorlist.CloudLogicError(-1, message)

    else:  # sk_field 없어도 pk_field 가 일치하면 우선 반환
        if pk_field == partition_object['_pk_field']:
            index_name = None
        else:
            indexes = partition_object.get('indexes', [])
            for index in indexes:
                if pk_field == index['_pk_field']:
                    # 완벽히 일치하면
                    index_name = index['index_name']
                    pk_name = index['pk_name']
                    sk_name = index['sk_name']
                    break
    return index_name, pk_name, sk_name


@NeedPermission(Permission.Run.FastDatabase.query_items)  # query_items 와 동일 기능이라 권한이 같음.
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    partition = params.get('partition', None)
    pk_field = params.get('pk_field', None)
    sk_field = params.get('sk_field', None)
    pk_value = params.get('pk_value', None)

    # 필수 파라메터 체크
    if not partition:
        raise errorlist.NEED_PARTITION

    # pk_field, value 없으면 partiton 으로 대체합니다.
    if not pk_field:
        # raise errorlist.NEED_PK_FIELD
        pk_field = '_partition'

    if not pk_value:
        # raise errorlist.NEED_PK_VALUE
        pk_value = partition

    sort_condition = params.get('sk_condition', None)  # 인지하기 쉽게 이름 변경함
    sk_value = params.get('sk_value', None)
    sk_second_value = params.get('sk_second_value', None)

    # 차례대로 위의 변수들이 먼저 할당되어야 쿼리할 수 있음.
    if sk_value is not None and sk_field is None:
        raise errorlist.NEED_SK_FIELD

    if sk_value is not None and sort_condition is None:
        raise errorlist.NEED_SK_CONDITION

    if sk_second_value is not None and sk_value is None:
        raise errorlist.NEED_SK_VALUE

    # sk_group 이 실제 파티션 중에 존재하는 값인지 체크, 실수 방지 차원임.
    current_partitions = resource.fdb_get_partitions(use_cache=True)
    partition_object = None

    for current_partition in current_partitions:
        _partition_name = current_partition.get('_partition_name', None)
        if _partition_name == partition:
            partition_object = current_partition

    # 존재하는 파티션인지 확인
    if partition_object is None:
        raise errorlist.NO_SUCH_PARTITION

    # 요청한 필드 값들과, 실제 파티션에서 가지고 있는 값들이 매칭되는지 확인하기
    # 이 값을 기준으로 인덱스를 타게할 수 있음.
    # 파티션이나 인덱스를 다 뒤져도 맞는게 없으면 에러 레이즈
    index_name, pk_name, sk_name = _find_proper_index_name(partition_object, pk_field, sk_field)

    filters = params.get('filters', [])
    max_scan_rep = params.get('max_scan_rep', 1)
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)

    consistent_read = params.get('consistent_read', True)

    projection_keys = params.get('projection_keys', None)

    # start_key json 변환
    if type(start_key) is str:
        # start_key_pk, start_key_sk = resource_util.split_pk_sk(start_key)
        start_key = json.loads(start_key)

    # 최대 스캔 횟수가 있을시 반복
    scan_rep_count = 0
    if not max_scan_rep:
        max_scan_rep = 1
    items = []
    end_key = start_key

    while scan_rep_count < max_scan_rep:
        _items, end_key = resource.fdb_query_items(
            pk_field=pk_field, pk_value=pk_value,
            sort_condition=sort_condition, partition=partition,
            sk_field=sk_field, sk_value=sk_value, sk_second_value=sk_second_value,
            start_key=end_key, filters=filters, limit=limit, reverse=reverse,
            consistent_read=consistent_read, index_name=index_name, pk_name=pk_name, sk_name=sk_name
        )
        scan_rep_count += 1
        items.extend(_items)
        if len(items) >= limit:
            break  # limit 보다 많은 경우 바로 리턴
        if not end_key:
            break

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
        else:
            body['error'] = errorlist.PART_OF_ITEMS_READ_POLICY_VIOLATION.to_dict()

    filtered = [filter_projection_keys(item, projection_keys) for item in filtered]
    if end_key:
        # end_key = resource_util.merge_pk_sk(end_key[pk_name], end_key[sk_name])
        end_key = json.dumps(end_key)

    filtered = [util.pop_ban_keys(item) for item in filtered]
    body['items'] = filtered
    body['end_key'] = end_key
    return body
