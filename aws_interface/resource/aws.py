import importlib
import os
import shutil
import tempfile
import json
import time
import uuid
from decimal import Decimal
from numbers import Number
from resource.wrapper.boto3_wrapper import get_boto3_session, Lambda, APIGateway, IAM, DynamoDB, CostExplorer, S3, Events, SNS
from resource.wrapper.boto3_wrapper import DynamoFDB
from resource.base import ResourceAllocator, Resource
from resource import config, util
from zipfile import ZipFile
import base64


def encode_dict(dict_obj):
    def cast_number(v):
        if isinstance(v, dict):
            return encode_dict(v)
        if isinstance(v, list):
            return encode_dict(v)
        if not isinstance(v, Number):
            return v
        if v % 1 == 0:
            return int(v)
        else:
            return float(v)

    if isinstance(dict_obj, dict):
        return {k: cast_number(v) for k, v in dict_obj.items()}
    elif isinstance(dict_obj, list):
        return [cast_number(v) for v in dict_obj]
    else:
        return dict_obj


def decode_dict(dict_obj):
    def cast_number(v):
        if isinstance(v, dict):
            return decode_dict(v)
        if isinstance(v, list):
            return decode_dict(v)
        if isinstance(v, float):
            return Decimal(str(v))
        else:
            return v

    if isinstance(dict_obj, dict):
        return {k: cast_number(v) for k, v in dict_obj.items()}
    elif isinstance(dict_obj, list):
        return [cast_number(v) for v in dict_obj]
    else:
        return dict_obj


def create_lambda_zipfile_bin(app_id, cloud_path, resource_path):
    output_filename = tempfile.mktemp()
    cloud_name = 'cloud'
    resource_name = 'resource'
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy lambda dir into temp/root_name folder
        shutil.copytree(cloud_path, '{}/{}'.format(tmp_dir, cloud_name))
        shutil.copytree(resource_path, '{}/{}'.format(tmp_dir, resource_name))

        # Write txt file included app_id
        with open(os.path.join(tmp_dir, cloud_name, 'app_id.txt'), 'w+') as file:
            file.write(app_id)

        # Archive all files
        shutil.make_archive(output_filename, 'zip', tmp_dir)
        zip_file_name = '{}.zip'.format(output_filename)
        zip_file = open(zip_file_name, 'rb')
        zip_file_bin = zip_file.read()
        zip_file.close()

    # Remove temp files
    os.remove(zip_file_name)
    return zip_file_bin


class AWSResourceAllocator(ResourceAllocator):
    def __init__(self, credential, app_id):
        super(AWSResourceAllocator, self).__init__(credential, app_id)
        self.boto3_session = get_boto3_session(credential)

    def create(self):
        self._create_bucket()
        self._create_dynamo_db_table()
        self._create_lambda_function()
        self._create_rest_api_connection()
        self._create_dynamo_fdb_table()

    def terminate(self):
        self._remove_bucket()
        self._remove_dynamo_db_table()
        self._remove_lambda_function()
        self._remove_rest_api_connection()
        self._remove_dynamo_fdb_table()

    def get_rest_api_url(self):
        api_gateway = APIGateway(self.boto3_session)
        return api_gateway.get_rest_api_url(self.app_id)

    def _create_dynamo_db_table(self):
        dynamo = DynamoDB(self.boto3_session)
        dynamo.init_table(self.app_id)

    def _create_dynamo_fdb_table(self):
        dynamo = DynamoFDB(self.boto3_session, self.app_id)
        dynamo.init_fdb_table()

    def _create_lambda_function(self):
        """
        Create or Update An AWS Lambda function
        :return:
        """
        print('[{}] apply_cloud_api: START'.format(self.app_id))
        role_name = '{}'.format(self.app_id)
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)

        role_arn = iam.create_role_and_attach_policies(role_name)

        name = '{}'.format(self.app_id)
        desc = 'aws-interface cloud API'
        runtime = 'python3.6'
        handler = 'cloud.lambda_function.aws_handler'

        cloud_module_name = 'cloud'
        cloud_module = importlib.import_module(cloud_module_name)
        cloud_module_path = os.path.dirname(cloud_module.__file__)

        resource_module_name = 'resource'
        resource_module = importlib.import_module(resource_module_name)
        resource_module_path = os.path.dirname(resource_module.__file__)

        zip_file = create_lambda_zipfile_bin(self.app_id, cloud_module_path, resource_module_path)

        try:
            lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file)
        except BaseException as ex:
            print(ex)
            lambda_client.update_function_code(name, zip_file)

    def _create_rest_api_connection(self):
        api_name = '{}'.format(self.app_id)
        func_name = '{}'.format(self.app_id)
        api_gateway = APIGateway(self.boto3_session)
        api_gateway.connect_with_lambda(api_name, func_name)

    def _create_bucket(self):
        s3 = S3(self.boto3_session)
        s3.create_bucket(self.app_id)

    def _remove_dynamo_db_table(self):
        dynamo = DynamoDB(self.boto3_session)
        dynamo.delete_table(self.app_id)

    def _remove_lambda_function(self):
        resource_name = '{}'.format(self.app_id)
        lambda_client = Lambda(self.boto3_session)
        lambda_client.delete_function(resource_name)

    def _remove_rest_api_connection(self):
        resource_name = '{}'.format(self.app_id)
        api_client = APIGateway(self.boto3_session)
        iam = IAM(self.boto3_session)
        api_client.delete_rest_api_by_name(resource_name)
        iam.detach_all_policies(resource_name)
        iam.delete_role(resource_name)

    def _remove_bucket(self):
        s3 = S3(self.boto3_session)
        s3.delete_bucket(self.app_id)

    def _remove_dynamo_fdb_table(self):
        dynamo = DynamoFDB(self.boto3_session, self.app_id)
        dynamo.delete_fdb_table()


