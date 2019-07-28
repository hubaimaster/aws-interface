
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid
from cloud.logic.util import generate_requirements_zipfile
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'runtime?': 'str',
        'description?': 'str',
        'zip_file?': 'base64',
        'run_groups?': 'list',
        'runnable?': 'bool',
    },
    'output_format': {
        'function_name?': 'str',
    },
    'description': 'Update function item'
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
            requirements_zip_file_id = uuid()
            zip_file_b64 = zip_file.encode('utf-8')
            zip_file_bin = base64.b64decode(zip_file_b64)
            requirements_zip_file_bin = generate_requirements_zipfile(zip_file_bin)
            resource.file_upload_bin(zip_file_id, zip_file_bin)
            resource.file_upload_bin(requirements_zip_file_id, requirements_zip_file_bin)
            item['zip_file_id'] = zip_file_id
            item['requirements_zip_file_id'] = requirements_zip_file_id

        resource.db_update_item(item['id'], item)
        body['function_name'] = function_name
        return body
    else:
        body['error'] = error.NO_SUCH_FUNCTION
        return body
