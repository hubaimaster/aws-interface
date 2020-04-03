
from cloud.permission import Permission, NeedPermission
from cloud.message import error


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'sort_key': 'str',
        'sort_key_type': "'N' | 'S'"
    },
    'output_format': {
        'result': 'dict?',
        'success': 'bool',
        'error': 'dict?',
    },
    'description': 'Create sort index and return result'
}


@NeedPermission(Permission.Run.Database.create_sort_index)
def do(data, resource):
    partition = 'sort_key'
    body = {}
    params = data['params']

    sort_key = params.get('sort_key')
    sort_key_type = params.get('sort_key_type')

    items, _ = resource.db_query(partition, [
        {'condition': 'eq',
         'option': 'or',
         'field': 'sort_key',
         'value': sort_key}
    ])
    if items:
        body['success'] = False
        body['error'] = error.EXISTING_SORT_KEY
        return body

    result = resource.db_create_sort_index(sort_key, sort_key_type)
    if result:
        item = {
            'sort_key': sort_key,
            'sort_key_type': sort_key_type
        }
        resource.db_put_item(partition, item)

    body['result'] = result
    body['success'] = True
    return body
