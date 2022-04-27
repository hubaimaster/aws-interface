"""
패키지 이름을 받아 설치하고, zip 파일을 만듭니다.
"""

from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid
from cloud import env
import tempfile
import subprocess
import os
import shutil


def generate_requirements_zipfile(package_text):
    output_filename = tempfile.mktemp()
    requirements_file = tempfile.mktemp()
    extracted_path = tempfile.mkdtemp()
    requirements_zipfile_path = tempfile.mkdtemp()
    with open(requirements_file, 'w+') as fp:
        fp.write(package_text)
    proc = subprocess.Popen(['pip', 'install', '-r', requirements_file, '-t', extracted_path, '--no-cache-dir'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # proc = subprocess.call(f'pip install -r {requirements_file} -t {extracted_path} --no-cache-dir'.split(),
    #                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    response_stdout = proc.stdout.read().decode('utf-8')

    print(os.listdir(extracted_path))
    shutil.make_archive(output_filename, 'zip', extracted_path)
    output_zip_file_name = '{}.zip'.format(output_filename)
    with open(output_zip_file_name, 'rb') as fp:
        zipfile_bin = fp.read()
    shutil.rmtree(extracted_path)
    shutil.rmtree(requirements_zipfile_path)
    os.remove(output_zip_file_name)
    return zipfile_bin, response_stdout


# Define the input output format of the function.
# This information is used when creating the *SDK*.
# 내부 함수

info = {
    'input_format': {
        'package_text': 'str, requirements.txt or package.json ...',
        'runtime': 'str="python | node"',
    },
    'output_format': {
        'zip_file_id': 'str',
    },
    'description': 'Install packages via package management program and return its internal file id'
                   'ATTENTION! DO NOT ALLOW permission that have invoked this function for NON-ADMIN users.'
}


@NeedPermission(Permission.Run.Logic.create_packages_zip)
def do(data, resource):
    if not env.safe_to_run_code():
        return {
            'success': False,
            'error': error.CANNOT_RUN_ON_NON_SERVERLESS
        }

    body = {}
    params = data['params']
    package_text = params.get('package_text')
    if not package_text:
        return {
            'success': False,
            'error': error.REQUIRED_PARAMS_NOT_EXIST
        }

    requirements_zip_file_id = uuid()

    requirements_zip_file_bin, response_stdout = generate_requirements_zipfile(package_text)
    resource.file_upload_bin(requirements_zip_file_id, requirements_zip_file_bin)

    body['zip_file_id'] = requirements_zip_file_id
    body['response_stdout'] = response_stdout
    return body


if __name__ == '__main__':
    text = 'requests'
    generate_requirements_zipfile(text)