class AWSResource(Resource):
    def __init__(self, credential, app_id, boto3_session=None):
        super(AWSResource, self).__init__(credential, app_id)
        if boto3_session:
            self.boto3_session = boto3_session
        elif credential:
            self.boto3_session = get_boto3_session(credential)
        self.dynamo = DynamoDB(self.boto3_session)
        self.dynamoFDB = DynamoFDB(self.boto3_session, app_id)
        self.s3 = S3(self.boto3_session)
        self.cache = {}

    def get_rest_api_url(self):
        api_gateway = APIGateway(self.boto3_session)
        return api_gateway.get_rest_api_url(self.app_id)

    def create_webhook_url(self, name):
        url = '{}?webhook={}'.format(self.get_rest_api_url(), name)
        return url

    # backend resource cost
    def cost_for(self, start, end):
        cost_exp = CostExplorer(self.boto3_session)
        return cost_exp.get_cost(start, end)

    def cost_and_usage_for(self, start, end):
        cost_exp = CostExplorer(self.boto3_session)
        return cost_exp.get_cost_and_usage(start, end)

    # DB ops
    def db_create_partition(self, partition):
        response = self.dynamo.create_partition(self.app_id, partition)
        return bool(response)

    def db_delete_partition(self, partition):
        response = self.dynamo.delete_partition(self.app_id, partition)
        return bool(response)

    def db_has_partition(self, partition):
        response = self.dynamo.get_partition(self.app_id, partition)
        return bool(response)

    def db_get_partitions(self):
        response = self.dynamo.get_partitions(self.app_id)
        items = response.get('Items', [])
        return items

    def db_delete_item(self, item_id):
        result = self.dynamo.delete_item(self.app_id, item_id)
        return bool(result)

    def db_delete_item_batch(self, item_ids):
        result = True
        for item_id in item_ids:
            result &= bool(self.dynamo.delete_item(self.app_id, item_id))
        return result

    def db_get_item(self, item_id, projection_keys=None):
        """
        Projection keys 가 있으면, projection_keys 만 반환.
        :param item_id:
        :param projection_keys:
        :return:
        """
        item = self.dynamo.get_item(self.app_id, item_id, projection_keys=projection_keys)
        return item.get('Item', None)

    def db_get_items(self, item_ids):
        result = self.dynamo.get_items(self.app_id, item_ids)
        return result.get('Items', [])

    def _remove_blanks(self, it):
        if isinstance(it, dict):
            it = {key: self._remove_blanks(value) for key, value in it.items() if value != '' and value != {} and value != []}
            return it
        elif isinstance(it, list):
            it = [self._remove_blanks(i) for i in it]
            return it
        else:
            if it == '':
                return None
            else:
                return it

    def db_put_item(self, partition, item, item_id=None, creation_date=None, index_keys=None, sort_keys=None):
        item = decode_dict(item)
        item = self._remove_blanks(item)
        result = self.dynamo.put_item(self.app_id, partition, item, item_id, creation_date, index_keys=index_keys, sort_keys=sort_keys)
        return bool(result)

    def db_update_item(self, item_id, item, index_keys=None, sort_keys=None):
        item = decode_dict(item)
        result = self.dynamo.update_item(self.app_id, item_id, item, index_keys=index_keys, sort_keys=sort_keys)
        return bool(result)

    def db_update_item_v2(self, item_id, item, index_keys=None, sort_keys=None):
        item = decode_dict(item)
        result = self.dynamo.update_item_v2(self.app_id, item_id, item, index_keys=index_keys, sort_keys=sort_keys)
        return bool(result)

    def db_get_count(self, partition, field=None, value=None):
        """
        Returns the number of items that satisfy the condition field == value
        :param partition: Partition to count
        :param field: Field name to check out
        :param value: Field value to find out
        :return:
        """
        if field and value:
            count_id = '{}-{}-{}-count'.format(partition, field, value)
        else:
            count_id = '{}-count'.format(partition)
        item = self.dynamo.get_item_count(self.app_id, count_id).get('Item', {'count': 0})
        count = item.get('count')
        return count

    def get_end_key_indexing(self, item, order_by):
        """
        인덱싱할때 페이지네이션 키
        :param item:
        :param order_by:
        :return:
        """
        return self.get_end_key(item, order_by, 'inverted_query')

    def get_end_key_scan(self, item, order_by):
        """
        스캔시 페이지네이션 키
        :param item:
        :param order_by:
        :return:
        """
        return self.get_end_key(item, order_by)

    def get_end_key(self, item, order_by, index_key='partition'):
        if not item:
            return item
        if item.get('id', None) is None:
            return None
        end_key = {
            'id': item['id'],
            order_by: item.get(order_by, 0),
            index_key: item.get(index_key, None)
        }

        if isinstance(item.get(order_by, 0), int) or isinstance(item.get(order_by, 0), float) or isinstance(item.get(order_by, 0), Decimal):
            end_key[order_by] = Decimal("%.20f" % item.get(order_by, 0))
            #end_key[order_by] = Decimal(str(item[order_by]))

        return end_key

    def db_get_items_in_partition(self, partition, order_by='creation_date',
                                  order_min=None, order_max=None, start_key=None, limit=100, reverse=False,
                                  sort_min=None, sort_max=None):
        def should_contains(key, min_value, max_value):
            if min_value:
                return key >= min_value
            if max_value:
                return key <= max_value
            return True

        if isinstance(start_key, str):
            start_key = json.loads(start_key)

        start_key = self.get_end_key(start_key, order_by)
        response = self.dynamo.get_items_in_partition_by_order(self.app_id, partition, order_by,
                                                               sort_min, sort_max, start_key, limit, reverse)
        items = response.get('Items', [])
        end_key = response.get('LastEvaluatedKey', None)
        if end_key:
            end_key = self.get_end_key(items[-1], order_by)

        filter_items = [item for item in items if should_contains(item[order_by], order_min, order_max)]
        if len(filter_items) < len(items):
            if filter_items:
                end_key = self.get_end_key(filter_items[-1], order_by)
            else:
                end_key = {
                    'id': None
                }
        elif end_key and (order_min or order_max):
            while end_key is not None:
                response = self.dynamo.get_items_in_partition_by_order(self.app_id, partition, order_by,
                                                                       sort_min, sort_max,
                                                                       end_key, limit, reverse)
                sub_items = response.get('Items', [])
                end_key = response.get('LastEvaluatedKey', None)
                sub_filter_items = [item for item in sub_items if should_contains(item[order_by], order_min, order_max)]

                items.extend(sub_items)
                filter_items.extend(sub_filter_items)

                if len(filter_items) < len(items) and filter_items:
                    end_key = self.get_end_key(filter_items[-1], order_by)
                    break

        if end_key is not None and end_key is not False:
            end_key = json.dumps(encode_dict(end_key))

        return filter_items, end_key

    def db_get_item_id_and_orders(self, partition, field, value, order_by='creation_date',
                                  order_min=None, order_max=None, start_key=None, limit=100, reverse=False,
                                  sort_min=None, sort_max=None, operation='eq'):
        def should_contains(key, min_value, max_value):
            if min_value:
                return key >= min_value
            if max_value:
                return key <= max_value
            return True

        # order_field 가 'creation_date' 이 아니면 아직 사용 불가능
        if isinstance(start_key, str):
            start_key = json.loads(start_key)

        start_key = self.get_end_key(start_key, order_by, 'inverted_query')

        response = self.dynamo.get_inverted_queries(self.app_id, partition, field, value, operation, order_by,
                                                    sort_min, sort_max, start_key, limit, reverse)
        items = response.get('Items', [])
        end_key = response.get('LastEvaluatedKey', None)
        if end_key:
            end_key = self.get_end_key(items[-1], order_by, 'inverted_query')

        filter_items = list([item for item in items if should_contains(item[order_by], order_min, order_max)])
        if len(filter_items) < len(items):
            if filter_items:
                end_key = self.get_end_key(filter_items[-1], order_by, 'inverted_query')
            else:
                end_key = {
                    'id': None
                }
        elif end_key and (order_min or order_max):
            while end_key is not None:
                response = self.dynamo.get_inverted_queries(self.app_id, partition, field, value, operation, order_by,
                                                            sort_min, sort_max, end_key, limit, reverse)
                sub_items = response.get('Items', [])
                end_key = response.get('LastEvaluatedKey', None)
                sub_filter_items = [item for item in sub_items if should_contains(item[order_by], order_min, order_max)]

                items.extend(sub_items)
                filter_items.extend(sub_filter_items)
                # 필터 아이템이 0개인 경우가 있음 이거 예외처리해줘야해
                if len(filter_items) < len(items) and filter_items:
                    end_key = self.get_end_key(filter_items[-1], order_by, 'inverted_query')
                    break

        item_id_and_creation_date_list = [{'item_id': item.get('item_id'), order_by: item.get(order_by)}
                                          for item in filter_items]
        if end_key is not None and end_key is not False:
            end_key = json.dumps(encode_dict(end_key))

        return item_id_and_creation_date_list, end_key

    def db_create_sort_index(self, sort_key, sort_key_type):
        if sort_key_type not in ['N', 'S']:
            raise Exception("sort_key_type must be 'N' or 'S'")
        result = self.dynamo.create_table(self.app_id, sort_key, sort_key_type)
        return result

    # File ops
    def file_download_bin(self, file_id):
        binary = self.s3.download_bin(self.app_id, file_id)
        return binary

    def file_upload_bin(self, file_id, binary):
        result = self.s3.upload_bin(self.app_id, file_id, binary)
        return bool(result)

    def file_delete_bin(self, file_id):
        result = self.s3.delete_bin(self.app_id, file_id)
        return bool(result)

    # Event scheduling
    def ev_put_schedule(self, schedule_name, cron_exp, params):
        input_json = {
            'body': params
        }
        target_id = str(uuid.uuid4()).replace('-', '')
        input_json = json.dumps(input_json)
        lambda_client = Lambda(self.boto3_session)
        lambda_function = lambda_client.get_function(self.app_id)
        lambda_function_config = lambda_function.get('Configuration')
        lambda_function_arn = lambda_function_config.get('FunctionArn')
        lambda_function_name = lambda_function_config.get("FunctionName")
        statement_id = target_id
        action = 'lambda:InvokeFunction'
        principal = 'events.amazonaws.com'
        events = Events(self.boto3_session)
        rule_response = events.put_rule(str(schedule_name), cron_exp)
        rule_arn = rule_response.get('RuleArn')
        _ = lambda_client.add_permission(lambda_function_name, statement_id, action, principal, rule_arn)
        put_target_resp = events.put_target(target_id, str(schedule_name), lambda_function_arn, input_json)
        return put_target_resp

    def ev_delete_schedule(self, schedule_name):
        events = Events(self.boto3_session)
        resp = events.get_targets(schedule_name)
        targets = resp.get('Targets', [])
        next_token = resp.get('NextToken', None)
        while next_token:
            resp = events.get_targets(schedule_name)
            targets.extend(resp.get('Targets', []))
            next_token = resp.get('NextToken', None)

        target_ids = [target.get('Id') for target in targets]

        resp = events.delete_targets(schedule_name, target_ids)
        resp = events.delete_rule(schedule_name)

        lambda_client = Lambda(self.boto3_session)
        lambda_function = lambda_client.get_function(self.app_id)
        lambda_function_config = lambda_function.get('Configuration')
        lambda_function_name = lambda_function_config.get("FunctionName")
        for target_id in target_ids:
            remove_response = lambda_client.remove_permission(lambda_function_name, target_id)
            print('remove_response:', remove_response)
        return resp

    def sms_send_message(self, phone_number, message, region='us-east-1'):
        sns = SNS(self.boto3_session, region)
        resp = sns.send_message(phone_number, message)
        return resp

    def function_update_memory_size(self, memory_size=3000):
        lam = Lambda(self.boto3_session)
        resp = lam.update_function_memory_size(self.app_id, memory_size)
        return resp

    def function_create_stand_alone_function(self, function_name, zipfile_bin):
        """
        ExecuteStandAlone 로 실행 가능한 스탠드얼론 함수 생성.
        :param function_name:
        :param zipfile_bin:
        :return:
        """
        role_name = '{}'.format(self.app_id)
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)

        role_arn = iam.create_role_and_attach_policies(role_name)

        name = '{}_{}'.format(self.app_id, function_name)
        desc = f'stand-alone-function-of-{self.app_id}'
        runtime = 'python3.6'
        handler = '__aws_interface_stand_alone_physical_handler.main'

        handler_method_name = '__aws_interface_stand_alone_physical_handler'
        handler_module_name = f'resource.standalone.{handler_method_name}'
        handler_module = importlib.import_module(handler_module_name)

        with open(handler_module.__file__, 'r') as fp:
            handler_module_content = fp.read()

        temp_extract_path = tempfile.mkdtemp()
        temp_zip_file = tempfile.mktemp()
        with open(temp_zip_file, 'wb+') as fp:
            fp.write(zipfile_bin)

        with ZipFile(temp_zip_file) as fp:
            fp.extractall(temp_extract_path)

        with open(os.path.join(temp_extract_path, f'{handler_method_name}.py'), 'w+') as fp:
            fp.write(handler_module_content)

        output_filename = tempfile.mktemp()
        shutil.make_archive(output_filename, 'zip', temp_extract_path)
        output_zip_file_name = '{}.zip'.format(output_filename)
        with open(output_zip_file_name, 'rb') as fp:
            zipfile_bin = fp.read()
        shutil.rmtree(temp_extract_path)
        os.remove(temp_zip_file)
        os.remove(output_zip_file_name)
        return lambda_client.create_function(name, desc, runtime, role_arn, handler, zipfile_bin)

    def function_update_stand_alone_function(self, function_name, zipfile_bin):
        """
        함수 수정.
        :param function_name:
        :param zipfile_bin:
        :return:
        """
        lambda_client = Lambda(self.boto3_session)

        name = '{}_{}'.format(self.app_id, function_name)

        handler_method_name = '__aws_interface_stand_alone_physical_handler'
        handler_module_name = f'resource.standalone.{handler_method_name}'
        handler_module = importlib.import_module(handler_module_name)

        with open(handler_module.__file__, 'r') as fp:
            handler_module_content = fp.read()

        temp_extract_path = tempfile.mkdtemp()
        temp_zip_file = tempfile.mktemp()
        with open(temp_zip_file, 'wb+') as fp:
            fp.write(zipfile_bin)

        with ZipFile(temp_zip_file) as fp:
            fp.extractall(temp_extract_path)

        with open(os.path.join(temp_extract_path, f'{handler_method_name}.py'), 'w+') as fp:
            fp.write(handler_module_content)

        output_filename = tempfile.mktemp()
        shutil.make_archive(output_filename, 'zip', temp_extract_path)
        output_zip_file_name = '{}.zip'.format(output_filename)
        with open(output_zip_file_name, 'rb') as fp:
            zipfile_bin = fp.read()
        shutil.rmtree(temp_extract_path)
        os.remove(temp_zip_file)
        os.remove(output_zip_file_name)
        return lambda_client.update_function_code(name, zipfile_bin)

    def function_execute_stand_alone_function(self, function_name, request_body):
        """
        Lambda SDK 로 함수를 실행하고 응답을 반환합니다.
        :param function_name:
        :param request_body:
        :return:
        """
        lambda_client = Lambda(self.boto3_session)
        name = '{}_{}'.format(self.app_id, function_name)
        json_body = json.dumps(encode_dict(request_body))
        json_body_byte = json_body.encode('utf-8')
        response = lambda_client.invoke_function(name, json_body_byte)
        response_body = response['Payload'].read().decode()
        response_body_json = json.loads(response_body)
        return response_body_json

    # 신규기능 FDB
    # 새로 추가된 FastDatabase, Fully NoSQL
    @classmethod
    def _fdb_item_id_to_pk_sk_pair(cls, item_id):
        """
        내부적으로 pk와 sk 조합을 item_id 로 부터 복호화합니다.
        :param item_id:
        :return:
        """
        try:
            return json.loads(item_id)
        except:
            return None

    @classmethod
    def _fdb_pk_sk_to_item_id(cls, pk, sk):
        """
        pk 와 sk 를 item_id 로 암호화합니다.
        :param pk:
        :param sk:
        :return:
        """
        return json.dumps({
            '_pk': pk,
            '_sk': sk
        })

    def fdb_create_partition(self, partition, pk_group, pk_field, sk_group, sk_field=None,
                             post_sk_fields=None, use_random_sk_postfix=True):
        """
        Fast DB 내부에 파티션을 생성합니다. 사실 생성의 개념보다는 파티션을 선언합니다.
        파티션 삭제시에, 내부 데이터는 삭제 되지 않기 때문에 유의해야합니다.
        :param partition: order 등 파티션 이름
        :param pk_group: app, system 등 파티션 필드 앞에 구분자를 붙일 때 사용합니다. 한번 지정되면 바꿀 수 없습니다.
        같은 user_id 를 가진 엔티티여도 시스템에서 사용하느냐, 앱에서 사용하느냐에 따라 구분할 수 있습니다.
        일례로 로그 데이터 등은 system 에 보관하는것이 안전하고, 속도 측면에서도 유리합니다.
        :param pk_field: user_id 등을 pk_field 로 지정하는것이 유리합니다. 병렬 처리와 관련 있으며, 디버깅을 위해
        실제 DB의 pk 필드 (인덱스) 에는 <pk_group>#<pk_field>#<pk.value> 의 값이 들어갑니다.
        :param sk_group: sort key 앞에 붙는 그룹 구분입니다. sk = <sk_group>#<partition>#<sk_field>#<sk.value> 가 들어갑니다.
        이 값을 이용하여 같이 조인되어야 하는 값들을 효과적으로 조인할 수 있습니다. 예를 들면
        그룹 order 으로 묶이는 경우, order 으로 order_plan 이나 order 등 같이 묶여서 반환시 성능이 극대화 시킬 수 있습니다.
        :param sk_field: created_at 등.. 날짜로 구성하면 날짜별 정렬이 가능합니다.
        :param post_sk_fields: 소트키 뒤에 붙는 field 입니다. 임의로 데이터 중복 생성 방지 기능을 만드는데 유용합니다.
        :param use_random_sk_postfix: pk 와 sk 가 같으면 중복 생성이 불능하기 때문에, 랜덤 문자열을 붙여 다른 아이템으로
        생성할 수 있습니다.
        :return:
        """
        self._fdb_remove_partition_cache()

        response = self.dynamoFDB.put_item({
            '_pk': config.STR_META_INFO_PARTITION,
            '_sk': partition,
            '_partition_name': partition,
            '_pk_group': pk_group,
            '_pk_field': pk_field,
            '_sk_group': sk_group,
            '_sk_field': sk_field,
            '_post_sk_fields': post_sk_fields,
            '_use_random_sk_postfix': use_random_sk_postfix,
            '_created_at': int(time.time()),
        })
        result_item = response.get('Attributes', {})
        return result_item

    def fdb_append_index(self, partition, index_name, pk_group, pk_field, sk_group, sk_field):
        """
        DB partition 에 인덱스를 추가합니다.
        TODO 일단 기본 기능 먼저 구현하고, 필요시에 인덱스 부분을 개발하도록 한다.
        :param partition:
        :param index_name:
        :param pk_group:
        :param pk_field:
        :param sk_group:
        :param sk_field:
        :return:
        """

    def _fdb_remove_partition_cache(self):
        """
        캐시 삭제, 새로운 파티션 추가시 필요!
        :return:
        """
        if 'partitions' in self.cache:
            self.cache.pop('partitions')

    def fdb_get_partitions(self, use_cache=False):
        """
        파티션 목록을 가져옵니다.
        :return:
        """
        if use_cache and 'partitions' in self.cache:
            return self.cache['partitions']
        response = self.dynamoFDB.query_items('_pk', config.STR_META_INFO_PARTITION, 'gte', '_sk', ' ',
                                              consistent_read=True)
        items = response.get('Items', [])
        self.cache['partitions'] = items
        return items

    def fdb_delete_partition(self, partition):
        """
        파티션을 삭제, 내부 데이터는 별도로 삭제해야합니다.
        :param partition:
        :return:
        """
        self._fdb_remove_partition_cache()
        response = self.dynamoFDB.delete_item(config.STR_META_INFO_PARTITION, partition)
        return response

    def fdb_has_pk_sk_by_item(self, partition, item):
        """
        item 의 pk-sk 조합이 이미 DB에 존재하는지 확인, create 확인용으로 주로 사용
        :param partition:
        :param item:
        :return:
        """
        item = self._fdb_process_item_with_partition(item, partition)
        item_id = item.get('_id', None)
        if item_id:
            items = self.fdb_get_items([item_id])
            for it in items:
                if it:
                    return True
        return False

    def _fdb_process_item_with_partition(self, item, partition):
        """
        item 을 DB에 넣기 전에 partition 에서 정하는 형태와 동일하게 매핑합니다.
        :param item:
        :param partition:
        :return:
        """
        partitions = self.fdb_get_partitions(use_cache=True)
        partitions_by_name = {
            p.get('_partition_name', None): p for p in partitions
        }
        partition_obj = partitions_by_name.get(partition, None)
        if not partition_obj:
            raise Exception('No such partition')

        pk_group = partition_obj['_pk_group']
        pk_field = partition_obj['_pk_field']
        sk_group = partition_obj['_sk_group']
        sk_field = partition_obj['_sk_field']
        post_sk_fields = partition_obj['_post_sk_fields']
        use_random_sk_postfix = partition_obj['_use_random_sk_postfix']

        item['_created_at'] = int(time.time())
        item = decode_dict(item)

        if pk_field not in item:
            raise Exception(f'pk_field:[{pk_field}] should in item')
        if sk_field and sk_field not in item:
            raise Exception(f'sk_field:[{sk_field}] should in item')

        pk_value = item[pk_field]
        if sk_field:
            sk_value = item[sk_field]
        else:
            sk_value = ''

        sk_digit_fit = int(config.SK_DIGIT_FIT)
        # 자리수를 맞춥니다. 숫자는 오른쪽부터 채우고 문자는 왼쪽부터 채웁니다.
        # sk_digit_fit: 1234 인데 sk_digit_fit=8 이면, '____1234' 처럼 sorting 을 위해 자리를 채웁니다.
        #         소숫점이 들어오면 '____1234.43' 이런식으로 . 이하는 무시합니다.
        #         0이면 그대로 둡니다.
        try:
            sk_value = Decimal(sk_value) * pow(10, config.SK_FLOAT_FIT)
            sk_value = int(sk_value)
            sk_value = util.convert_int_to_custom_base64(sk_value)
            sk_value = sk_value.rjust(sk_digit_fit)
        except:
            sk_value = str(sk_value)
            sk_value = sk_value.ljust(sk_digit_fit)

        if sk_field is None:
            # None 이 그대로 삽입되는걸 방지
            sk_field = ''
        pk = f'{pk_group}#{pk_field}#{pk_value}'
        sk = f'{sk_group}#{partition}#{sk_field}#{sk_value}'

        if post_sk_fields:
            for post_sk_field in post_sk_fields:
                post_sk_value = item.get(post_sk_field, '')
                sk += f'#{post_sk_field}#{post_sk_value}'

        if use_random_sk_postfix:
            sk += '#' + str(uuid.uuid4()).replace('-', '')

        item['_pk'] = pk
        item['_sk'] = sk
        item['_partition'] = partition
        item['_id'] = self._fdb_pk_sk_to_item_id(pk, sk)
        return item

    def fdb_put_items(self, partition, items):
        """
        배치 생성.
        item 삽입 전에 파티션을 불러와서 매칭을 잘 확인해야합니다.
        :param partition:
        :param items:
        :return:
        """
        items = [self._fdb_process_item_with_partition(item, partition) for item in items]
        _ids = [item['_id'] for item in items]
        response = self.dynamoFDB.batch_put(items)
        return _ids

    def fdb_put_item(self, partition, item):
        """
        생성
        :param partition:
        :param item:
        :return:
        """
        item = self._fdb_process_item_with_partition(item, partition)
        response = self.dynamoFDB.put_item(item)
        _id = item.get('_id', None)
        return _id

    def fdb_get_items(self, item_ids, consistent_read=False):
        """
        item_ids 를 배치로 쿼리하여 가져옵니다.
        :param item_ids:
        :param consistent_read:
        :return:
        """
        response = self.dynamoFDB.get_items(
            [self._fdb_item_id_to_pk_sk_pair(item_id) for item_id in item_ids],
            consistent_read=consistent_read
        )
        return response

    def _convert_number_to_custom64(self):
        pass

    def fdb_query_items(self, pk_group, pk_field, pk_value, sort_condition=None,
                        sk_group='', partition=None, sk_field='', sk_value='', sk_second_value=None, filters=None,
                        start_key=None, limit=100, reverse=False, consistent_read=False, index_name=None):
        """
        DB 를 쿼리하고, 이는 NoSQL 최적화 되어 있습니다.
        단계별로 pk 관련 키들은 쿼리에 필수이며,
        sk 관련 키들은 단계별로 아이템 쿼리를 진행할 수 있도록 도와줍니다.
        partition 을 넘겨야, sk_value 를 입력할 수 있기 때문에,
        sk_field 를 파티션을 통해 구할 수 있습니다.
        TODO: 인덱스 기능이 추가될 경우, 마지막 파라메터 index 를 받아 처리해야합니다.
        :param pk_group:
        :param pk_field:
        :param pk_value:
        :param sort_condition:
        :param sk_group:
        :param partition:
        :param sk_field:
        :param sk_value:
        :param sk_second_value:
        :param filters:
        :param start_key:
        :param limit:
        :param reverse:
        :param consistent_read:
        :param index_name: 없을시 기본 파라메터로 쿼리
        :return:
        """
        if partition is not None:
            partitions = self.fdb_get_partitions(use_cache=True)
            partitions_by_name = {
                p.get('_partition_name', None): p for p in partitions
            }
            partition_obj = partitions_by_name.get(partition, None)
            if not partition_obj:
                raise Exception('No such partition')

            p_pk_field = partition_obj['_pk_field']

            if p_pk_field != pk_field:
                raise Exception(f'pk_field must be a [{p_pk_field}]')

        sk_digit_fit = int(config.SK_DIGIT_FIT)
        # 자리수를 맞춥니다. 숫자는 오른쪽부터 채우고 문자는 왼쪽부터 채웁니다.
        if sk_value:
            try:
                sk_value = Decimal(sk_value) * pow(10, config.SK_FLOAT_FIT)
                sk_value = int(sk_value)
                sk_value = util.convert_int_to_custom_base64(sk_value)
                sk_value = sk_value.rjust(sk_digit_fit)
            except:
                sk_value = str(sk_value)
                sk_value = sk_value.ljust(sk_digit_fit)
        else:
            sk_value = ''

        pk = f'{pk_group}#{pk_field}#{pk_value}'

        if not sk_group:
            # sort key 의 맨 처음 부분이기 때문에 문자 하나는 있어야 함, 공백 문자 삽입
            sk_group = ' '

        sk = f'{sk_group}'
        if partition:
            sk += f'#{partition}'
        if sk_field:
            sk += f'#{sk_field}'

        sk_high = ''
        if sk_second_value:
            sk_high = sk + f'#{sk_second_value}'
        if sk_value:
            sk += f'#{sk_value}'

        response = self.dynamoFDB.query_items('_pk', pk,
                                              sort_condition, '_sk', sk,
                                              sort_key_second_value=sk_high, filters=filters,
                                              start_key=start_key, reverse=reverse, limit=limit,
                                              consistent_read=consistent_read, index_name=index_name)
        end_key = response.get('LastEvaluatedKey', None)
        items = response.get('Items', [])
        return items, end_key

    def fdb_delete_items(self, item_ids):
        """
        배치 삭제, 여러개를 한번에 삭제
        :param item_ids:
        :return:
        """
        self.dynamoFDB.batch_delete([self._fdb_item_id_to_pk_sk_pair(item_id) for item_id in item_ids])


if __name__ == '__main__':
    pass