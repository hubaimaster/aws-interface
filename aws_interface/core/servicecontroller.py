from core.util import *


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
        boto3_session = get_boto3_session(self.bundle)
        self.cost_explorer = boto3_session.client('ce')

    def apply(self, recipe):
        return

    def generate_sdk(self, recipe):
        return None

    def get_cost(self, start, end):
        response = self.cost_explorer.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['BLENDED_COST']
        )
        response = response.get('ResultsByTime', {})
        response = response[-1]

        total = response.get('Total', {})
        blendedCost = total.get('BlendedCost', {})
        amount = blendedCost.get('Amount', -1)
        unit = blendedCost.get('Unit', None)
        return {'Amount': amount, 'Unit': unit}

    def get_usage_costs(self, start, end):
        response = self.cost_explorer.get_cost_and_usage(
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
        boto3_session = get_boto3_session(self.bundle)
        self.dynamodb = boto3_session.client('dynamodb')

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
                        'AttributeName': 'group',
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
                        'IndexName': 'group-createDate-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'group',
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

    def apply(self, recipe):
        return

    def generate_sdk(self, recipe):
        return

    def get_user_count(self):
        return 0

