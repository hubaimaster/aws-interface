#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

from cloud.permission import Permission, NeedPermission
from cloud.message import error
import cloud.notification.send_slack_message_as_system_notification as slack

import uuid
import os
import tempfile
import cloud.libs.simplejson as json
import subprocess
from zipfile import ZipFile
from cloud.log.create_log import create_event
from concurrent.futures import ThreadPoolExecutor

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'payload': {
            '...': '...',
        }
    },
    'output_format': {
        'response': {
            '...': '...'
        },
        'stdout?': 'str',
        'traceback?': 'str'
    },
    'description': 'Run function and return response'
}


cache = {
    # Cache for speed
}

can_run_subprocess = False


def copy_configfile(destination, sdk_config, config_name='aws_interface_config.json'):
    config_filepath = os.path.join(destination, config_name)
    if not os.path.exists(config_filepath):
        with open(config_filepath, 'w+') as fp:
            json.dump(sdk_config, fp)


def run_subprocess(python_file):
    proc = subprocess.Popen(['python', python_file], stdout=subprocess.PIPE)
    resp = proc.stdout.read().decode('utf-8')
    return resp


def put_cache(key, sub_key, value):
    cache['{}{}'.format(key, sub_key)] = value


def get_cache(key, sub_key):
    return cache.get('{}{}'.format(key, sub_key), None)


