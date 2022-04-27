import importlib
import os
import shutil
import tempfile
import json
import uuid
from decimal import Decimal
from numbers import Number
from resource.wrapper.boto3_wrapper import get_boto3_session, Lambda, APIGateway, IAM, DynamoDB, CostExplorer, S3, Events, SNS
from resource.base import ResourceAllocator, Resource
from zipfile import ZipFile


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

    def terminate(self):
        self._remove_bucket()
        self._remove_dynamo_db_table()
        self._remove_lambda_function()
        self._remove_rest_api_connection()

    def get_rest_api_url(self):
        api_gateway = APIGateway(self.boto3_session)
        return api_gateway.get_rest_api_url(self.app_id)

    def _create_dynamo_db_table(self):
        dynamo = DynamoDB(self.boto3_session)
        dynamo.init_table(self.app_id)

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


class AWSResource(Resource):
    def __init__(self, credential, app_id, boto3_session=None):
        super(AWSResource, self).__init__(credential, app_id)
        if boto3_session:
            self.boto3_session = boto3_session
        elif credential:
            self.boto3_session = get_boto3_session(credential)
        self.dynamo = DynamoDB(self.boto3_session)
        self.s3 = S3(self.boto3_session)

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
