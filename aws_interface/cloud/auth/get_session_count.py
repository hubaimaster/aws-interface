from cloud.aws import *

# Define the input output format of the function.
# This information is used when creating the *SDK*.
input_format = {

}
output_format = {
    'item': {
        'count': int
    }
}


def do(data, boto3):
    response = {}
    recipe = data['recipe']
    app_id = data['app_id']

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)
    partition = 'session'

    dynamo = DynamoDB(boto3)
    count = dynamo.get_item_count(table_name, '{}-count'.format(partition))
    item = count.get('Item', {'count': 0})
    response['item'] = item
    return response
