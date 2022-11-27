import json
import time
import tempfile
import botocore
import botocore.client
from boto3.dynamodb.conditions import Key, Attr

from sys import maxsize
from decimal import Decimal
import cloud.shortuuid as shortuuid
from resource.config import MAX_N_GRAM
from resource.util import divide_chunks
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from concurrent.futures import ThreadPoolExecutor

type_deserializer = TypeDeserializer()
type_serializer = TypeSerializer()


def get_boto3_session(credentials):
    import boto3
    bundle = credentials['aws']
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    region_name = bundle.get('region', 'ap-northeast-2')
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
    )
    return session


class APIGateway:
    stage_name = 'prod_aws_interface'

    def __init__(self, boto3_session):
        self.region = boto3_session.region_name
        self.client = boto3_session.client('apigateway')
        self.lambda_client = boto3_session.client('lambda')
        self.iam_client = IAM(boto3_session)

    def get_rest_api_id(self, rest_api_name):
        rest_api_id = None
        apis = self.get_rest_apis().get('items', [])
        for api in apis:
            if api['name'] == rest_api_name:
                rest_api_id = api['id']
                break
        if not rest_api_id:
            response = self.create_rest_api(rest_api_name)
            rest_api_id = response['id']
        return rest_api_id

    def delete_rest_api_by_name(self, rest_api_name):
        try:
            rest_api_id = self.get_rest_api_id(rest_api_name)
            response = self.client.delete_rest_api(
                restApiId=rest_api_id
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def get_root_resource_id(self, rest_api_id):
        resources = self.get_resources(rest_api_id).get('items', [])
        parent_id = None
        for res in resources:
            if res['path'] == '/':
                parent_id = res['id']
        return parent_id

    def get_lambda_function_resource_id(self, rest_api_id, lambda_func_name):
        resources = self.get_resources(rest_api_id).get('items', [])
        resource_id = None
        for res in resources:
            if res.get('pathPart') == lambda_func_name:
                resource_id = res['id']
        return resource_id

    def get_rest_api_url(self, cloud_api_name):
        base_url = 'https://{}.execute-api.{}.amazonaws.com/{}/{}'
        api_id = self.get_rest_api_id(cloud_api_name)
        region = self.region
        stage = self.stage_name
        url = base_url.format(api_id, region, stage, cloud_api_name)
        return url

    def create_redirection(self, cloud_api_name, name, redirection_uri, method='POST'):
        stage_name = self.stage_name
        api_client = self.client
        path_part = name
        # Find existing rest api
        rest_api_id = self.get_rest_api_id(cloud_api_name)
        root_resource_id = self.get_root_resource_id(rest_api_id)
        resource_id = self.create_resource(rest_api_id, root_resource_id, path_part)['id']
        self.put_method(rest_api_id, resource_id, method)
        self.put_integration(rest_api_id, resource_id, method, redirection_uri, {}, 'AWS_PROXY')
        api_client.create_deployment(
            restApiId=rest_api_id,
            stageName=stage_name,
        )
        url = '{}/{}'.format(self.get_rest_api_url(cloud_api_name), path_part)
        return {
            'rest_api_id': rest_api_id,
            'resource_id': resource_id,
            'name': name,
            'url': url,
            'path': path_part,
            'redirection_uri': redirection_uri,
        }

    def delete_resource(self, rest_api_id, resource_id):
        response = self.client.delete_resource(
            restApiId=rest_api_id,
            resourceId=resource_id
        )
        return response

    def connect_with_lambda(self, cloud_api_name, lambda_func_name):
        aws_region = self.region
        api_client = self.client
        aws_lambda = self.lambda_client

        # Find existing rest api
        rest_api_id = self.get_rest_api_id(cloud_api_name)
        root_resource_id = self.get_root_resource_id(rest_api_id)
        resource_id = self.get_lambda_function_resource_id(rest_api_id, lambda_func_name)

        stage_name = self.stage_name

        if not resource_id:
            resource_id = api_client.create_resource(
                restApiId=rest_api_id,
                parentId=root_resource_id,  # resource id for the Base API path
                pathPart=lambda_func_name
            )['id']

        self.put_method(rest_api_id, resource_id, 'POST')

        lambda_version = aws_lambda.meta.service_model.api_version

        aws_account_id = self.iam_client.get_account_id()

        uri_data = {
            "aws-region": aws_region,
            "api-version": lambda_version,
            "aws-acct-id": aws_account_id,
            "lambda-function-name": lambda_func_name,
        }
        uri = self.get_uri(uri_data)

        integration_response_param = {
            'method.response.header.Access-Control-Allow-Headers': '\'*\'',
            'method.response.header.Access-Control-Allow-Methods': '\'POST,OPTIONS\'',
            'method.response.header.Access-Control-Allow-Origin': '\'*\''
        }
        method_response_param = {
            'method.response.header.Access-Control-Allow-Headers': False,
            'method.response.header.Access-Control-Allow-Origin': False,
            'method.response.header.Access-Control-Allow-Methods': False,
            'method.response.header.X-Requested-With': False,
        }

        # create integration
        self.put_integration(rest_api_id, resource_id, 'POST', uri)
        self.put_integration_response(rest_api_id, resource_id, 'POST')
        self.put_method_response(rest_api_id, resource_id, 'POST', method_response_param)

        uri_data['aws-api-id'] = rest_api_id
        post_source_arn = self.get_source_arn(uri_data, 'POST')

        print('put_permission post'.center(80, '-'))
        self.put_permission(lambda_func_name, post_source_arn)

        # CORS OPTION
        self.put_method(rest_api_id, resource_id, 'OPTIONS')
        self.put_method_response(rest_api_id, resource_id, 'OPTIONS', method_response_param)
        self.put_integration(rest_api_id, resource_id, 'OPTIONS', uri, {
            'application/json': '{"statusCode": 200}'
        }, 'MOCK')

        self.put_integration_response(rest_api_id, resource_id, 'OPTIONS', integration_response_param)
        self.put_integration_response(rest_api_id, resource_id, 'POST', integration_response_param)

        print('create_deployment'.center(80, '-'))
        api_client.create_deployment(
            restApiId=rest_api_id,
            stageName=stage_name,
        )

    def put_method(self, rest_api_id, resource_id, method_type, auth_type='NONE'):
        try:
            response = self.client.put_method(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=method_type,
                authorizationType=auth_type,
                apiKeyRequired=False,
            )
        except BaseException as ex:
            print(ex)
            return None
        return response

    def put_method_response(self, rest_api_id, resource_id, method_type, response_parameters=dict()):
        try:
            response = self.client.put_method_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod=method_type,
                statusCode="200",
                responseParameters=response_parameters,
            )
        except BaseException as ex:
            response = None
            print(ex)
        return response

    def get_uri(self, uri_data):
        uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:" \
               "{aws-acct-id}:function:{lambda-function-name}/invocations".format(**uri_data)
        return uri

    def put_integration(self, rest_api_id, resource_id, method_type, uri, requestTemplates={}, type="AWS_PROXY"):
        integration_resp = self.client.put_integration(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=method_type,
            type=type,
            integrationHttpMethod=method_type,
            uri=uri,
            requestTemplates=requestTemplates,
        )
        return integration_resp

    def put_integration_response(self, rest_api_id, resource_id, method_type, response_parameters=dict()):
        response = self.client.put_integration_response(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=method_type,
            statusCode="200",
            selectionPattern=".*",
            responseParameters=response_parameters,
        )
        return response

    def get_source_arn(self, uri_data, method_type):
        method_type = 'POST'
        arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/" + method_type + "/{lambda-function-name}"
        arn = arn.format(**uri_data)
        return arn

    def put_permission(self, lambda_func_name, source_arn):
        statement_id = 'state{}'.format(lambda_func_name)

        try:
            _ = self.lambda_client.remove_permission(
                FunctionName=lambda_func_name,
                StatementId=statement_id,
            )
        except Exception:
            print('Failed to remove permissions for {}'.format(lambda_func_name))
            pass

        try:
            self.lambda_client.add_permission(
                FunctionName=lambda_func_name,
                StatementId=statement_id,
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn
            )
        except Exception:
            raise Exception('Failed to put permissions for {}'.format(lambda_func_name))

    def get_method(self, rest_api_id, resource_id, method_type='POST'):
        response = self.client.get_method(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=method_type
        )
        return response

    def get_rest_apis(self):
        response = self.client.get_rest_apis(
            limit=100
        )
        return response

    def create_rest_api(self, api_name):
        response = self.client.create_rest_api(
            name=api_name,
            endpointConfiguration={
                'types': [
                    'EDGE'
                ]
            }
        )
        return response

    def create_resource(self, rest_api_id, parent_id, path_part):
        response = self.client.create_resource(
            restApiId=rest_api_id,
            parentId=parent_id,
            pathPart=path_part
        )
        return response

    def get_resources(self, rest_api_id):
        response = self.client.get_resources(
            restApiId=rest_api_id,
            limit=100,
        )
        return response

    def delete_rest_api(self, rest_api_id):
        return self.client.delete_rest_api(
            restApiId=rest_api_id
        )

    def get_method_response(self, rest_api_id, resource_id, method_type, status_code):
        response = self.client.get_method_response(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=method_type,
            statusCode=status_code
        )
        return response


