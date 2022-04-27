import os
import shutil
import tempfile

from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid
from zipfile import ZipFile
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


def get_add_requirements_zip_file(resource, zipfile_bin, requirements_zip_file_id):
    """
    zipfile_bin 압축 풀고, requirements 추가 후에 재압축 하여 bin 반환
    :param resource:
    :param zipfile_bin:
    :param requirements_zip_file_id:
    :return:
    """
    requirements_zip_temp_dir = tempfile.mktemp()
    extracted_dir = tempfile.mkdtemp()
    zipfile_temp = tempfile.mktemp()
    requirements_zip_file_bin = resource.file_download_bin(requirements_zip_file_id)
    result_zipfile_name = tempfile.mktemp()
    with open(requirements_zip_temp_dir, 'wb+') as zip_temp:
        zip_temp.write(requirements_zip_file_bin)
    with ZipFile(requirements_zip_temp_dir) as zip_temp:
        zip_temp.extractall(extracted_dir)
    with open(zipfile_temp, 'wb+') as fp:
        fp.write(zipfile_bin)
    with ZipFile(zipfile_temp) as zip_temp:
        zip_temp.extractall(extracted_dir)
    shutil.make_archive(result_zipfile_name, 'zip', extracted_dir)
    with open(f'{result_zipfile_name}.zip', 'rb') as fp:
        result_zipfile_bin = fp.read()

    os.remove(requirements_zip_temp_dir)
    shutil.rmtree(extracted_dir)
    os.remove(zipfile_temp)
    os.remove(f'{result_zipfile_name}.zip')
    return result_zipfile_bin


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
    use_logging = params.get('use_logging', False)
    use_traceback = params.get('use_traceback', False)
    requirements_zip_file_id = params.get('requirements_zip_file_id', None)
    use_standalone = params.get('use_standalone', False)  #

    zip_file_id = uuid()

    item = dict()
    item['function_name'] = function_name
    item['description'] = description
    item['handler'] = handler
    item['runtime'] = runtime
    item['runnable'] = runnable
    item['zip_file_id'] = zip_file_id
    item['requirements_zip_file_id'] = requirements_zip_file_id
    item['sdk_config'] = sdk_config
    item['use_logging'] = use_logging
    item['use_traceback'] = use_traceback
    item['use_standalone'] = use_standalone

    functions, _ = resource.db_query(partition, [
        {'condition': 'eq', 'field': 'function_name', 'value': function_name}
    ], None, 1000, False)
    # item_ids, _ = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    function_version = 0
    if functions:
        function_version = int(functions[-1].get('function_version', 0)) + 1

    item['function_version'] = function_version

    zip_file_b64 = zip_file.encode('utf-8')
    zip_file_bin = base64.b64decode(zip_file_b64)
    resource.file_upload_bin(zip_file_id, zip_file_bin)

    if use_standalone:
        standalone_function_name = f'{function_name}_{function_version}'
        item['standalone_function_name'] = standalone_function_name
        if requirements_zip_file_id:
            zip_file_bin = get_add_requirements_zip_file(resource, zip_file_bin, requirements_zip_file_id)
        resource.function_create_stand_alone_function(standalone_function_name, zip_file_bin)

    resource.db_put_item(partition, item)
    body['function_name'] = function_name
    body['function_version'] = function_version
    return body
    #
    # if len(item_ids) == 0:
    #
    # else:
    #     body['error'] = error.EXISTING_FUNCTION
    #     return body
