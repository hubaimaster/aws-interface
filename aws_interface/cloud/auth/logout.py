from cloud.aws import *
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'message': 'str',
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
    dynamo.delete_item(table_name, 'session', session_id)
    body['message'] = '로그아웃 되었습니다.'
    return Response(body)
