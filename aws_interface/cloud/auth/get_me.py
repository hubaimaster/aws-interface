from cloud.aws import *
from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str'
    },
    'output_format': {
        'item': {
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'group': 'str',
            'extra': 'map',
        }
    }
}


def do(data, boto3):
    body = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    session_id = params.get('session_id', None)

    table_name = 'auth-{}'.format(app_id)

    dynamo = DynamoDB(boto3)
    try:
        result = dynamo.get_item(table_name, session_id)
    except BaseException as ex:
        print(ex)
        body['message'] = 'permission denied'
        Response(body)

    item = result.get('Item', {})
    user_id = item.get('userId', None)
    if user_id:
        user = dynamo.get_item(table_name, user_id).get('Item', None)
        body['item'] = user
    else:
        body['item'] = None
    return Response(body)
