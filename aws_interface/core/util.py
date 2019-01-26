import boto3
import shutil
import importlib
import uuid
import os
from datetime import date


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        #region_name='us-east-1',
    )
    return session


def get_current_date():
    today = date.today()
    return today


def get_current_month_date():
    today = date.today()
    datem = date(today.year, today.month, 1)
    return datem


def create_zipfile_bin(dir_name, root_name='cloud'):
    output_filename = str(uuid.uuid4())
    tmp_dir = str(uuid.uuid4())
    if os.path.isdir(tmp_dir):
        os.remove(tmp_dir)
    os.mkdir(tmp_dir)
    shutil.copytree(dir_name, '{}/{}'.format(tmp_dir, root_name))
    shutil.make_archive(output_filename, 'zip', tmp_dir)
    zip_file_name = '{}.zip'.format(output_filename)
    zip_file = open(zip_file_name, 'rb')
    zip_file_bin = zip_file.read()
    zip_file.close()
    os.remove(zip_file_name)
    shutil.rmtree(tmp_dir)
    return zip_file_bin


def get_aws_iam_role_arn(iam_client):
    return iam_client.CurrentUser().arn


