from cloud.aws import *
from cloud.response import Response
import cloud.shortuuid as shortuuid

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'file_path': 'str',
    },
    'output_format': {
        'file_bin': 'bin',
        'success': 'bool'
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
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

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    bucket_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    s3 = S3(boto3)
    dynamo = DynamoDB(boto3)
    item = dynamo.get_item(table_name, file_path).get('Item')
    if item:
        if has_permission(item):
            file_key = item['file_key']
            file_bin = s3.download_file_bin(bucket_name, file_key)
            body['file_bin'] = file_bin
            body['success'] = True
            return Response(body)
        else:
            body['success'] = False
            body['message'] = 'permission denied'
            return Response(body)
    else:
        body['success'] = False
        body['message'] = 'file_path: {} does not exist'.format(file_path)
        return Response(body)


    folder = dynamo.get_item(table_name, file_path)
    if folder.get('Item'):
        body['success'] = False
        body['message'] = 'file_path: {} exists'.format(file_path)
        return Response(body)

    dynamo.put_item(table_name, parent_path, item, item_id=file_path)
    body['success'] = True
    return Response(body)
