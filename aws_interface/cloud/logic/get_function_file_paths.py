
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from zipfile import ZipFile
import tempfile
import os


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
    },
    'output_format': {
        'item?': {
            'type': '"text" | "bin" | "image" | "video"',
            'content': 'str',
        },
        'error?': {
            'code': 'int',
            'message': 'str',
        },
    }
}


def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d


@NeedPermission(Permission.Run.Logic.get_function_file_paths)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')

    items, _ = resource.db_query(partition,
                                 [{'option': None, 'field': 'function_name', 'value': function_name,
                                   'condition': 'eq'}])

    if len(items) == 0:
        body['message'] = 'function_name: {} did not exist'.format(function_name)
        return Response(body)
    else:
        item = items[0]
        zip_file_id = item['zip_file_id']
        zip_file_bin = resource.file_download_bin(zip_file_id)
        zip_temp_dir = tempfile.mktemp(prefix='/tmp/')

        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)
        with ZipFile(zip_temp_dir) as zip_file:
            file_paths = zip_file.namelist()
            file_paths = [file_path for file_path in file_paths if not file_path.endswith('/')]
            body['file_paths'] = list(set(file_paths))
        return Response(body)
