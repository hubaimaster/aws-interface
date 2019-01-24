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


def create_zipfile_bin(dir_name):
    output_filename = uuid.uuid4()
    shutil.make_archive(output_filename, 'zip', dir_name)
    zip_file = open(output_filename, 'rb')
    zip_file_bin = zip_file.read()
    zip_file.close()
    os.remove(zip_file)
    return zip_file_bin


def get_aws_iam_role_arn(iam_client):
    return iam_client.CurrentUser().arn


def create_aws_lambda_function(lambda_client, cloud_api):
    name = cloud_api['name']
    description = cloud_api['description']
    handler = cloud_api['handler']
    package = cloud_api['package']
    package_path = importlib.import_module(package).__path__
    zip_file_bin = create_zipfile_bin(package_path)
    role_arn = ''
    response = lambda_client.create_function(
        FunctionName=name,
        Runtime='python3.6',
        Role=role_arn,  # TODO
        Handler=handler,
        Code={
            'ZipFile': zip_file_bin,
        },
        Description=description,
        Timeout=32,
        MemorySize=128,
        Publish=True,
        TracingConfig={
            'Mode': 'Active'
        }
    )
    return response


