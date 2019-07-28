
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
        'runtime': 'str',
        'description?': 'str',
        'zip_file?': 'base64',
        'run_groups': 'list',
        'runnable?': 'bool',
    },
    'output_format': {
        'function_name?': 'str',
    },
    'description': 'Create function'
}


@NeedPermission(Permission.Run.Logic.create_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    description = params.get('description', None)
    zip_file = params.get('zip_file', None)
    runtime = params.get('runtime')
    handler = params.get('handler')
    runnable = params.get('runnable', True)
    sdk_config = params.get('sdk_config', {})

    zip_file_id = uuid()
    requirements_zip_file_id = uuid()

    item = dict()
    item['function_name'] = function_name
    item['description'] = description
    item['handler'] = handler
    item['runtime'] = runtime
    item['runnable'] = runnable
    item['zip_file_id'] = zip_file_id
    item['requirements_zip_file_id'] = requirements_zip_file_id
    item['sdk_config'] = sdk_config

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    if len(item_ids) == 0:
        zip_file_b64 = zip_file.encode('utf-8')
        zip_file_bin = base64.b64decode(zip_file_b64)
        requirements_zip_file_bin = generate_requirements_zipfile(zip_file_bin)
        resource.file_upload_bin(zip_file_id, zip_file_bin)
        resource.file_upload_bin(requirements_zip_file_id, requirements_zip_file_bin)
        resource.db_put_item(partition, item)
        body['function_name'] = function_name
        return body
    else:
        body['error'] = error.EXISTING_FUNCTION
        return body
