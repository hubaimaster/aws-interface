from cloud.aws import *
import boto3

def do(data): 
    recipe = data['recipe']
    dynamo = DynamoDB(boto3)
    return data