class DynamoDB:
    def __init__(self, boto3_session):
        # TODO 작동안될수도 있으니 조심
        dynamo_config = botocore.client.Config(max_pool_connections=100)
        self.client = boto3_session.client('dynamodb', config=dynamo_config)
        self.resource = boto3_session.resource('dynamodb', config=dynamo_config)
        self.table_cache = {}

    def init_table(self, table_name):
        self.create_table(table_name)

    def create_table(self, table_name, sort_key='creation_date', sort_key_type='N'):
        try:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': 'partition',
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': 'inverted_query',
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': sort_key,
                        'AttributeType': sort_key_type
                    }
                ],
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                ],
                BillingMode='PAY_PER_REQUEST',
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'KEYS_ONLY'
                },
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'partition-{}'.format(sort_key),
                        'KeySchema': [
                            {
                                'AttributeName': 'partition',
                                'KeyType': 'HASH'
                            }, {
                                'AttributeName': '{}'.format(sort_key),
                                'KeyType': 'RANGE'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }, {
                        'IndexName': 'inverted_query-{}'.format(sort_key),
                        'KeySchema': [
                            {
                                'AttributeName': 'inverted_query',
                                'KeyType': 'HASH'
                            }, {
                                'AttributeName': sort_key,
                                'KeyType': 'RANGE'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    },
                ]
            )
            print('CREATING TABLE...')
            self.client.get_waiter('table_exists').wait(TableName=table_name)
            return response
        except Exception as ex:
            print(ex)
            try:
                self.update_table(table_name, {'hash_key': 'inverted_query', 'hash_key_type': 'S',
                                               'sort_key': sort_key, 'sort_key_type': sort_key_type})
            except Exception as ex:
                pass
            try:
                self.update_table(table_name, {'hash_key': 'partition', 'hash_key_type': 'S',
                                               'sort_key': sort_key, 'sort_key_type': sort_key_type})
            except Exception as ex:
                pass

            return True

    def update_table(self, table_name, index):
        attr_updates = []
        index_updates = []
        hash_key = index['hash_key']
        hash_key_type = index['hash_key_type']
        sort_key = index.get('sort_key', None)
        sort_key_type = index.get('sort_key_type', None)
        key_schema = [
            {
                'AttributeName': hash_key,
                'KeyType': 'HASH'
            }
        ]
        if sort_key:
            index_name = hash_key + '-' + sort_key
            key_schema.append({
                'AttributeName': sort_key,
                'KeyType': 'RANGE'
            })
        else:
            index_name = hash_key
        index_create = {
            'Create': {
                'IndexName': index_name,
                'KeySchema': key_schema,
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        }
        hash_key_update = {
            'AttributeName': hash_key,
            'AttributeType': hash_key_type
        }
        index_updates.append(index_create)
        attr_updates.append(hash_key_update)
        if sort_key:
            sort_key_update = {
                'AttributeName': sort_key,
                'AttributeType': sort_key_type
            }
            attr_updates.append(sort_key_update)

        try:
            response = self.client.update_table(
                AttributeDefinitions=attr_updates,
                TableName=table_name,
                GlobalSecondaryIndexUpdates=index_updates
            )
            return response
        except Exception as e:
            if "LimitExceededException" in str(e):
                # print("Error while creating index:" + str(e) + ", RE-TRY AFTER 60 SECONDS")
                # time.sleep(60)
                # # TODO Sleep 대신 스택이나 큐에 등록해놓고 시도.. 대기열
                # return self.update_table(table_name, index)
                return
            else:
                return e

    def delete_table(self, name):
        try:
            response = self.client.delete_table(
                TableName=name
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def delete_fdb_table(self, name):
        try:
            response = self.client.delete_table(
                TableName=name
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def create_partition(self, table_name, partition):
        item = {
            'name': partition
        }
        response = self.put_item(table_name, 'partition-list', item, partition, indexing=False)
        return response

    def get_partition(self, table_name, partition):
        response = self.get_item(table_name, partition)
        return response.get('Item', None)

    def delete_partition(self, table_name, partition):
        return self.delete_item(table_name, partition)

    def get_partitions(self, table_name):
        return self.get_items_in_partition(table_name, 'partition-list', limit=maxsize)

    def delete_item(self, table_name, item_id):
        item = self.get_item(table_name, item_id)
        partition = item.get('Item', {}).get('partition', None)

        response = self.client.delete_item(
            TableName=table_name,
            Key={
                'id': {
                    'S': item_id
                }
            }
        )

        if partition:
            self._add_item_count(table_name, '{}-count'.format(partition), value_to_add=-1)
            # for field, value in item.get('Item', {}).items():
            #     self._add_item_count(table_name, '{}-{}-{}-count'.format(partition, field, value), value_to_add=-1)
        self._delete_inverted_query(table_name, partition, item_id)
        return response

    def get_table(self, table_name):
        # 캐싱된 테이블 객체 반환
        if table_name in self.table_cache:
            table = self.table_cache[table_name]
        else:
            table = self.resource.Table(table_name)
            self.table_cache[table_name] = table
        return table

    def get_projection_expression(self, expression_attribute_names):
        expression = ', '.join(expression_attribute_names)
        return expression

    def get_projection_expression_attribute_names(self, projection_keys):
        expression_attribute_names = {}
        for projection_key in projection_keys:
            key = '#key{}'.format(projection_key)
            val = projection_key
            expression_attribute_names[key] = val
        return expression_attribute_names

    def get_item(self, table_name, item_id, projection_keys=None):
        table = self.get_table(table_name)
        if projection_keys:
            expression_attribute_names = self.get_projection_expression_attribute_names(projection_keys)
            projection_expression = self.get_projection_expression(expression_attribute_names)
            item = table.get_item(Key={
                'id': item_id
            },
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_attribute_names
            )
        else:
            item = table.get_item(Key={
                'id': item_id
            })
        # print("get_item_response:", item)
        return item

    def time(self):
        return Decimal("%.20f" % time.time())

    def to_decimal(self, timestamp):
        return Decimal("%.20f" % timestamp)

    def put_item(self, table_name, partition, item, item_id=None, creation_date=None, indexing=True, index_keys=None, sort_keys=None):
        if 'id' in item:
            item_id = item.get('id')

        if not item_id:
            item_id = str(shortuuid.uuid())
        if not creation_date:
            creation_date = self.time()

        table = self.get_table(table_name)
        item['id'] = item_id
        item['creation_date'] = creation_date
        item['partition'] = partition

        # 디비에 넣기전에 인덱스 타입을 고려하여 데이터를 변경한다.
        if not sort_keys:
            sort_keys = []
        item = self._make_item_type_fit(item, sort_keys)
        try:
            response = table.put_item(
                Item=item,
            )
        except Exception as ex:
            print(ex)
            return False

        """ Counting if the item is a new one """
        self._add_item_count(table_name, '{}-count'.format(partition))

        if indexing:
            self._delete_inverted_query(table_name, partition, item_id)
            # 원래는 update 시에도 put_item 함수를 썼기 때문에, indexes 를 삭제해줘야 했지만, 지금은 그럴 필요가 없음.
            # 근데 Delete_inverted_query 를 하면, 쓸 데 없이 read 쿼리가 수반 됨. 따라서 주석
            self._put_inverted_query(table_name, partition, item, index_keys=index_keys, sort_keys=sort_keys)
        return response

    def get_items(self, table_name, item_ids):
        keys = list([{'id': {'S': item_id}} for item_id in item_ids])
        response = self.client.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': keys,
                    'ConsistentRead': True
                }
            }
        )
        items = response['Responses'][table_name]
        for item in items:
            for key, value in item.items():
                value = type_deserializer.deserialize(value)
                item[key] = value
        return {'Items': items}

    def get_items_in_partition(self, table_name, partition, start_key=None, limit=100, reverse=False):
        index_name = 'partition-creation_date'
        response = self.get_items_eq_hash_key(table_name, index_name, 'partition', partition, start_key, limit, reverse)
        return response

    def get_items_in_partition_by_order(self, table_name, partition, order_by, order_min, order_max, start_key=None, limit=100, reverse=False):
        index_name = 'partition-{}'.format(order_by)
        key_expression = Key('partition').eq(partition)
        if order_min:
            key_expression = key_expression & Key(order_by).gte(Decimal(order_min))
        if order_max:
            key_expression = key_expression & Key(order_by).lte(Decimal(order_max))

        response = self.get_items_with_key_expression(table_name, index_name, key_expression, start_key, limit,
                                                      reverse)
        return response

    def get_inverted_queries(self, table_name, partition, field, operand, operation, order_by, order_min, order_max, start_key=None, limit=100, reverse=False):
        if operation in ['in', 'ins', 'eq']:
            hash_key_name = 'inverted_query'
            sort_key_name = '{}'.format(order_by)
            hash_key = '{}-{}-{}-{}'.format(partition, field, operand, operation)
            index_name = '{}-{}'.format(hash_key_name, sort_key_name)
            key_expression = Key(hash_key_name).eq(hash_key)
            if order_min:
                key_expression = key_expression & Key(sort_key_name).gte(Decimal(order_min))
            if order_max:
                key_expression = key_expression & Key(sort_key_name).lte(Decimal(order_max))
            try:
                response = self.get_items_with_key_expression(table_name, index_name, key_expression, start_key, limit,
                                                          reverse)
            except Exception as ex:
                print(ex)
                response = {
                    'Items': []
                }
            return response
        else:
            raise BaseException('an operation is must be <in> or <eq>')

    def get_items_eq_hash_key(self, table_name, index_name, hash_key_name, hash_key_value,
                              start_key=None, limit=100, reverse=False):
        key_expression = Key(hash_key_name).eq(hash_key_value)
        response = self.get_items_with_key_expression(table_name, index_name, key_expression, start_key, limit, reverse)
        return response

    def get_items_with_key_expression(self, table_name, index_name, key_expression,
                                      start_key=None, limit=100, reverse=False):
        if start_key:
            for key in start_key:
                if isinstance(start_key[key], float):
                    start_key[key] = self.to_decimal(start_key[key])

        scan_index_forward = not reverse
        table = self.resource.Table(table_name)
        if start_key:
            response = table.query(
                IndexName=index_name,
                Limit=limit,
                ConsistentRead=False,
                ExclusiveStartKey=start_key,
                KeyConditionExpression=key_expression,
                ScanIndexForward=scan_index_forward,
            )
        else:
            response = table.query(
                IndexName=index_name,
                Limit=limit,
                ConsistentRead=False,
                KeyConditionExpression=key_expression,
                ScanIndexForward=scan_index_forward,
            )
        return response

    def get_target_fields(self, item, prefix='', target_fields=None):
        if target_fields is None:
            target_fields = []
        for key in item:
            value = item[key]
            if isinstance(value, dict):
                self.get_target_fields(value, key + '.', target_fields)
            else:
                target_fields.append(prefix + key)
        return target_fields

    def get_update_expression_attrs_pair(self, item):
        """
        item 에서 업데이트 표현식과 속성을 튜플로 반환합니다.
        :param item:
        :return: (UpdateExpression, ExpressionAttributeValues)
        """
        expression = 'set'
        attr_names = {}
        attr_values = {}
        for idx, (key, value) in enumerate(item.items()):
            attr_key = '#key{}'.format(idx)
            attr_value = ':val{}'.format(idx)
            expression += ' {}={}'.format(attr_key, attr_value)

            attr_names['{}'.format(attr_key)] = key
            attr_values['{}'.format(attr_value)] = value
            if idx != len(item) - 1:
                expression += ','
        return expression, attr_names, attr_values

    def update_item(self, table_name, item_id, item, index_keys=None, sort_keys=None):
        table = self.get_table(table_name)
        item['id'] = item_id
        response = table.put_item(
            TableName=table_name,
            Item=item,
        )
        partition = item.get('partition')
        min_creation_date = self._delete_inverted_query(table_name, partition, item_id)
        if not item.get('creation_date', None):
            item['creation_date'] = min_creation_date
        self._put_inverted_query(table_name, partition, item, index_keys=index_keys, sort_keys=sort_keys)
        return response

    def update_item_v2(self, table_name, item_id, item, index_keys=None, sort_keys=None):
        table = self.get_table(table_name)
        partition = item.get('partition')
        pop_list = ['id']
        for pop_field in pop_list:
            if pop_field in item:
                item.pop(pop_field)
        if not item:
            return True

        expression, attr_names, attr_values = self.get_update_expression_attrs_pair(item)
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression=expression,
            ExpressionAttributeValues=attr_values,
            ExpressionAttributeNames=attr_names,
            ReturnValues="UPDATED_NEW",
        )
        target_fields = self.get_target_fields(item)
        item['id'] = item_id
        min_creation_date = self._delete_inverted_query(table_name, partition, item_id, target_fields=target_fields)
        if not item.get('creation_date', None):
            item['creation_date'] = min_creation_date
        self._put_inverted_query(table_name, partition, item, index_keys=index_keys, target_fields=target_fields, sort_keys=sort_keys)
        return response

    def update_item_with_strong_read(self, table_name, item_id, item, index_keys):
        """
        일관된 읽기 후 업데이트
        :return:
        """
        # attr_names = {'#{}'.format(key): key for key, _ in item.items}
        # attr_values = {':{}'.format(key): {''}}
        # response = self.client.update_item(
        #     ExpressionAttributeNames=attr_names,
        #     ExpressionAttributeValues={
        #         ':v': {
        #             'N': str(value_to_add),
        #         }
        #     },
        #     Key={
        #         'id': {
        #             'S': item_id,
        #         }
        #     },
        #     ReturnValues='ALL_NEW',
        #     TableName=table_name,
        #     UpdateExpression='ADD #A :v',
        # )
        return

    def _add_item_count(self, table_name, count_id, value_to_add=1):
        if len(str(count_id)) > 1024:  # Index size max is 1024
            return False
        count = 0
        while count < 3:
            count += 1
            try:
                response = self.client.update_item(
                    ReturnConsumedCapacity='INDEXES',
                    ExpressionAttributeNames={
                        '#A': 'count',
                    },
                    ExpressionAttributeValues={
                        ':v': {
                            'N': str(value_to_add),
                        }
                    },
                    Key={
                        'id': {
                            'S': count_id,
                        }
                    },
                    # ReturnValues='ALL_NEW',
                    ReturnValues='NONE',
                    TableName=table_name,
                    UpdateExpression='ADD #A :v',
                )
                # print('add_item_count_response:', response)
                return response
            except Exception as ex:
                print(ex)
                time.sleep(0.3)

    def get_item_count(self, table_name, count_id):
        response = self.get_item(table_name, count_id)
        return response

    def _eq_operands(self, value):
        value = str(value)
        return [value]

    def _make_n_gram(self, value):
        max_len = len(value)
        tokens = []
        for i in range(1, min(MAX_N_GRAM, max_len) + 1):
            for j in range(0, max_len - i + 1):
                token = value[j:j + i]
                tokens.append(token)
        return tokens

    def _ins_operands(self, value):
        if isinstance(value, str):
            return self._make_n_gram(value)
        else:
            return []

    def _make_item_type_fit(self, item, sort_keys):
        """
        item 내부 키들의 타입 중 인덱스키에 위반 되는 것이 있으면
        최대한 캐스팅하고 안되면 없애버림.
        :param item:
        :param sort_keys:
        :return:
        """
        item = item.copy()
        for sort_key_item in sort_keys:
            sort_key = sort_key_item.get('sort_key', None)
            sort_key_type = sort_key_item.get('sort_key_type', None)
            if sort_key and sort_key_type and sort_key in item:
                item_value = item.get(sort_key, None)
                try:
                    if sort_key_type == 'S':
                        item[sort_key] = str(item_value)
                    if sort_key_type == 'N':
                        if isinstance(item_value, str):
                            item_value = float(item_value)
                        item[sort_key] = Decimal(item_value)
                except Exception as ex:
                    # 형변환 실패시 아예 넣지 않음
                    print(ex)
                    item.pop(sort_key)
        return item

    def _put_inverted_query(self, table_name, partition, item, index_keys=None, target_fields=None, sort_keys=None):
        table = self.resource.Table(table_name)
        item_id = item.get('id')
        creation_date = item.get('creation_date', None)
        if not creation_date:
            creation_date = self.time()
        if not sort_keys:
            sort_keys = []
        sort_key_pairs = {}
        for sort_key_item in sort_keys:
            sort_key = sort_key_item.get('sort_key', None)
            if sort_key:
                item_value = item.get(sort_key, None)
                if item_value is not None:
                    sort_key_pairs[sort_key] = item_value

        with table.batch_writer() as batch:
            for field, value in item.items():
                for operand in self._eq_operands(value):
                    self._put_inverted_query_field(batch, partition, field, operand, 'eq', item_id, creation_date, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)
                for operand_ins in self._ins_operands(value):
                    self._put_inverted_query_field(batch, partition, field, operand_ins, 'ins', item_id, creation_date, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)
                self._put_deep_inverted_query(batch, partition, item_id, creation_date, field, value, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)

    def _put_deep_inverted_query(self, batch, partition, item_id, creation_date, field, value, index_keys=None, target_fields=None, sort_key_pairs=None):
        if sort_key_pairs is None:
            sort_key_pairs = {}
        if isinstance(value, dict):
            for field2, value2 in value.items():
                for operand2 in self._eq_operands(value2):
                    # key.key2 eq val 와 같이 사용 할 수 있도록
                    self._put_inverted_query_field(batch, partition, '{}.{}'.format(field, field2), operand2, 'eq',
                                                   item_id, creation_date, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)
                for operand2_ins in self._ins_operands(value2):
                    self._put_inverted_query_field(batch, partition, '{}.{}'.format(field, field2), operand2_ins, 'ins',
                                                   item_id, creation_date, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)

                self._put_deep_inverted_query(batch, partition, item_id, creation_date, '{}.{}'.format(field, field2),
                                              value2, index_keys=index_keys, target_fields=target_fields, sort_key_pairs=sort_key_pairs)


    def _put_inverted_query_field(self, table, partition, field, operand, operation, item_id, creation_date, index_keys=None, target_fields=None, sort_key_pairs=None):
        advanced_index_operations = ['ins']
        if len(str(operand)) > 256:
            return False
        if isinstance(index_keys, list):
            has_key = False
            for index_key in index_keys:
                if isinstance(index_key, str) and index_key == field and operation not in advanced_index_operations:  # 일반 인덱싱
                    has_key = True
                if isinstance(index_key, tuple) and index_key == (field, operation):  # 고급 인덱싱 / 풀텍스트 등
                    has_key = True
            if not has_key:
                return False
        elif operation in advanced_index_operations:
            return False  # 고급 인덱싱은 인덱스 리스트에 포함되어있어야 인덱싱.

        if target_fields is not None:
            if field not in target_fields:
                return False
        _inverted_query = '{}-{}-{}-{}'.format(partition, field, operand, operation)
        query = {
            'id': 'query-{}'.format(shortuuid.uuid()),
            'partition': 'index-{}'.format(item_id),
            'inverted_query': _inverted_query,
            'creation_date': creation_date,
            'item_id': item_id,
        }
        # 소트 키 전달시 소트 키 삽입.. 딕셔너리
        if sort_key_pairs:
            for sort_key, sort_value in sort_key_pairs.items():
                if sort_key not in query:
                    if sort_value:  # 벨류가 있을시에만..
                        query[sort_key] = sort_value

        count = 0
        while count < 3:
            count += 1
            try:
                response = table.put_item(
                    Item=query,
                )
                return response
            except Exception as ex:
                print(ex)
                time.sleep(0.5 * count)

    def _delete_inverted_query(self, table_name, partition, item_id, target_fields=None):
        min_creation_date = 0  # 인덱스 삭제할때 sort_key 구하기.. 효율을 위해
        table = self.resource.Table(table_name)
        items = self.get_items_in_partition(table_name, 'index-{}'.format(item_id), limit=maxsize).get('Items', [])
        with table.batch_writer() as batch:
            for item in items:
                inverted_query = item.get('inverted_query', None)
                creation_date = item.get('creation_date', 0)
                min_creation_date = min(min_creation_date, creation_date)
                # Target fields 에 있는 필드만
                is_target = True
                if target_fields is not None:
                    is_target = False
                    for target_field in target_fields:
                        prefix = '{}-{}-'.format(partition, target_field)
                        if inverted_query.startswith(prefix):
                            is_target = True
                            break
                if is_target:
                    inverted_query_id = item.get('id', None)
                    count = 0
                    while count < 3:
                        count += 1
                        try:
                            batch.delete_item(
                                Key={
                                    'id': inverted_query_id
                                }
                            )
                            break
                        except Exception as ex:
                            print(ex)
                            time.sleep(0.5 * count)
        return min_creation_date


