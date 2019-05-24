
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import Error
import json

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'test_name': 'str',
        'function_name': 'str',
        'test_input': 'dict',
    },
    'output_format': {
        'test_name?': 'str',
        'error?': {
            'code': 'int',
            'message': 'str',
        },
    }
}


@NeedPermission(Permission.Run.Logic.create_function_test)
def do(data, resource):
    partition = 'logic-function-test'
    body = {}
    params = data['params']

    test_name = params.get('test_name')
    function_name = params.get('function_name')
    test_input = params.get('test_input')
    if isinstance(test_input, dict):
        test_input = json.dumps(test_input)

    item = dict()
    item['test_name'] = test_name
    item['function_name'] = function_name
    item['test_input'] = test_input

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'test_name', test_name)
    if len(item_ids) == 0:
        resource.db_put_item(partition, item)
        body['test_name'] = test_name
        return Response(body)
    else:
        body['error'] = Error.existing_function
        return Response(body)
