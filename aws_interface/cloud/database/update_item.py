from cloud.aws import *
from cloud.response import Response
from cloud.database.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'item': 'map',
        'read_groups': 'list',
        'write_groups': 'list',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    item_id = params.get('item_id', None)
    new_item = params.get('item', {})
    read_groups = params.get('read_groups', [])
    write_groups = params.get('write_groups', [])

    new_item['read_groups'] = read_groups
    new_item['write_groups'] = write_groups

    table_name = 'database-{}'.format(app_id)

    dynamo = DynamoDB(boto3)

    result = dynamo.get_item(table_name, item_id)
    item = result.get('Item', {})

    if has_write_permission(user, item):
        dynamo.update_item(table_name, item_id, new_item)
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
