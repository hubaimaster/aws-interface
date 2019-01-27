from cloud.aws import *
import boto3


def do(data):
    response = {}
    recipe = data['recipe']
    app_id = data['app_id']

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    partition = 'user'

    dynamo = DynamoDB(boto3)
    count = dynamo.get_item_count(table_name, '{}-count'.format(partition))
    count = count.get('Item', {})
    count = count.get('count', 0)
    count = int(count)
    response['value'] = count
    return response
