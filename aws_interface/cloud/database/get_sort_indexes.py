from cloud.permission import Permission, NeedPermission
from cloud.message import error


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'items': '[{"sort_key": str, "sort_key_type": "N" | "S"}, ...]',
        'success': 'bool',
    },
    'description': 'Create sort index and return result'
}

# Created when system was built
DEFAULT_SORT_KEY = 'creation_date'


@NeedPermission(Permission.Run.Database.get_sort_indexes)
def do(data, resource):
    partition = 'sort_key'
    body = {}
    params = data['params']
    items = []
    items, start_key = resource.db_query(partition, [], limit=10000)
    while start_key:
        items, start_key = resource.db_query(partition, [], limit=10000, start_key=start_key)

    if not list(filter(lambda x: x['sort_key'] == DEFAULT_SORT_KEY, items)):
        items.append({
            'sort_key': 'creation_date',
            'sort_key_type': 'N'
        })
    body['success'] = True
    body['items'] = items
    return body
