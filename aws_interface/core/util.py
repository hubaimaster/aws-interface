import boto3
from datetime import date


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session


def get_current_date():
    today = date.today()
    return today


def get_current_month_date():
    today = date.today()
    datem = date(today.year, today.month, 1)
    return datem


def create_aws_lambda_function(lambda_client, cloud_api):
    name = cloud_api['name']
    handler = cloud_api['handler']
    package = cloud_api['package']
    response = lambda_client.create_function(
        FunctionName=name,
        Runtime='python3.6',
        Role='string',
        Handler=handler,
        Code={
            'ZipFile': b'bytes',
            'S3Bucket': 'string',
            'S3Key': 'string',
            'S3ObjectVersion': 'string'
        },
        Description='string',
        Timeout=123,
        MemorySize=123,
        Publish=True | False,
        VpcConfig={
            'SubnetIds': [
                'string',
            ],
            'SecurityGroupIds': [
                'string',
            ]
        },
        DeadLetterConfig={
            'TargetArn': 'string'
        },
        Environment={
            'Variables': {
                'string': 'string'
            }
        },
        KMSKeyArn='string',
        TracingConfig={
            'Mode': 'Active' | 'PassThrough'
        },
        Tags={
            'string': 'string'
        },
        Layers=[
            'string',
        ]
    )
    return response


