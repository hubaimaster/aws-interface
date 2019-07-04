
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'runtime?': 'str',
        'description?': 'str',
        'zip_file?': 'bytes',
        'run_groups?': 'list',
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
    runtime = params.get('runtime', None)
    handler = params.get('handler', None)
    runnable = params.get('runnable', None)
    sdk_config = params.get('sdk_config', None)

    items, _ = resource.db_query(partition, [{'option': None, 'field': 'function_name', 'condition': 'eq',
                                              'value': function_name}])

    if items:
        item = items[0]
        if description:
            item['description'] = description
        if handler:
            item['handler'] = handler
        if runtime:
            item['runtime'] = runtime
        if runnable is not None:
            item['runnable'] = runnable
        if sdk_config is not None:
            item['sdk_config'] = sdk_config
        if zip_file:
            zip_file_id = uuid()
            zip_file_b64 = zip_file.encode('utf-8')
            zip_file_b64 = base64.b64decode(zip_file_b64)
            resource.file_upload_bin(zip_file_id, zip_file_b64)
            item['zip_file_id'] = zip_file_id

        resource.db_update_item(item['id'], item)
        body['function_name'] = function_name
        return Response(body)
    else:
        body['error'] = error.NO_SUCH_FUNCTION
        return Response(body)
