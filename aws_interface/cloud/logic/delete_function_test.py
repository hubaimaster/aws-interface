
from cloud.response import Response
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'test_name': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


@NeedPermission(Permission.Run.Logic.delete_function_test)
def do(data, resource):
    partition = 'logic-function-test'
    body = {}
    params = data['params']

    test_name = params.get('test_name')
    items, _ = resource.db_query(partition, [{'option': None, 'field': 'test_name', 'value': test_name, 'condition': 'eq'}])
    for item in items:
        success = resource.db_delete_item(item['id'])
        body['success'] = success
    return Response(body)
