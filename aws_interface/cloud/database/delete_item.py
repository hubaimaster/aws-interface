from cloud.aws import *
from cloud.response import Response


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

    def has_write_permission(user, item):
        group = user.get('group', None)
        user_id = user.get('id', None)
        groups = item.get('write_groups', [])
        if group in groups:
            return True
        elif 'owner' in groups and user_id == item.get('owner'):
            return True
        return False

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