class DynamoFDB:
    def __init__(self, boto3_session, app_id):
        # TODO 작동안될수도 있으니 조심
        dynamo_config = botocore.client.Config(max_pool_connections=100)
        self.client = boto3_session.client('dynamodb', config=dynamo_config)
        self.resource = boto3_session.resource('dynamodb', config=dynamo_config)
        self.table_cache = {}
        self.app_id = app_id
        self.table_name = f'FDB_{app_id}'

    def init_fdb_table(self):
        self.create_fdb_table(self.table_name)
        # self.create_fdb_partition_index(self.table_name)

    def create_fdb_table(self, table_name):
        """
        fdb 용 테이블 생성문입니다.
        :param table_name:
        :return:
        """
        try:
            response = self.client.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': '_pk',
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': '_sk',
                        'AttributeType': 'S'
                    }
                ],
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': '_pk',
                        'KeyType': 'HASH'
                    }, {
                        'AttributeName': '_sk',
                        'KeyType': 'RANGE'
                    },
                ],
                BillingMode='PAY_PER_REQUEST',
                StreamSpecification={
                    'StreamEnabled': True,
                    'StreamViewType': 'NEW_AND_OLD_IMAGES'
                },
            )
            print('CREATING FDB TABLE...')
            self.client.get_waiter('table_exists').wait(TableName=table_name)
            return response
        except Exception as ex:
            print(ex)
            return True

    def create_fdb_partition_index(self, table_name, index_name, pk_name, sk_name):
        """
        fdb 용 파티션 쿼리 전용 인덱스 생성문입니다.
        :param table_name:
        :return:
        """
        try:
            response = self.client.update_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': pk_name,
                        'AttributeType': 'S'
                    }, {
                        'AttributeName': sk_name,
                        'AttributeType': 'S'
                    }
                ],
                TableName=table_name,
                GlobalSecondaryIndexUpdates=[
                    {
                        'Create': {
                            'IndexName': index_name,
                            'KeySchema': [
                                {
                                    'AttributeName': pk_name,
                                    'KeyType': 'HASH'
                                }, {
                                    'AttributeName': sk_name,
                                    'KeyType': 'RANGE'
                                },
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL',
                            },
                        },
                    }
                ]
            )
            print('UPDATE FDB TABLE INDEX...')
            return response
        except Exception as ex:
            print(ex)
            return True

    def delete_fdb_table(self):
        try:
            response = self.client.delete_table(
                TableName=self.table_name
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def delete_item(self, pk, sk):
        response = self.get_table(self.table_name).delete_item(
            Key={
                '_pk': pk,
                '_sk': sk
            }
        )
        return response

    def get_table(self, table_name):
        # 캐싱된 테이블 객체 반환
        if table_name in self.table_cache:
            table = self.table_cache[table_name]
        else:
            table = self.resource.Table(table_name)
            self.table_cache[table_name] = table
        return table

    def get_item(self, pk, sk):
        table = self.get_table(self.table_name)
        key = {
            '_pk': pk,
            '_sk': sk
        }
        response = table.get_item(Key=key)
        item = response.get('Item', None)
        return item

    def put_item(self, item):
        table = self.get_table(self.table_name)
        # 디비에 넣기전에 인덱스 타입을 고려하여 데이터를 변경한다.
        response = table.put_item(
            Item=item,
        )
        return response

    def get_update_expression_attrs_pair(self, item):
        """
        item 에서 업데이트 표현식과 속성을 튜플로 반환합니다.
        :param item:
        :return: (UpdateExpression, ExpressionAttributeValues)
        """
        expression = 'set'
        attr_names = {}
        attr_values = {}
        for idx, (key, value) in enumerate(item.items()):
            attr_key = '#key{}'.format(idx)
            attr_value = ':val{}'.format(idx)
            expression += ' {}={}'.format(attr_key, attr_value)

            attr_names['{}'.format(attr_key)] = key
            attr_values['{}'.format(attr_value)] = value
            if idx != len(item) - 1:
                expression += ','
        return expression, attr_names, attr_values

    def update_item(self, pk, sk, item):
        expression, attr_names, attr_values = self.get_update_expression_attrs_pair(item)
        response = self.get_table(self.table_name).update_item(
            Key={'_pk': pk, '_sk': sk},
            UpdateExpression=expression,
            ExpressionAttributeValues=attr_values,
            ExpressionAttributeNames=attr_names,
            ReturnValues="ALL_NEW",
        )
        return response

    def batch_put(self, items):
        table = self.get_table(self.table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(
                    Item=item,
                )
        return True

    def batch_delete(self, pk_sk_pairs):
        """
        :param pk_sk_pairs: [
            {
                'pk': '...',
                'sk': '...'
            }, ...
        ]
        :return:
        """
        table = self.get_table(self.table_name)
        with table.batch_writer() as batch:
            for pk_sk_pair in pk_sk_pairs:
                key = {
                    '_pk': pk_sk_pair['_pk'],
                    '_sk': pk_sk_pair['_sk']
                }
                batch.delete_item(Key=key)
        return True

    def _get_items(self, pk_sk_pairs, consistent_read=False, retry_attempt=0):
        keys = list([{
            '_pk': {'S': pk_sk_pair['_pk']},
            '_sk': {'S': pk_sk_pair['_sk']}
        } for pk_sk_pair in pk_sk_pairs if pk_sk_pair])
        if keys:
            response = self.client.batch_get_item(
                RequestItems={
                    self.table_name: {
                        'Keys': keys,
                        'ConsistentRead': consistent_read
                    }
                }
            )

            items_succeed = response['Responses'][self.table_name]

            # response 제대로 안왔을때 재시도 로직
            unprocessed_keys = response.get('UnprocessedKeys', {}).get(self.table_name, {}).get('Keys', [])
            if unprocessed_keys:
                # Backoff al.
                time.sleep(pow(retry_attempt + 1, 2))
                items_to_extend = self._get_items(unprocessed_keys, consistent_read, retry_attempt + 1)
                items_succeed.extend(items_to_extend)
        else:  # Keys 가 없을시 성공 내역 없음
            items_succeed = []

        for item in items_succeed:
            for key, value in item.items():
                value = type_deserializer.deserialize(value)
                item[key] = value

        return items_succeed

    def get_items(self, pk_sk_pairs, consistent_read=False):
        chunks = list(divide_chunks(pk_sk_pairs, 100))
        items_succeed = []
        futures = []
        # 배치 + 멀티스레드로 가져옵니다.
        with ThreadPoolExecutor(max_workers=len(chunks)) as worker:
            for chunk in chunks:
                futures.append(worker.submit(self._get_items, chunk, consistent_read))
        for future in futures:
            items_succeed.extend(future.result())

        # 요청한 순서대로 정렬합니다.
        items_by_key = {(item.get('_pk', ''), item.get('_sk', '')): item for item in items_succeed}
        sorted_items = []
        for pk_sk in pk_sk_pairs:
            if pk_sk:
                item = items_by_key.get((pk_sk['_pk'], pk_sk['_sk']), None)
                sorted_items.append(item)
            else:
                sorted_items.append(None)
        return sorted_items

    def query_items(self, partition_key_name, partition_key_value,
                    sort_condition, sort_key_name, sort_key_value, sort_key_second_value=None, filters=None,
                    start_key=None, reverse=False, limit=100, consistent_read=False, index_name=None):
        """
        AWS BOTO3 전용으로 쿼리 메서드 랩핑
        :param partition_key_name: 파티션키 속성의 이름
        :param partition_key_value: 파티션키 속성의 값
        :param sort_condition: 소트키 조건
        :param sort_key_name:
        :param sort_key_value:
        :param sort_key_second_value:
        :param filters: [
            {
                'field': '<FIELD>',
                'value': '<VALUE>',
                'condition': 'eq' | 'neq' | 'lte' | 'lt' | 'gte' | 'gt' | 'btw' | 'stw' |
                        'is_in' | 'contains' | 'exist' | 'not_exist'
            }
        ]
        :param start_key:
        :param reverse:
        :param limit:
        :param consistent_read:
        :param index_name:
        :return:
        """
        table = self.get_table(self.table_name)
        key_expression = Key(partition_key_name).eq(partition_key_value)
        if sort_condition == 'eq':
            key_expression &= Key(sort_key_name).eq(sort_key_value)
        elif sort_condition == 'lte':
            key_expression &= Key(sort_key_name).lte(sort_key_value)
        elif sort_condition == 'lt':
            key_expression &= Key(sort_key_name).lt(sort_key_value)
        elif sort_condition == 'gte':
            key_expression &= Key(sort_key_name).gte(sort_key_value)
        elif sort_condition == 'gt':
            key_expression &= Key(sort_key_name).gt(sort_key_value)
        elif sort_condition == 'btw':
            key_expression &= Key(sort_key_name).between(sort_key_value, sort_key_second_value)
        elif sort_condition == 'stw':
            key_expression &= Key(sort_key_name).begins_with(sort_key_value)
        elif sort_condition is None:
            pass
        else:
            raise Exception('sort_type must be one of [eq, lte, lt, gte, gt, btw, stw]')

        filter_expression = None
        if filters:
            for ft in filters:
                field = ft['field']
                value = ft.get('value', None)
                high_value = ft.get('second_value', None)
                cond = ft['condition']

                attr_to_add = Attr(field)
                if cond == 'eq':
                    attr_to_add = attr_to_add.eq(value)
                elif cond == 'neq':
                    attr_to_add = attr_to_add.ne(value)
                elif cond == 'lte':
                    attr_to_add = attr_to_add.lte(value)
                elif cond == 'lt':
                    attr_to_add = attr_to_add.lt(value)
                elif cond == 'gte':
                    attr_to_add = attr_to_add.gte(value)
                elif cond == 'gt':
                    attr_to_add = attr_to_add.gt(value)
                elif cond == 'btw':
                    attr_to_add = attr_to_add.between(value, high_value)
                elif cond == 'stw':
                    attr_to_add = attr_to_add.begins_with(value)
                elif cond == 'is_in':
                    attr_to_add = attr_to_add.is_in(value)
                elif cond == 'contains':
                    attr_to_add = attr_to_add.contains(value)
                elif cond == 'exist':
                    attr_to_add = attr_to_add.exists()
                elif cond == 'not_exist':
                    attr_to_add = attr_to_add.not_exists()
                else:
                    raise Exception('<condition> parameter must be one of ['
                                    'eq, neq, lte, lt, gte, gt, btw, stw, is_in, contains, exist, not_exist'
                                    ']')
                if filter_expression:
                    filter_expression &= attr_to_add
                else:
                    filter_expression = attr_to_add
        args = {
            'Limit': limit,
            'ConsistentRead': consistent_read,
            'KeyConditionExpression': key_expression,
            'ScanIndexForward': not reverse,
        }
        if index_name:
            args['IndexName'] = index_name
            args['ConsistentRead'] = False  # index 사용시 일관된 읽기는 사용 불가
        if filter_expression:
            args['FilterExpression'] = filter_expression
        if start_key:
            args['ExclusiveStartKey'] = start_key

        response = table.query(**args)
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
            Timeout=899,
            MemorySize=5120,
            Publish=True,
            TracingConfig={
                'Mode': 'Active'
            },
        )
        return response

    def update_function_code(self, name, zip_file):
        response = self.client.update_function_code(
            FunctionName=name,
            ZipFile=zip_file,
            Publish=True
        )
        return response

    def update_function_memory_size(self, name, memory_size):
        response = self.client.update_function_configuration(
            FunctionName=name,
            MemorySize=memory_size,
        )
        return response

    def delete_function(self, name):
        try:
            response = self.client.delete_function(
                FunctionName=name,
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def invoke_function(self, name, payload_bytes):
        response = self.client.invoke(
            FunctionName=name,
            InvocationType='RequestResponse',
            Payload=payload_bytes,
        )
        return response

    def get_function(self, name):
        response = self.client.get_function(
            FunctionName=name,
        )
        return response

    def add_permission(self, function_name, statement_id, action, principal, source_arn):
        response = self.client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action=action,
            Principal=principal,
            SourceArn=source_arn,
        )
        return response

    def remove_permission(self, function_name, statement_id):
        response = self.client.remove_permission(
            FunctionName=function_name,
            StatementId=statement_id,
        )
        return response


class S3:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('s3')
        self.resource = boto3_session.resource('s3')
        self.region = boto3_session.region_name

    @classmethod
    def to_dns_name(cls, bucket_name):
        def f(c):
            if c.isupper():
                return 'c.{}'.format(c.lower())
            else:
                return c
        bucket_name = [f(c) for c in bucket_name]
        bucket_name = ''.join(bucket_name)
        return bucket_name

    def init_bucket(self, bucket_name):
        self.create_bucket(bucket_name)

    def create_bucket(self, bucket_name):
        try:
            bucket_name = self.to_dns_name(bucket_name)
            response = self.client.create_bucket(
                ACL='private',
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.region
                },
            )
            return response
        except botocore.exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print('Pass: [{}]'.format(ex))
            else:
                raise ex

    def upload_bin(self, bucket_name, file_name, binary):
        bucket_name = self.to_dns_name(bucket_name)
        with tempfile.TemporaryFile() as tmp:
            tmp.write(binary)
            tmp.seek(0)
            response = self.client.upload_fileobj(tmp, bucket_name, file_name)
            return response

    def delete_bin(self, bucket_name, file_name):
        bucket_name = self.to_dns_name(bucket_name)
        return self.resource.Object(bucket_name, file_name).delete()

    def download_bin(self, bucket_name, file_name):
        bucket_name = self.to_dns_name(bucket_name)
        try:
            with tempfile.NamedTemporaryFile() as data:
                self.client.download_fileobj(bucket_name, file_name, data)
                data.seek(0)
                return data.read()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
                return None
            else:
                raise

    def delete_bucket(self, bucket_name):
        try:
            bucket_name = self.to_dns_name(bucket_name)
            response = self.client.delete_bucket(
                Bucket=bucket_name
            )
            return response
        except BaseException as ex:
            print(ex)
            return None


