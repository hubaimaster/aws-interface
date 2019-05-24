
from cloud.response import Response
from cloud.permission import has_write_permission
from cloud.permission import Permission, NeedPermission
from cloud.message import Error
from cloud.shortuuid import uuid
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'function_name': 'str',
        'runtime': 'str',
        'description?': 'str',
        'zip_file?': 'bytes',
        'run_groups': 'list',
        'runnable?': 'bool',
    },
    'output_format': {
        'function_name?': 'str',
        'error?': {
            'code': 'int',
            'message': 'str',
        },
    }
}


@NeedPermission(Permission.Run.Logic.update_function)
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

    zip_file_id = uuid()

    item = dict()
    item['function_name'] = function_name
    item['description'] = description
    item['handler'] = handler
    item['runtime'] = runtime
    item['run_groups'] = run_groups
    item['runnable'] = runnable
    item['zip_file_id'] = zip_file_id

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    if len(item_ids) == 0:
        body['error'] = Error.no_such_function
    else:
        zip_file_b64 = zip_file.encode('utf-8')
        zip_file_b64 = base64.b64decode(zip_file_b64)
        resource.file_upload_bin(zip_file_id, zip_file_b64)
        resource.db_put_item(partition, item, item_ids[0])
        body['function_name'] = function_name
        return Response(body)
