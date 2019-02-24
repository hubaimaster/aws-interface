from cloud.aws import *
from cloud.response import Response
from cloud.database.util import has_write_permission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
    },
    'output_format': {
        'success': 'bool',
        'message': 'str',
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    user = data['user']

    item_id = params.get('item_id', None)
    table_name = 'database-{}'.format(app_id)
    dynamo = DynamoDB(boto3)

    item = dynamo.get_item(table_name, item_id).get('Item')
    if has_write_permission(user, item):
        _ = dynamo.delete_item(table_name, item_id)
        body['success'] = True
    else:
        body['success'] = False
        body['message'] = 'permission denied'
    return Response(body)
