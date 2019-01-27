from cloud.aws import *
import boto3


def do(data):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']

    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    partition = 'user'

    dynamo = DynamoDB(boto3)
    result = dynamo.get_items(table_name, partition, exclusive_start_key=start_key, limit=limit)
    items = result.get('Items', [])
    end_key = result.get('LastEvaluatedKey', None)
    response['items'] = items
    response['end_key'] = end_key
    return response
