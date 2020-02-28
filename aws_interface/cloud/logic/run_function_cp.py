from cloud.permission import Permission, NeedPermission
from cloud.message import error

import ast
import uuid
import os
import tempfile
import cloud.libs.simplejson as json
import traceback
import subprocess

from zipfile import ZipFile
from cloud.log.create_log import create_event


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'payload': {
            '...': '...',
        },
    },
    'output_format': {
        'response': {
            '...': '...'
        },
        'stdout?': 'str',
    },
    'description': 'Run function and return response'
}


def copy_configfile(destination, sdk_config, config_name='aws_interface_config.json'):
    config_filepath = os.path.join(destination, config_name)
    if not os.path.exists(config_filepath):
        with open(config_filepath, 'w+') as fp:
            json.dump(sdk_config, fp)


def run_subprocess(python_file):
    proc = subprocess.Popen(['python', python_file], stdout=subprocess.PIPE)
    resp = proc.stdout.read().decode('utf-8')
    return resp


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
        return body
    else:
        item = items[0]

        zip_file_id = item['zip_file_id']
        requirements_zip_file_id = item.get('requirements_zip_file_id', None)
        function_handler = item['handler']
        sdk_config = item.get('sdk_config', {})
        function_package = '.'.join(function_handler.split('.')[:-1])
        function_method = function_handler.split('.')[-1]

        zip_file_bin = resource.file_download_bin(zip_file_id)

        zip_temp_dir = tempfile.mktemp()

        extracted_dir = tempfile.mkdtemp()

        with open(zip_temp_dir, 'wb') as zip_temp:
            zip_temp.write(zip_file_bin)

        # Extract function files and copy configs
        with ZipFile(zip_temp_dir) as zip_file:
            zip_file.extractall(extracted_dir)
            copy_configfile(extracted_dir, sdk_config)

        # Extract requirements folders and files
        if requirements_zip_file_id:
            requirements_zip_temp_dir = tempfile.mktemp()
            requirements_zip_file_bin = resource.file_download_bin(requirements_zip_file_id)
            with open(requirements_zip_temp_dir, 'wb') as zip_temp:
                zip_temp.write(requirements_zip_file_bin)
            with ZipFile(requirements_zip_temp_dir) as zip_temp:
                zip_temp.extractall(extracted_dir)

        virtual_handler = 'virtual_handler{}.py'.format(uuid.uuid4())
        virtual_handler_path = os.path.join(extracted_dir, virtual_handler)
        vh_code = "from {} import {}".format(function_package, function_method) + '\n' +\
                  "import io\n" + \
                  "import json\n" + \
                  "from contextlib import redirect_stdout\n" +\
                  "if __name__ == '__main__':\n" +\
                  "    std_str = io.StringIO()\n" +\
                  "    with redirect_stdout(std_str):" +\
                  "        resp = {}({}, {})".format(function_method, payload, {}) + "\n" +\
                  '    print(json.dumps({\"response\": resp, \"stdout\": str(std_str.getvalue())}))\n'

        with open(virtual_handler_path, 'w+') as vh:
            vh.write(vh_code)

        try:
            return_value = run_subprocess(virtual_handler_path)
            return_value = ast.literal_eval(return_value)
            response = return_value.get('response')
            stdout = return_value.get('stdout')

            body['response'] = response
            body['stdout'] = stdout

        except Exception as ex:
            error_traceback = traceback.format_exc()
            body['error'] = error.FUNCTION_ERROR
            body['error']['message'] = body['error']['message'].format('{}, {}'.format(ex, error_traceback))
        os.remove(zip_temp_dir)

        # Logging
        create_event(resource, user, 'run_function:{}'.format(function_name), json.dumps({
            'params': params,
            'body': body,
        }), 'logic')

        return body
