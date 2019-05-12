
from cloud.response import Response
from cloud.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'function_name': 'str',
        'runtime': 'str',
        'description': 'str?',
        'zip_file': 'bytes?',
        'run_groups': 'list',
        'runnable': 'bool?',
    },
    'output_format': {
        'success': 'bool',
        'function_name': 'str?',
        'message': 'str?',
    }
}


def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    description = params.get('description', None)
    zip_file = params.get('zip_file', None)
    runtime = params.get('runtime')
    handler = params.get('handler')
    run_groups = params.get('run_groups')
    runnable = params.get('runnable', True)

    item = dict()
    item['function_name'] = function_name
    item['description'] = description
    item['handler'] = handler
    item['zip_file'] = zip_file
    item['runtime'] = runtime
    item['run_groups'] = run_groups
    item['runnable'] = runnable

    item_ids = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    if len(item_ids) == 0:
        resource.db_put_item('logic', item)
        resource.sl_create_function(function_name, runtime, handler, run_groups, zip_file)
        body['success'] = True
        body['function_name'] = function_name
        return Response(body)
    else:
        item_id = item_ids[0]
        resource.db_put_item()
        resource.db_put_item(partition, item, item_id)
        body['success'] = True
        body['function_name'] = function_name
        return Response(body)
