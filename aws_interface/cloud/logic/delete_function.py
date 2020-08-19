
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
    },
    'output_format': {
        'success': 'bool'
    }
}


@NeedPermission(Permission.Run.Logic.delete_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    function_version = params.get('function_version', None)

    query = [{'option': None, 'field': 'function_name', 'value': function_name, 'condition': 'eq'}]
    items, _ = resource.db_query(partition, query, reverse=True)
    for item in items:
        if item.get('function_version', None) == function_version:
            success = resource.db_delete_item(item['id'])
            body['success'] = success

    return body
