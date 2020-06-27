
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy, get_policy_code
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
        'query': "[{'condition': 'eq' | 'neq' | 'in' | 'nin' | 'gt' | 'ge' | 'ls' | 'le', \
                    'option': 'or' | 'and' | None, \
                    'field': 'str', \
                    'value': 'object'}, ...]",
        'start_key': 'str',
        'limit': 'int=100',
        'reverse': 'bool=False',
        'sort_key': 'str="creation_date"'
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

    if type(start_key) is str:
        start_key = json.loads(start_key)

    # 쿼리 유효성 검사
    policy_code = get_policy_code(resource, partition, 'query')
    if not match_policy(policy_code, user, query_instructions):
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.REGISTER_POLICY_VIOLATION
        return body

    if resource.db_get_item(partition):
        items, end_key = resource.db_query(partition, query_instructions, start_key, limit, reverse, order_by=sort_key)
        policy_code = get_policy_code(resource, partition, 'read')
        filtered = []
        for item in items:
            if match_policy(policy_code, user, item):
                filtered.append(item)

        body['items'] = filtered
        body['end_key'] = end_key
        return body
    else:
        body['items'] = None
        body['end_key'] = None
        body['error'] = error.NO_SUCH_PARTITION
        return body
