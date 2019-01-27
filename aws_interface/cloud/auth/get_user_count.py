from cloud.aws import *
from cloud.crypto import *
import boto3


def do(data):
    response = {}
    recipe = data['recipe']
    params = data['params']
    app_id = data['app_id']
    admin = data['admin']

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
        'extra': extra,
    }
    dynamo.put_item(table_name, partition, item)
    return response
