import json
import boto3


def get_boto3_session(access_key, secret_key):
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session


class Saver:
    def __init__(self, boto3_session):
        self.s3 = boto3_session.client('s3')

    def __upload__(self, local_file_path, bucket, obj):
        self.s3.upload_file(local_file_path, bucket, obj)

    def save(self, abstract_service):
        json_string = json.dumps(abstract_service)


class AbstractService(dict):
    #Load service config from aws service
    def __init__(self, user_id):
        raise NotImplementedError()

    #Save service config to aws service
    def save(self):
        raise NotImplementedError()
