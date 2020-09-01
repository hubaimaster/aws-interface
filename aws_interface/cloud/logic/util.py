from zipfile import ZipFile
import tempfile
import subprocess
import os
import shutil


def generate_requirements_zipfile(zipfile_bin):
    # output_filename = tempfile.mktemp()
    # with open(output_filename, 'wb+') as fp:
    #     fp.write(zipfile_bin)
    # extracted_path = tempfile.mkdtemp()
    # requirements_zipfile_path = tempfile.mkdtemp()
    # with ZipFile(output_filename) as zf:
    #     zf.extractall(extracted_path)
    # sh_path = os.path.join('cloud', 'logic', 'bash')
    # sh_path = os.path.join('./', sh_path, 'downloadrequirements.sh')
    # subprocess.run([sh_path, extracted_path, requirements_zipfile_path])
    # print(os.listdir(requirements_zipfile_path))
    # shutil.make_archive(output_filename, 'zip', requirements_zipfile_path)
    # with open('{}.zip'.format(output_filename), 'rb') as fp:
    #     zipfile_bin = fp.read()
    # shutil.rmtree(extracted_path)
    # shutil.rmtree(requirements_zipfile_path)
    # os.remove(output_filename)
    return zipfile_bin
