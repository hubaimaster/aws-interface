
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.logic.util import generate_requirements_zipfile
from zipfile import ZipFile
from shortuuid import uuid
import tempfile
import os


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'file_path': 'str',
        'file_content': 'str',
        'file_type': '"text" | "bin" | "image" | "video"',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Put file to function zip file'
}

SUPPORT_TYPES = ['text']


@NeedPermission(Permission.Run.Logic.put_function_file)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    function_version = params.get('function_version', 0)
    file_path = params.get('file_path')
    file_content = params.get('file_content')
    file_type = params.get('file_type', 'text')

    if file_type not in SUPPORT_TYPES:
        body['error'] = error.UNSUPPORTED_FILE_TYPE
        return body

    if function_version is None:
        function_version = 0

    items, _ = resource.db_query(partition,
                                 [{'option': None, 'field': 'function_name', 'value': function_name,
                                   'condition': 'eq'}])
    items = list(filter(lambda x: int(x.get('function_version', 0)) == int(function_version), items))

    if len(items) == 0:
        body['message'] = 'function_name: {} did not exist'.format(function_name)
        return body
    else:
        item = items[0]
        zip_file_id = item['zip_file_id']
        zip_file_bin = resource.file_download_bin(zip_file_id)
        zip_temp_dir = tempfile.mktemp()
        extracted_dir = tempfile.mkdtemp()

        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)
        with ZipFile(zip_temp_dir) as zip_file:
            zip_file.extractall(extracted_dir)
        with open(os.path.join(extracted_dir, file_path), 'w+', encoding='utf-8') as fp:
            fp.write(file_content)
        with ZipFile(zip_temp_dir, 'a') as zip_file:
            file_name = os.path.join(extracted_dir, file_path)
            zip_file.write(file_name, file_path)

        zip_file_id = uuid()

        with open(zip_temp_dir, 'rb') as zip_file:
            zip_file_bin = zip_file.read()
            resource.file_upload_bin(zip_file_id, zip_file_bin)
            if 'zip_file_id' in item:
                resource.file_delete_bin(item['zip_file_id'])  # Remove previous zip file
            item['zip_file_id'] = zip_file_id  # Set new file's id
            success = resource.db_update_item(item['id'], item)
            body['success'] = success

        # if 'requirements.txt' in file_path:
        #     requirements_zipfile_id = uuid()
        #     requirements_zipfile_bin = generate_requirements_zipfile(zip_file_bin)
        #     resource.file_upload_bin(requirements_zipfile_id, requirements_zipfile_bin)
        #     if 'requirements_zipfile_id' in item:
        #         resource.file_delete_bin(item['requirements_zipfile_id'])
        #     item['requirements_zipfile_id'] = requirements_zipfile_id

        return body
