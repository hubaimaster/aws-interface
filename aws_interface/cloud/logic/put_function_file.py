import shutil

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

    # 나중에 주석과 같이 업데이트해야하는데 테스트가 부족해서 보류.
    if function_version is None:  # or function_version == '':
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

        requirements_zip_file_id = item.get('requirements_zip_file_id', None)

        requirements_zip_file_bin = None
        requirements_temp_dir = None
        if requirements_zip_file_id:
            requirements_zip_file_bin = resource.file_download_bin(requirements_zip_file_id)
            requirements_temp_dir = tempfile.mktemp()

        extracted_dir = tempfile.mkdtemp()
        use_standalone = item.get('use_standalone', False)

        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)
        with ZipFile(zip_temp_dir) as zip_file:
            zip_file.extractall(extracted_dir)

        # Standalone 의 경우 따로 requirements 패키지 다운받아서 재압축
        if use_standalone and requirements_zip_file_id:
            with open(requirements_temp_dir, 'wb') as zip_temp:
                zip_temp.write(requirements_zip_file_bin)
            with ZipFile(requirements_temp_dir) as zip_file:
                zip_file.extractall(extracted_dir)

        with open(os.path.join(extracted_dir, file_path), 'w+', encoding='utf-8') as fp:
            fp.write(file_content)

        new_zip_path = tempfile.mktemp()
        shutil.make_archive(new_zip_path, 'zip', extracted_dir)
        new_zip_path_ext = f'{new_zip_path}.zip'
        with ZipFile(new_zip_path_ext, 'a') as zip_file:
            file_name = os.path.join(extracted_dir, file_path)
            zip_file.write(file_name, file_path)

        zip_file_id = uuid()

        with open(new_zip_path_ext, 'rb') as zip_file:
            zip_file_bin = zip_file.read()
            resource.file_upload_bin(zip_file_id, zip_file_bin)

            if 'zip_file_id' in item:
                resource.file_delete_bin(item['zip_file_id'])  # Remove previous zip file
            item['zip_file_id'] = zip_file_id  # Set new file's id
            success = resource.db_update_item(item['id'], item)
            if use_standalone:
                resource.function_update_stand_alone_function(f'{function_name}_{function_version}', zip_file_bin)
            body['success'] = success

        try:
            os.remove(new_zip_path_ext)
            os.remove(zip_temp_dir)
            if requirements_temp_dir:
                os.remove(requirements_temp_dir)
            shutil.rmtree(extracted_dir)
        except Exception as ex:
            print(ex)

        return body
