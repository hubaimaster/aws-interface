from cloud.aws import *


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    session_id = params.get('id', None)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)

    dynamo = DynamoDB(boto3)
    result = dynamo.get_item(table_name, session_id)
    item = result.get('Item', None)
    response['item'] = item
    return response
