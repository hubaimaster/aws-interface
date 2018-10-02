import boto3
from controller.protocol.resource import Resource
from controller.config import Variable, Enum
from decimal import Decimal
import json


# <-- Imp -->
class AwsResource(Resource):

    def __init__(self, aws_request):
        self.request = aws_request
        self.session = boto3.Session(
            aws_access_key_id=aws_request.get_passport()['access_key'],
            aws_secret_access_key=aws_request.get_passport()['secret_key'],
        )
        self.region = aws_request.get_passport()['region']
        self.dynamo = self.session.client('dynamodb', self.region)

    def create_table(self, service_name):
        table_name = Variable.table_prefix + service_name
        response = self.dynamo.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'KEYS_ONLY'
            }
        )
        print('response:', response)
        return True

    def create_table_index(self, service_name, hash_key, sort_key, hash_type='S', sort_type='N'):
        table_name = Variable.table_prefix + service_name
        index_name = Variable.index_prefix + hash_key + '-' + sort_key
        table = self.session.resource('dynamodb', self.region).Table(table_name)
        attr_def = [
                {'AttributeName': hash_key, 'AttributeType': hash_type},
                {'AttributeName': sort_key, 'AttributeType': sort_type}
            ]
        index = [
            {
                'Create': {
                    'IndexName': index_name,
                    'KeySchema': [
                        {
                            'AttributeName': hash_key,
                            'KeyType': 'HASH'
                        }, {
                            'AttributeName': sort_key,
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL',
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 1,
                        'WriteCapacityUnits': 1
                    }
                }
            },
        ]
        response = table.update(AttributeDefinitions=attr_def, GlobalSecondaryIndexUpdates=index)
        print('response:', response)
        return True

    def delete_table_index(self, service_name, index_name):
        table_name = Variable.table_prefix + service_name
        table = self.session.resource('dynamodb', self.region).Table(table_name)
        index = [{
            'Delete': {
                'IndexName': index_name
            }
        }]
        response = table.update(GlobalSecondaryIndexUpdates=index)
        print('response:', response)
        return True

    def get_table_list(self):
        client = self.session.client('dynamodb', self.region)
        t_list = client.list_tables(Limit=100)
        t_name_list = t_list['TableNames']
        return t_name_list

    def get_table(self, service_name):
        table_name = Variable.table_prefix + service_name
        table = self.session.resource('dynamodb', self.region).Table(table_name)

        raise NotImplementedError()

    def set_table_value(self, service_name, key, value):
        table_name = Variable.table_prefix + service_name
        table = self.session.resource('dynamodb', self.region).Table(table_name)
        value = json.dumps(value)
        response = table.put_item(
            Item={
                'id': 'TABLE-VALUE-' + key,
                'modelPartition': Enum.tableValue,
                'creationDate': Decimal(0),
                'value': str(value),
            }
        )
        print('response:', response)

    def get_table_value(self, service_name, key):
        table_name = Variable.table_prefix + service_name
        table = self.session.resource('dynamodb', self.region).Table(table_name)
        item = table.get_item(
            Key={
                'id': 'TABLE-VALUE-' + key
            }
        )['Item']
        value = item['value']
        value = json.loads(value)
        return value

    def deploy_table(self, service_name):
        table_name = Variable.table_prefix + service_name
        return