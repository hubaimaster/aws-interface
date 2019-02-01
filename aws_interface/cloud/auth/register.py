from cloud.aws import *
from cloud.crypto import *


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
    params = data['params']
    app_id = data['app_id']

    email = params['email']
    password = params['password']
    extra = params.get('extra', {})

    salt = Salt.get_salt(32)
    password_hash = hash_password(password, salt)

    table_name = '{}-{}'.format(recipe['recipe_type'], app_id)  # Should be auth-143..
    partition = 'user'

    dynamo = DynamoDB(boto3)

    item = {
        'email': email,
        'passwordHash': password_hash,
        'salt': salt,
        'group': 'user',
        'extra': extra,
    }
    dynamo.put_item(table_name, partition, item)
    return response