# TODO now it can only invoke python3.6 runtime. any other runtimes (java, node, ..) will be able to invoke.
@NeedPermission(Permission.Run.Logic.run_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']
    user = data.get('user', None)
    client_ip = data.get('client_ip', None)

    function_name = params.get('function_name')
    payload = params.get('payload')
    show_traceback = params.get('show_traceback', False)
    # show_traceback = False
    # logging = params.get('logging', False)

    if payload and isinstance(payload, dict):
        payload['__client_ip'] = client_ip

    items, _ = resource.db_query(partition, [{'option': None, 'field': 'function_name', 'value': function_name, 'condition': 'eq'}], reverse=True)

    if len(items) == 0:
        body['error'] = error.NO_SUCH_FUNCTION
        return body
    else:
        item = items[0]

        zip_file_id = item['zip_file_id']
        requirements_zip_file_id = item.get('requirements_zip_file_id', None)
        function_handler = item['handler']
        use_traceback = item.get('use_traceback', False)
        use_logging = item.get('use_logging', False)
        sdk_config = item.get('sdk_config', {})
        use_standalone = item.get('use_standalone', False)
        function_version = item.get('function_version', False)

        function_package = '.'.join(function_handler.split('.')[:-1])
        function_method = function_handler.split('.')[-1]
        function_name_as_random = 'fn{}'.format(uuid.uuid4()).replace('-', '')

        zip_temp_dir = get_cache(zip_file_id, 'zip_temp_dir')
        extracted_dir = get_cache(zip_file_id, 'extracted_dir')

        if use_standalone:
            request_body = {
                'payload': payload,
                'user': user,
                'handler': function_handler,
                'show_traceback': show_traceback and use_traceback
            }
            response = resource.function_execute_stand_alone_function(f'{function_name}_{function_version}', request_body)
            return response  # TODO

        if (zip_temp_dir is None) or (extracted_dir is None):
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
            try:
                if requirements_zip_file_id:
                    requirements_zip_temp_dir = tempfile.mktemp()
                    requirements_zip_file_bin = resource.file_download_bin(requirements_zip_file_id)
                    with open(requirements_zip_temp_dir, 'wb') as zip_temp:
                        zip_temp.write(requirements_zip_file_bin)
                    with ZipFile(requirements_zip_temp_dir) as zip_temp:
                        zip_temp.extractall(extracted_dir)
            except Exception as ex:
                pass

        virtual_handler = 'virtual_handler{}.py'.format(uuid.uuid4())
        virtual_handler_path = os.path.join(extracted_dir, virtual_handler)
        vh_code = "#!/usr/bin/python\n" + \
                  "# -*- coding: utf-8 -*-\n" + \
                  "import io\n" + \
                  "import json\n" + \
                  "import traceback\n" + \
                  "from contextlib import redirect_stdout\n" +\
                  "if __name__ == '__main__':\n" +\
                  "    std_str = io.StringIO()\n" +\
                  "    with redirect_stdout(std_str):\n" + \
                  "        resp, error = None, None\n" + \
                  "        try:\n" + \
                  "            from {} import {} as {}".format(function_package, function_method, function_name_as_random) + '\n' + \
                  "            resp = {}({}, {})\n".format(function_name_as_random, payload, json.loads(json.dumps(user))) +\
                  "        except Exception as e:\n" +\
                  "            error = traceback.format_exc()\n" +\
                  '    print(json.dumps({\"response\": resp, \"stdout\": std_str.getvalue(), \"error\": error}, default=lambda o: \"<not serializable>\"))\n'
        with open(virtual_handler_path, 'w+') as vh:
            vh.write(vh_code)

        return_value = {}
        try:
            return_value = run_subprocess(virtual_handler_path)

            if return_value:
                return_value = json.loads(return_value)
            else:
                return_value = {}

            body['response'] = return_value.get('response', None)
            # body['stdout'] = return_value.get('stdout', None)
            err = return_value.get('error', None)
            if err:
                if use_traceback and show_traceback:
                    body['traceback'] = err

        except Exception as ex:
            error_traceback = None  # traceback.format_exc()
            body['error'] = error.FUNCTION_ERROR
            body['error']['message'] = body['error']['message'].format('{}, {}, {}'.format(ex, error_traceback, return_value))

        # os.remove(zip_temp_dir)
        # shutil.rmtree(extracted_dir, ignore_errors=True)
        os.remove(virtual_handler_path)
        put_cache(zip_file_id, 'zip_temp_dir', zip_temp_dir)
        put_cache(zip_file_id, 'extracted_dir', extracted_dir)

        # Logging
        if use_logging:
            content = json.dumps({
                'params': params,
                'body': body,
            })
            content = content[:1000 * 1000 * 2]
            create_event(resource, user, 'run_function:{}'.format(function_name), content, 'logic')

        return body


from concurrent.futures import ThreadPoolExecutor


class SubprocessPool:
    # subprocess 풀을 만들어 빠르게 실행할 수 있도록 한다 (오버헤드 제거)
    pool = []
    thread_pool = ThreadPoolExecutor(max_workers=32)

    def __init__(self, python_file_path, size=10):
        self.python_file_path = python_file_path
        self.size = size
        self.__inc_process_to_pool()

    def __inc_process_to_pool(self):
        self.pool.append(subprocess.Popen(['python', self.python_file_path],
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE,
                                          stderr=subprocess.STDOUT))

    def __add_processes(self):
        if len(self.pool) < self.size / 3 + 1:
            for idx in range(self.size // 2):
                self.thread_pool.submit(self.__inc_process_to_pool)

    def communication(self, input_string):
        if len(self.pool) == 0:
            # 없으면 즉시 바로 생성
            self.__inc_process_to_pool()
        else:
            self.thread_pool.submit(self.__add_processes)
        process = self.pool.pop(0)
        result = process.communicate(input_string.encode('utf-8'))

        return result


if __name__ == '__main__':
    start = time.time()
    python_file = 'temp.py'

    content = 'import io\n' \
              'import requests\n' \
              'import sys\n'\
              'import traceback\n' \
              'from contextlib import redirect_stdout\n' \
              'import random\n' \
              'v = input()\n'\
              'print("OK", v)\n'

    with open(python_file, 'w+') as fp:
        fp.write(content)

    pp = SubprocessPool(python_file, 6)

    for i in range(0, 30):
        # start = time.time()
        out, err = pp.communication(f'num:{i}')
        print('out:', out.decode('utf-8'))
        print(f'TTT:{i}:', time.time() - start)
        print('------')
