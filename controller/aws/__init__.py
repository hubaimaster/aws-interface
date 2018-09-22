import boto3
from controller.protocol import Resource, Request


class AwsRequest(Request):
    def __init__(self, access_key, secret_key, region, params):
        self['passport'] = {'access_key': access_key,
                            'secret_key': secret_key,
                            'region': region}
        self['params'] = params

    def get_param(self, key):
        if key in self['params']:
            return self['params'][key]
        else:
            raise BaseException(key, 'not in', self['params'])

    def get_passport(self):
        return self['passport']


class AwsResource(Resource):

    def __init__(self, aws_request):
        self.request = aws_request
        self.session = boto3.Session(
            aws_access_key_id=aws_request.get_passport()['access_key'],
            aws_secret_access_key=aws_request.get_passport()['secret_key'],
        )
        self.region = aws_request.get_passport()['region']
        self.dynamo = self.session.client('dynamodb', self.region)

    def create_table(self, table_name):
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

    def create_item(self, table_name, item):
        table = self.session.resource('dynamo', self.region).Table(table_name)
        response = table.put_item(
            Item=item
        )
        print('response:', response)
        return True

    def create_table_index(self, table_name, index_name, hash_key, sort_key, hash_type='S', sort_type='N'):
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

