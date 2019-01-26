import json


class APIGateway:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('apigateway')

    def create_rest_api(self, api_name):
        response = self.client.create_rest_api(
            name=api_name,
            minimumCompressionSize=128,
            apiKeySource='HEADER',
            endpointConfiguration={
                'types': [
                    'EDGE'
                ]
            }
        )
        return response

    def delete_rest_api(self, rest_api_id):
        return self.client.delete_rest_api(
            restApiId=rest_api_id
        )


class DynamoDB:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('dynamodb')
        self.resource = boto3_session.resource('dynamodb')

    def create_table(self, table_name):
        try:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }
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
            return response
        except:
            return None

    def update_table(self, table_name, indexes):
        attr_updates = []
        index_updates = []
        for index in indexes:
            hash_key = index['hash_key']
            hash_key_type = index['hash_key_type']
            sort_key = index['sort_key']
            sort_key_type = index['sort_key_type']
            index_name = hash_key + '-' + sort_key
            index_create = {
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
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    }
                }
            hash_key_update = {
                'AttributeName': hash_key,
                'AttributeType': hash_key_type
            }
            sort_key_update = {
                'AttributeName': sort_key,
                'AttributeType': sort_key_type
            }
            index_updates.append(index_create)
            attr_updates.append(hash_key_update)
            attr_updates.append(sort_key_update)
        try:
            response = self.client.update_table(
                AttributeDefinitions=attr_updates,
                TableName=table_name,
                GlobalSecondaryIndexUpdates=index_updates
            )
        except:
            return None
        return response

    def put_item(self, table_name, item_id, item):
        item['id'] = item_id
        response = self.client.put_item(
            TableName=table_name,
            Item=item,
        )
        return response

    def delete_item(self, table_name, item_id):
        response = self.client.delete_item(
            TableName=table_name,
            Key={
                'id': {
                    'S': item_id
                }
            }
        )
        return response





class Lambda:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('lambda')

    def create_function(self, name, description, runtime, role_arn, handler, zip_file):
        response = self.client.create_function(
            FunctionName=name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={
                'ZipFile': zip_file
            },
            Description=description,
            Timeout=128,
            MemorySize=128,
            Publish=True,
            TracingConfig={
                'Mode': 'Active'
            },
        )
        return response


class IAM:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('iam')

    def create_role_and_attach_policies(self, role_name):
        policy_arns = [
            'arn:aws:iam::aws:policy/AWSLambdaExecute',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        try:
            self.create_role(role_name)
        except:
            print('Already have a role', role_name)
        try:
            self.attach_policies(role_name, policy_arns)
        except:
            print('Fail to attach policies')
        return self.get_role_arn(role_name)

    def get_role_arn(self, role_name):
        role = self.client.Role(role_name)
        role_arn = role.arn
        return role_arn

    def create_role(self, role_name):
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        assume_role_policy_document = json.dumps(assume_role_policy_document)
        response = self.client.create_role(
            Path='/',
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document,
        )
        return response

    def attach_policies(self, role_name, policy_arns):
        for policy_arn in policy_arns:
            self.attach_policy(role_name, policy_arn)

    def attach_policy(self, role_name, policy_arn):
        response = self.client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        return response


class CostExplorer:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('ce', 'us-east-1')

    def get_cost_and_usage(self, start, end):
        response = self.client.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['AmortizedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                },
            ],
        )
        return response

    def get_cost(self, start, end):
        response = self.client.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['BLENDED_COST']
        )
        return response
