from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item': 'str',
        'partition': 'str',
        'read_permissions': 'list',
        'write_permissions': 'list',
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

    partition = params.get('partition', None)
    item = params.get('item', {})
    read_permissions = params.get('read_permissions', [])
    write_permissions = params.get('write_permissions', [])

    item['read_permissions'] = read_permissions
    item['write_permissions'] = write_permissions
    item['owner'] = user_id

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    dynamo.put_item(table_name, partition, item)

    body['success'] = True
    return Response(body)
