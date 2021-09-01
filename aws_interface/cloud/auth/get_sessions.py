
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str',
        'query': 'list?'
    },
    'output_format': {
        'items': [{'str': 'any'}],
        'end_key': 'str'
    },
    'description': 'Return sessions'
}


@NeedPermission(Permission.Run.Auth.get_sessions)
def do(data, resource):
    body = {}
    params = data['params']
    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    partition = 'session'
    query = params.get('query', [])
    reverse = params.get('reverse', True)

    items, end_key = resource.db_query(partition, query, start_key, limit, reverse)
    # items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit, reverse=True)
    body['items'] = items
    body['end_key'] = end_key
    return body
