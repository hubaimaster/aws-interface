
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'items': 'list',
        'end_key': 'str',
    },
    'description': 'Return function test list'
}


@NeedPermission(Permission.Run.Logic.get_function_tests)
def do(data, resource):
    partition = 'logic-function-test'
    body = {}
    params = data['params']

    start_key = None
    limit = 1000

    items = []
    while True:
        _items, end_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit)
        items.extend(_items)
        start_key = end_key
        if not start_key:
            break

    body['items'] = items
    body['end_key'] = end_key
    return body
