from cloud.aws import *
import boto3

def do(data):  # Create session and return session token
    recipe = data['recipe']
    dynamo = DynamoDB(boto3)
    return data
