from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'parent_name': 'str',
        'folder_name': 'str',
    },
    'output_format': {
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

    parent_name = params.get('parent_name')
    folder_name = params.get('folder_name')
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    item = {

    }
    item['owner'] = user_id

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)


    body['success'] = True
    return Response(body)
