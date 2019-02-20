from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'path': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, boto3):
    body = {}
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_id = user.get('id', None)

    def has_permission(_item):
        write_groups = _item['write_groups']
        if 'owner' in write_groups:
            owner_id = _item['owner']
            if owner_id == user_id:
                return True
        user_group = user['group']
        return user_group in write_groups

    _path = params.get('path')

    table_name = 'storage-{}'.format(app_id)
    bucket_name = 'storage-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    s3 = S3(boto3)
    item = dynamo.get_item(table_name, _path).get('Item')

    def delete_item(_item):
        if has_permission(_item):
            dynamo.delete_item(table_name, _path)
            if _item['type'] == 'folder':
                items = dynamo.get_items(table_name, _path).get('Items', [])
                print(items)
                for __item in items:
                    delete_item(__item)
            elif _item['type'] == 'file':
                file_key = item['file_key']
                s3.delete_file_bin(bucket_name, file_key)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)

    if item:
        delete_item(item)
        body['success'] = True
        return Response(body)
    else:
        body['success'] = False
        body['message'] = 'folder_path: {} does not exist'.format(_path)
        return Response(body)

