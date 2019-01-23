from core.util import *
from cloud.aws import *


class ServiceController:
    def __init__(self, bundle, app_id):
        self.bundle = bundle
        self.app_id = app_id
        self.common_init()

    def common_init(self):
        #  init object here .. assign boto3 session
        return

    def apply(self, recipe_controller):
        raise NotImplementedError()

    def generate_sdk(self, recipe_controller):
        raise NotImplementedError()


class BillServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)

    def apply(self, recipe):
        return

    def generate_sdk(self, recipe):
        return None

    def get_cost(self, start, end):
        response = CostExplorer(self.boto3_session).get_cost(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        total = response.get('Total', {})
        blendedCost = total.get('BlendedCost', {})
        amount = blendedCost.get('Amount', -1)
        unit = blendedCost.get('Unit', None)
        result = {'Amount': amount, 'Unit': unit}
        return result

    def get_usage_costs(self, start, end):
        response = CostExplorer(self.boto3_session).get_cost_and_usage(start, end)
        response = response.get('ResultsByTime', {})
        response = response[-1]

        groups = response.get('Groups', [])
        groups = [{
            'Service': x.get('Keys', [None])[0],
            'Cost': x.get('Metrics', {}).get('AmortizedCost', {})
                   } for x in groups]
        groups.sort(key=lambda x: x['Cost']['Amount'], reverse=True)
        return groups


class AuthServiceController(ServiceController):
    def common_init(self):
        self.boto3_session = get_boto3_session(self.bundle)
        self.dynamodb = self.boto3_session.client('dynamodb')
        self.lambda_client = self.boto3_session.client('lambda')
        self.__create_table()

    def __create_table(self):
        table_name = 'auth-' + self.app_id
        try:
            _ = self.dynamodb.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': 'createDate',
                        'AttributeType': 'N'
                    }, {
                        'AttributeName': 'partition',
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
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'partition-createDate-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'partition',
                                'KeyType': 'HASH'
                            }, {
                                'AttributeName': 'createDate',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 3,
                            'WriteCapacityUnits': 3
                        }
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 3,
                    'WriteCapacityUnits': 3
                }
            )
        except:
            return False
        return True

    def _insert_item_to_table(self, partition, item):
        table_name = 'auth-' + self.app_id
        self.dynamodb.put_item(
            TableName='string',
            Item={
                'string': {
                    'S': 'string',
                    'N': 'string',
                    'B': b'bytes',
                    'SS': [
                        'string',
                    ],
                    'NS': [
                        'string',
                    ],
                    'BS': [
                        b'bytes',
                    ],
                    'M': {
                        'string': {'... recursive ...'}
                    },
                    'L': [
                        {'... recursive ...'},
                    ],
                    'NULL': True | False,
                    'BOOL': True | False
                }
            },
        )

    def apply(self, recipe_controller):
        self._apply_user_group(recipe_controller)
        self._apply_cloud_api(recipe_controller)
        return

    def _apply_user_group(self, recipe_controller):
        user_groups = recipe_controller.get_user_groups()

    def _apply_cloud_api(self, recipe_controller):
        cloud_apis = recipe_controller.get_cloud_apis()
        for cloud_api in cloud_apis:
            raise NotImplementedError()


    def generate_sdk(self, recipe_controller):
        return

    def get_user_count(self):
        return 0

