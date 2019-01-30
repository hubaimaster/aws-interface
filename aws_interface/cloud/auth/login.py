from cloud.aws import *


def do(data, boto3):  # Create session and return session token
    recipe = data['recipe']
    dynamo = DynamoDB(boto3)
    return data
