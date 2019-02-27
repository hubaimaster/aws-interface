from cloud.aws import *
from cloud.response import Response
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_path': 'str',
        'index': 'int',
    },
    'output_format': {
        'base64': 'bin',
        'index': 'int',
        'size': 'int',
        'success': 'bool'
    }
}


def do(data, boto3):
    body = {}
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_id = user.get('id', None)

    def has_permission(_item):
        read_groups = _item['read_groups']
        if 'owner' in read_groups:
            owner_id = _item['owner']
            if owner_id == user_id:
                return True
        user_group = user['group']
        return user_group in read_groups

    file_path = params.get('file_path')
    index = params.get('index')

    table_name = 'storage-{}'.format(app_id)
    bucket_name = 'storage-{}'.format(app_id)

    s3 = S3(boto3)
    dynamo = DynamoDB(boto3)
    item = dynamo.get_item(table_name, file_path).get('Item')
    if item:
        if has_permission(item):
            if item['type'] == 'split_file':
                file_key = item['file_key']
                file_bin = s3.download_file_bin(bucket_name, file_key)
                file_b64 = base64.b64encode(file_bin).decode('utf-8')
                body['success'] = True
                body['base64'] = file_b64
                body['index'] = item['index']
                body['size'] = item['size']
                return Response(body)
            else:
                body['success'] = False
                body['message'] = 'file_path is not a split_file'
                return Response(body)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'file_path: {} does not exist'.format(file_path)
        return Response(body)

