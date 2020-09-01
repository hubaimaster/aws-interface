
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from zipfile import ZipFile
import tempfile
import os


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'file_path': 'str',
    },
    'output_format': {
        'item?': {
            'type': '"text" | "bin" | "image" | "video"',
            'content': 'str',
        },
    },
    'description': 'Return function text or binary file'
}


@NeedPermission(Permission.Run.Logic.get_function_file)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    function_version = params.get('function_version', 0)
    file_path = params.get('file_path')

    items, _ = resource.db_query(partition,
                                 [{'option': None, 'field': 'function_name', 'value': function_name,
                                   'condition': 'eq'}])

    if function_version is None:
        function_version = 0
    items = list(filter(lambda x: int(x.get('function_version', 0)) == int(function_version), items))

    if not file_path:
        body['error'] = error.NO_SUCH_FILE
        return body

    if items:
        item = items[0]
        zip_file_id = item['zip_file_id']
        zip_file_bin = resource.file_download_bin(zip_file_id)
        zip_temp_dir = tempfile.mktemp()
        extracted_dir = tempfile.mkdtemp()
        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)
        with ZipFile(zip_temp_dir) as zip_file:
            zip_file.extractall(extracted_dir)
        with open(os.path.join(extracted_dir, file_path), 'r+', encoding="utf-8") as fp:
            content = fp.read()

        body['item'] = {
            'type': 'text',
            'content': content
        }
        return body

    body['error'] = 'function_name: {} did not exist'.format(function_name)
    return body
