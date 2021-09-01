from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.database import util
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'query': "[{\"condition\": \"eq\" | \"neq\" | \"in\" | \"nin\" | \"gt\" | \"ge\" | \"ls\" | \"le\", \
                    \"option\": \"or\" | \"and\" | None, \
                    \"field\": \"str\", \
                    \"value\": \"object\"}, ...]",
        'start_key': 'str',
        'limit': 'int=100',
        'reverse': 'bool=False',
        'sort_key': 'str="creation_date"',
        'join': "{\"user_id\": \"user\", "
                " \"info.user_id\": \"info.user\","
                " \"info_user_id\": \"user\", ...}",
        'projection_keys': 'list',
    },
    'output_format': {
        'items?': [
            {
                'id': 'str',
                'creation_date': 'float',
                '...': '...',
            }
        ],
        'end_key?': 'str',
    },
    'description': 'Query items'
}

DEFAULT_SORT_KEY = 'creation_date'


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


@NeedPermission(Permission.Run.Database.query_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    partition = params.get('partition', None)
    query_instructions = params.get('query', [])
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    reverse = params.get('reverse', False)
    sort_key = params.get('sort_key', DEFAULT_SORT_KEY)
    join = params.get('join', {})
    projection_keys = params.get('projection_keys', None)

    if type(start_key) is str:
        start_key = json.loads(start_key)

    # 쿼리 유효성 검사
    policy_code = get_policy_code(resource, partition, 'query')
    if not match_policy(policy_code, user, query_instructions):
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.QUERY_POLICY_VIOLATION
        return body

    # Join 유효성 검사
    policy_code = get_policy_code(resource, partition, 'join')
    if not match_policy(policy_code, user, join):
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.JOIN_POLICY_VIOLATION
        return body

    if resource.db_has_partition(partition):
        index_keys = util.get_index_keys_to_index(resource, user, partition, 'r')
        items, end_key = resource.db_query(partition, query_instructions, start_key, limit,
                                           reverse, order_by=sort_key, index_keys=index_keys)
        policy_code = get_policy_code(resource, partition, 'read')
        filtered = []
        for item in items:
            if match_policy(policy_code, user, item):
                filtered.append(item)

        if join:
            util.join_items(resource, user, filtered, join)

        items = [filter_projection_keys(item, projection_keys) for item in filtered]
        body['items'] = items
        body['end_key'] = end_key
        return body
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.NO_SUCH_PARTITION
        return body
