from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item': 'dict',
        'partition': 'str',
        'read_groups': 'list',
        'write_groups': 'list',
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
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    read_groups.append('admin')
    write_groups.append('admin')
    
    item['read_groups'] = read_groups
    item['write_groups'] = write_groups
    item['owner'] = user_id

    table_name = 'database-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    dynamo.put_item(table_name, partition, item)

    body['success'] = True
    body['item_id'] = item.get('id', None)
    return Response(body)
