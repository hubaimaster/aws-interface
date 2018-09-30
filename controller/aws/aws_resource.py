import boto3
from controller.protocol.resource import Resource
from controller.config import Variable

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

    def create_item(self, service_name, item):
        table_name = Variable.table_prefix + service_name
        table = self.session.resource('dynamodb', self.region).Table(table_name)
        response = table.put_item(
            Item=item
        )
        print('response:', response)
        return True

    def create_table_index(self, service_name, index_name, hash_key, sort_key, hash_type='S', sort_type='N'):
        table_name = Variable.table_prefix + service_name
        response = self.dynamo.update_table(
            AttributeDefinitions=[
                {
                    'AttributeName': hash_key,
                    'AttributeType': hash_type
                }, {
                    'AttributeName': sort_key,
                    'AttributeType': sort_type
                }
            ],
            TableName=table_name,
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
            GlobalSecondaryIndexUpdates=[
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
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    }
                },
            ]
        )
        print('response:', response)
        return True

    def delete_table_index(self, service_name, index_name):
        pass

    def get_table_list(self):
        pass

    def get_table(self, service_name):
        pass

    def set_table_value(self, service_name, key, value):
        pass

    def get_table_value(self, service_name, key):
        pass