class IAM:
    policy_arns = [
        'arn:aws:iam::aws:policy/AWSLambdaExecute',
        'arn:aws:iam::aws:policy/AWSLambda_FullAccess',
        'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
        'arn:aws:iam::aws:policy/AmazonS3FullAccess',
        'arn:aws:iam::aws:policy/AWSXrayFullAccess',
    ]

    def __init__(self, boto3_session):
        self.client = boto3_session.client('iam')
        self.resource = boto3_session.resource('iam')

    def create_role_and_attach_policies(self, role_name):
        self.create_role(role_name)
        self.attach_policies(role_name, self.policy_arns)
        return self.get_role_arn(role_name)

    def get_role_arn(self, role_name):
        role = self.resource.Role(role_name)
        role_arn = role.arn
        return role_arn

    def delete_role(self, role_name):
        try:
            response = self.client.delete_role(
                RoleName=role_name
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

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
        try:
            response = self.client.create_role(
                Path='/',
                RoleName=role_name,
                AssumeRolePolicyDocument=assume_role_policy_document,
            )
        except:
            print('Already have a role', role_name)
            return None
        return response

    def attach_policies(self, role_name, policy_arns):
        for policy_arn in policy_arns:
            self.attach_policy(role_name, policy_arn)

    def attach_policy(self, role_name, policy_arn):
        try:
            response = self.client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        except Exception as e:
            print('Failed to attach policy: {} by: {}'.format(role_name, e))
            return None
        return response

    def detach_all_policies(self, role_name):
        for policy_arn in self.policy_arns:
            self.detach_policy(role_name, policy_arn)

    def detach_policy(self, role_name, policy_arn):
        try:
            response = self.client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            return response
        except BaseException as ex:
            print(ex)
            return None

    def get_account_id(self):
        account_id = self.resource.CurrentUser().arn.split(':')[4]
        return account_id


class CostExplorer:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('ce')

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


class Events:
    def __init__(self, boto3_session):
        self.client = boto3_session.client('events')

    def put_rule(self, name, schedule_expression):
        response = self.client.put_rule(
            Name=name,
            ScheduleExpression=schedule_expression,
            State='ENABLED',
        )
        return response

    def put_target(self, target_id, rule_name, target_arn, target_input):
        response = self.client.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': target_id,
                    'Arn': target_arn,
                    'Input': target_input,
                },
            ]
        )
        return response

    def get_rules(self, name, next_token=None):
        if next_token:
            response = self.client.list_rules(
                NamePrefix=name,
                NextToken=next_token,
                Limit=1000
            )
        else:
            response = self.client.list_rules(
                NamePrefix=name,
                Limit=1000
            )
        return response

    def get_targets(self, rule_name, next_token=None):
        if next_token:
            response = self.client.list_targets_by_rule(
                Rule=rule_name,
                NextToken=next_token,
                Limit=100
            )
        else:
            response = self.client.list_targets_by_rule(
                Rule=rule_name,
                Limit=100
            )
        return response

    def delete_rule(self, name):
        response = self.client.delete_rule(
            Name=name,
            Force=True
        )
        return response

    def delete_targets(self, rule_name, target_ids):
        response = self.client.remove_targets(
            Rule=rule_name,
            Ids=target_ids,
            Force=True
        )
        return response


class SNS:
    def __init__(self, boto3_session, region='us-east-1'):
        self.client = boto3_session.client('sns', region_name=region)

    def send_message(self, phone_number, message):
        return self.client.publish(PhoneNumber=phone_number, Message=message)


if __name__ == '__main__':
    pass