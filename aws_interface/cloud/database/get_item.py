from cloud.aws import *
from cloud.response import Response
from cloud.database.util import has_read_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'item': 'map',
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    user_group = user.get('group', None)
    item_id = params.get('item_id', None)

    table_name = 'database-{}'.format(app_id)

    dynamo = DynamoDB(boto3)

    item = dynamo.get_item(table_name, item_id)
    item = item.get('Item', {})

    if has_read_permission(user, item):
        # Remove system key
        body['item'] = item
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
