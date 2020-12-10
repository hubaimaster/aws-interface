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
                " \"info_user_id\": \"user\", ...}"
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

    if resource.db_get_item(partition):
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

        body['items'] = filtered
        body['end_key'] = end_key
        return body
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.NO_SUCH_PARTITION
        return body
