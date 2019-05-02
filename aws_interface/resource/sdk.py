
import os
import shutil
import tempfile
from os import listdir
from os.path import isfile, join


PLATFORMS = (
    'java',
    'javascript',
    'python3',
    'swift'
)


def generate(rest_api_url, platform):
    """
    Generate the sdk for the given recipe types.

    :param rest_api_url
    URL of REST API

    :param platform

    :return: Binary of zipfile
    """
    if platform not in PLATFORMS:
        raise ValueError('platform should be one of {}'.format(PLATFORMS))

    template_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(template_dir, 'templates')
    template_dir = os.path.join(template_dir, platform)

    working_dir = tempfile.mkdtemp()
    sdk_dir = os.path.join(working_dir, 'sdk')

    shutil.copytree(template_dir, sdk_dir)

    _replace_template_key(sdk_dir, 'REST_API_URL', rest_api_url)
    # Archive all files and extract binary
    output_filename = tempfile.mktemp()
    shutil.make_archive(output_filename, 'zip', sdk_dir)
    zip_file = '{}.zip'.format(output_filename)
    with open(zip_file, 'rb') as f:
        zip_file_bin = f.read()

    # Remove temp files
    os.remove(zip_file)
    shutil.rmtree(working_dir)

    return zip_file_bin


def _replace_template_key(sdk_dir, key, value):
    """
    Replace {{key}} to value in file
    :param sdk_dir: dir included file included {{key}}
    :param key: tag to replace
    :param value: replacement for {{key}}
    :return:
    """
    target_key = '{{' + key + '}}'
    files = [f for f in listdir(sdk_dir) if isfile(join(sdk_dir, f))]
    for file in files:
        file = os.path.join(sdk_dir, file)
        with open(file, 'r') as rf:
            template_file = rf.read()
            template_file = template_file.replace(target_key, value)
        with open(file, 'w+') as wf:
            wf.write(template_file)
