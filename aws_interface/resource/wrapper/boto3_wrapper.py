import json
import time
import tempfile
import botocore

from boto3.dynamodb.conditions import Key, GreaterThanEquals, LessThanEquals
from boto3.dynamodb.types import TypeDeserializer
from sys import maxsize
from decimal import Decimal
import cloud.shortuuid as shortuuid


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
            'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With\'',
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
        self.put_integration(rest_api_id, resource_id, 'OPTIONS', uri)
        self.put_integration_response(rest_api_id, resource_id, 'OPTIONS', integration_response_param)

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

    def put_integration(self, rest_api_id, resource_id, method_type, uri):
        integration_resp = self.client.put_integration(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod=method_type,
            type="AWS",
            integrationHttpMethod=method_type,
            uri=uri,
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
        self.client = boto3_session.client('dynamodb')
        self.resource = boto3_session.resource('dynamodb')

    def init_table(self, table_name):
        self.create_table(table_name)

    def create_table(self, table_name):
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
                        'AttributeName': 'creation_date',
                        'AttributeType': 'N'
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
                        'IndexName': 'partition-creation_date',
                        'KeySchema': [
                            {
                                'AttributeName': 'partition',
                                'KeyType': 'HASH'
                            }, {
                                'AttributeName': 'creation_date',
                                'KeyType': 'RANGE'
                            },
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }, {
                        'IndexName': 'inverted_query-creation_date',
                        'KeySchema': [
                            {
                                'AttributeName': 'inverted_query',
                                'KeyType': 'HASH'
                            }, {
                                'AttributeName': 'creation_date',
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
            self.update_table(table_name, {'hash_key': 'partition', 'hash_key_type': 'S',
                                           'sort_key': 'creation_date', 'sort_key_type': 'N'})
            self.update_table(table_name, {'hash_key': 'inverted_query', 'hash_key_type': 'S',
                                           'sort_key': 'creation_date', 'sort_key_type': 'N'})
            return None

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

        while True:
            try:
                response = self.client.update_table(
                    AttributeDefinitions=attr_updates,
                    TableName=table_name,
                    GlobalSecondaryIndexUpdates=index_updates
                )
                return response
            except Exception as e:
                print(e)
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
        self._delete_inverted_query(table_name, item_id)
        return response

    def get_item(self, table_name, item_id):
        table = self.resource.Table(table_name)
        item = table.get_item(Key={
            'id': item_id
        })
        return item

    def time(self):
        return Decimal("%.20f" % time.time())

    def put_item(self, table_name, partition, item, item_id=None, creation_date=None, indexing=True):
        if not item_id:
            item_id = str(shortuuid.uuid())
        if not creation_date:
            creation_date = self.time()
        table = self.resource.Table(table_name)
        item['id'] = item_id
        item['creation_date'] = creation_date
        item['partition'] = partition
        response = table.put_item(
            Item=item,
        )
        self._add_item_count(table_name, '{}-count'.format(partition))
        if indexing:
            self._delete_inverted_query(table_name, item_id)
            self._put_inverted_query(table_name, partition, item)
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
        type_deserializer = TypeDeserializer()
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
            key_expression = key_expression & Key(order_by).gte(order_min)
        elif order_max:
            key_expression = key_expression & Key(order_by).lte(order_max)
        response = self.get_items_with_key_expression(table_name, index_name, key_expression, start_key, limit,
                                                      reverse)
        return response


    def get_inverted_queries(self, table_name, partition, field, operand, operation, order_by, order_min, order_max, start_key=None, limit=100, reverse=False):
        if operation == 'in' or operation == 'eq':
            hash_key_name = 'inverted_query'
            sort_key_name = '{}'.format(order_by)
            hash_key = '{}-{}-{}-{}'.format(partition, field, operand, operation)
            index_name = '{}-{}'.format(hash_key_name, sort_key_name)
            key_expression = Key(hash_key_name).eq(hash_key)
            if order_min:
                key_expression = key_expression & Key(sort_key_name).gte(order_min)
            elif order_max:
                key_expression = key_expression & Key(sort_key_name).lte(order_max)
            try:
                response = self.get_items_with_key_expression(table_name, index_name, key_expression, start_key, limit,
                                                          reverse)
            except Exception as ex:
                print(ex)
                response = {'Items': []}
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
                    start_key[key] = Decimal(start_key[key])

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

    def update_item(self, table_name, item_id, item):
        table = self.resource.Table(table_name)
        item['id'] = item_id
        response = table.put_item(
            TableName=table_name,
            Item=item,
        )
        partition = item.get('partition')
        self._delete_inverted_query(table_name, item_id)
        self._put_inverted_query(table_name, partition, item)
        return response

    def _put_item_count(self, table_name, count_id, value):
        response = self.put_item(table_name, 'meta_info', {'count': value}, item_id=count_id)
        return response

    def _add_item_count(self, table_name, count_id, value_to_add=1):
        response = self.client.update_item(
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
            ReturnValues='ALL_NEW',
            TableName=table_name,
            UpdateExpression='ADD #A :v',
        )
        return response

    def get_item_count(self, table_name, count_id):
        response = self.get_item(table_name, count_id)
        return response

    def _eq_operands(self, value):
        value = str(value)
        return [value]

    def _put_inverted_query(self, table_name, partition, item):
        table = self.resource.Table(table_name)
        item_id = item.get('id')
        creation_date = item.get('creation_date', self.time())
        with table.batch_writer() as batch:
            for field, value in item.items():
                for operand in self._eq_operands(value):
                    self._put_inverted_query_field(batch, partition, field, operand, 'eq', item_id, creation_date)

    def _put_inverted_query_field(self, table, partition, field, operand, operation, item_id, creation_date):
        _inverted_query = '{}-{}-{}-{}'.format(partition, field, operand, operation)
        query = {
            'id': 'query-{}'.format(shortuuid.uuid()),
            'partition': 'index-{}'.format(item_id),
            'inverted_query': _inverted_query,
            'creation_date': creation_date,
            'item_id': item_id,
        }
        response = table.put_item(
            Item=query,
        )
        return response

    def _delete_inverted_query(self, table_name, item_id):
        table = self.resource.Table(table_name)
        items = self.get_items_in_partition(table_name, 'index-{}'.format(item_id), limit=maxsize).get('Items', [])
        with table.batch_writer() as batch:
            for item in items:
                inverted_query_id = item.get('id', None)
                batch.delete_item(
                    Key={
                        'id': inverted_query_id
                    }
                )


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
            MemorySize=1024,
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
        try:
            self.create_bucket(bucket_name)
            print('create_bucket success')
        except Exception as ex:
            print(ex)

    def create_bucket(self, bucket_name):
        bucket_name = self.to_dns_name(bucket_name)
        response = self.client.create_bucket(
            ACL='private',
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': self.region
            },
        )
        return response

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
