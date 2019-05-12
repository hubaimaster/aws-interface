
from cloud.response import Response
from cloud.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'function_name': 'str',
    },
    'output_format': {
        'item': 'dict',
        'message:': 'str?',
    }
}


def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')

    item_ids = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    if len(item_ids) == 0:
        body['message'] = 'function_name: {} did not exist'.format(function_name)
        return Response(body)
    else:
        item = resource.db_get_item(item_ids[0])
        body['item'] = item
        return Response(body)
