
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
    },
    'output_format': {
        'item': {
            'function_name': 'str',
            'runtime': 'str',
            'handler': 'str',
            'description': 'str',
            'zip_file_id': 'str',
            'runnable': 'bool',
            'sdk_config': {
                'rest_api_url': 'str',
                'session_id': 'str',
            }
        },
    },
    'description': 'Return function item'
}


@NeedPermission(Permission.Run.Logic.get_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')

    items, _ = resource.db_query(partition,
                                 [{'option': None, 'field': 'function_name', 'value': function_name,
                                   'condition': 'eq'}])

    if len(items) == 0:
        body['error'] = error.NO_SUCH_FUNCTION
        return body
    else:
        body['item'] = items[0]
        return body
