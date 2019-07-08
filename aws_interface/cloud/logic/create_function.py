
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid

from zipfile import ZipFile
import base64
import tempfile
import subprocess
import os
import shutil


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'runtime': 'str',
        'description?': 'str',
        'zip_file?': 'bytes',
        'run_groups': 'list',
        'runnable?': 'bool',
    },
    'output_format': {
        'function_name?': 'str',
    },
    'description': 'Create function'
}


# 이거 그냥 분리해서 실행시 같은 폴더에 넣어주는게 좋을듯? -> 파일 목록에서 보이니깐 미관상 안좋음
def download_unzip_requirements(zipfile_bin):
    output_filename = tempfile.mktemp()
    with open(output_filename, 'wb+') as fp:
        fp.write(zipfile_bin)
    extracted_path = tempfile.mkdtemp()
    with ZipFile(output_filename) as zf:
        zf.extractall(extracted_path)
    sh_path = os.path.join('cloud', 'logic', 'bash')
    sh_path = os.path.join('./', sh_path, 'downloadrequirements.sh')
    subprocess.run([sh_path, extracted_path])
    print(os.listdir(extracted_path))
    shutil.make_archive(output_filename, 'zip', extracted_path)
    with open('{}.zip'.format(output_filename), 'rb') as fp:
        zipfile_bin = fp.read()
    shutil.rmtree(extracted_path)
    os.remove(output_filename)
    return zipfile_bin


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

    item = dict()
    item['function_name'] = function_name
    item['description'] = description
    item['handler'] = handler
    item['runtime'] = runtime
    item['runnable'] = runnable
    item['zip_file_id'] = zip_file_id
    item['sdk_config'] = sdk_config

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'function_name', function_name)
    if len(item_ids) == 0:
        zip_file_b64 = zip_file.encode('utf-8')
        zip_file_bin = base64.b64decode(zip_file_b64)
        zip_file_bin = download_unzip_requirements(zip_file_bin)
        resource.file_upload_bin(zip_file_id, zip_file_bin)
        resource.db_put_item(partition, item)
        body['function_name'] = function_name
        return Response(body)
    else:
        body['error'] = error.EXISTING_FUNCTION
        return Response(body)
