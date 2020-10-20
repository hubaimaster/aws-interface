
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str?',
        'limit': 'int?=1000',
        'reverse': 'bool?=True'
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str?'
    },
    'description': 'Create trigger [System will call function when <module_name> invoked.]'
}


@NeedPermission(Permission.Run.Trigger.get_triggers)
def do(data, resource):
    partition = 'trigger'
    body = {}
    params = data['params']
    start_key = params.get('start_key', None)
    limit = params.get('limit', 1000)
    reverse = params.get('reverse', True)
    items = []
    while True:
        _items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit, reverse=reverse)
        items.extend(_items)
        start_key = end_key
        if not start_key:
            break

    body['items'] = items
    body['end_key'] = end_key
    return body
