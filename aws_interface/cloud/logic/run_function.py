
from cloud.response import Response
from cloud.permission import Permission, NeedPermission, logic_has_run_permission
from cloud.message import error
import sys
import io
import os
import tempfile

from importlib import import_module
from zipfile import ZipFile
from contextlib import redirect_stdout

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'payload': 'dict',
    },
    'output_format': {
        'response': 'dict',
        'error?': {
            'code': 'int',
            'message': 'str',
        },
    }
}


# TODO now it can only invoke python3.6 runtime. any other runtimes (java, node, ..) will be able to invoke.
@NeedPermission(Permission.Run.Logic.run_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']
    user = data.get('user', None)

    function_name = params.get('function_name')
    payload = params.get('payload')

    items, _ = resource.db_query(partition, [{'option': None, 'field': 'function_name', 'value': function_name, 'condition': 'eq'}])

    if len(items) == 0:
        body['error'] = error.NO_SUCH_FUNCTION
        return Response(body)
    else:
        item = items[0]

        zip_file_id = item['zip_file_id']
        function_handler = item['handler']
        function_package = '.'.join(function_handler.split('.')[:-1])
        function_method = function_handler.split('.')[-1]

        zip_file_bin = resource.file_download_bin(zip_file_id)
        zip_temp_dir = tempfile.mktemp()
        extracted_dir = tempfile.mkdtemp()

        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)
        with ZipFile(zip_temp_dir) as zip_file:
            zip_file.extractall(extracted_dir)
        try:
            #  Comment removing cache because of a performance issue
            #  invalidate_caches()
            sys.path.insert(0, extracted_dir)
            module = import_module(function_package)
            std_str = io.StringIO()
            with redirect_stdout(std_str):
                handler = getattr(module, function_method)
                body['response'] = handler(payload, user)
            body['stdout'] = std_str.getvalue()
        except Exception as ex:
            body['error'] = error.FUNCTION_ERROR
            body['error']['message'] = body['error']['message'].format(ex)
        os.remove(zip_temp_dir)

        return Response(body)
