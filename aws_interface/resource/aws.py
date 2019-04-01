import importlib
import os
import shutil
import tempfile
import json
from resource.wrapper.boto3_wrapper import get_boto3_session, Lambda, APIGateway, IAM, DynamoDB, CostExplorer
from resource.base import ResourceAllocator, Resource

VENDOR = 'aws'


def create_lambda_zipfile_bin(app_id, recipes, cloud_path, resource_path):
    output_filename = tempfile.mktemp()
    cloud_name = 'cloud'
    resource_name = 'resource'
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy lambda dir into temp/root_name folder
        shutil.copytree(cloud_path, '{}/{}'.format(tmp_dir, cloud_name))
        shutil.copytree(resource_path, '{}/{}'.format(tmp_dir, resource_name))

        # Copy recipes json
        with open(os.path.join(tmp_dir, cloud_name, 'recipes.json'), 'w+') as file:
            recipes_dict = {recipe['recipe_type']: recipe for recipe in recipes}
            json.dump(recipes_dict, file)

        # Write txt file included app_id
        with open(os.path.join(tmp_dir, cloud_name, 'app_id.txt'), 'w+') as file:
            file.write(app_id)

        with open(os.path.join(tmp_dir, cloud_name, 'vendor.txt'), 'w+') as file:
            file.write(VENDOR)

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
    def __init__(self, credential, app_id, recipes):
        super(AWSResourceAllocator, self).__init__(credential, app_id, recipes)
        self.boto3_session = get_boto3_session(credential)

    def create(self):
        self._create_dynamo_db_table()
        self._create_lambda_function()
        self._create_rest_api_connection()

    def terminate(self):
        self._remove_dynamo_db_table()
        self._remove_lambda_function()
        self._remove_rest_api_connection()

    def get_rest_api_url(self):
        api_gateway = APIGateway(self.boto3_session)
        return api_gateway.get_rest_api_url(self.app_id)

    def get_logs(self):
        return ['dummy', 'log']

    def _create_dynamo_db_table(self):
        dynamo = DynamoDB(self.boto3_session)
        dynamo.init_table(self.app_id)

    def _create_lambda_function(self):
        """
        Update AWS Lambda functions

        Upload python scripts for the APIs specified in the recipe to AWS Lambda in compressed format.
        The original python scripts are located in cloud/<recipe_type>

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
        handler = 'cloud.lambda_function.handler'

        cloud_module_name = 'cloud'
        cloud_module = importlib.import_module(cloud_module_name)
        cloud_module_path = os.path.dirname(cloud_module.__file__)

        resource_module_name = 'resource'
        resource_module = importlib.import_module(resource_module_name)
        resource_module_path = os.path.dirname(resource_module.__file__)

        zip_file = create_lambda_zipfile_bin(self.app_id, self.recipes, cloud_module_path, resource_module_path)

        success = True
        try:
            lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file)
        except BaseException as ex:
            print(ex)
            try:
                print('[{}] apply_cloud_api: {}'.format(self.app_id, 'RETRY'))
                lambda_client.update_function_code(name, zip_file)
            except BaseException as ex:
                success = False
                print(ex)

        print('[{}] apply_cloud_api: {}'.format(self.app_id, 'COMPLETE' if success else 'FAIL'))

    def _create_rest_api_connection(self):
        api_name = '{}'.format(self.app_id)
        func_name = '{}'.format(self.app_id)
        api_gateway = APIGateway(self.boto3_session)
        api_gateway.connect_with_lambda(api_name, func_name)

    def _get_rest_api_url(self):
        api_name = '{}'.format(self.app_id)
        api_client = APIGateway(self.boto3_session)
        api_url = api_client.get_rest_api_url(api_name)
        return api_url

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


class AWSResource(Resource):
    def __init__(self, credential, app_id, boto3_session=None):
        super(AWSResource, self).__init__(credential, app_id)
        if boto3_session:
            self.boto3_session = boto3_session
        elif credential:
            self.boto3_session = get_boto3_session(credential)

    # backend resource cost
    def cost_for(self, start, end):
        cost_exp = CostExplorer(self.boto3_session)
        return cost_exp.get_cost(start, end)

    def cost_and_usage_for(self, start, end):
        cost_exp = CostExplorer(self.boto3_session)
        return cost_exp.get_cost_and_usage(start, end)

    # DB ops
    def db_create_partition(self, partition):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.create_partition(self.app_id, partition)
        return bool(response)

    def db_delete_partition(self, partition):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.delete_partition(self.app_id, partition)
        return bool(response)

    def db_get_partitions(self):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.get_partitions(self.app_id)
        items = response.get('Items', [])
        return items

    def db_delete_item(self, item_id):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.delete_item(self.app_id, item_id)
        return bool(result)

    def db_delete_item_batch(self, item_ids):
        result = True
        dynamo = DynamoDB(self.boto3_session)
        for item_id in item_ids:
            result &= bool(dynamo.delete_item(self.app_id, item_id))
        return result

    def db_get_item(self, item_id):
        dynamo = DynamoDB(self.boto3_session)
        item = dynamo.get_item(self.app_id, item_id)
        return item.get('Item', None)

    def db_get_items(self, partition, exclusive_start_key=None, limit=None, reverse=False):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.get_items(self.app_id, partition, exclusive_start_key, limit, reverse)
        end_key = result.get('LastEvaluatedKey', None)
        items = result.get('Items', [])
        return items, end_key

    def db_query(self, partition, instructions, start_keys=None, limit=100, reverse=False):
        # TODO 상위레이어에서 쿼리를 순차적으로 실행가능한 instructions 으로 만들어 전달 -> ORM 클래스 만들기
        all_item_ids = set()

        if start_keys is None:
            start_keys = [None] * len(instructions)

        def q(temp_start_keys):
            item_ids = set()
            end_keys = []
            for idx, (operation, statement) in enumerate(instructions):
                start_key = temp_start_keys[idx]
                ids, end_key = self._invoke_statement(partition, statement, start_key, limit)
                end_keys.append(end_key)
                if operation == 'and':
                    item_ids &= ids
                elif operation == 'or':
                    item_ids |= ids
                else:
                    item_ids |= ids
            return item_ids, end_keys

        _end_keys = [None] * len(instructions)
        while limit > len(all_item_ids):
            _item_ids, _end_keys = q(start_keys)
            all_item_ids |= _item_ids
            if all(end_key is None for end_key in _end_keys):
                _end_keys = None
                break
        all_item_ids = list(all_item_ids)
        items = [self.db_get_item(item_id) for item_id in all_item_ids]

        return items, _end_keys

    def db_put_item(self, partition, item, item_id=None, creation_date=None):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.put_item(self.app_id, partition, item, item_id, creation_date)
        return bool(result)

    def db_update_item(self, item_id, item):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.update_item(self.app_id, item_id, item)
        return bool(result)

    def db_get_count(self, partition):
        dynamo = DynamoDB(self.boto3_session)
        item = dynamo.get_item_count(self.app_id, '{}-count'.format(partition)).get('Item', {'count': 0})
        count = item.get('count')
        return count

    # File ops
    def file_download_base64(self, file_id):
        raise NotImplementedError

    def file_upload_base64(self, file_id, file_base64):
        raise NotImplementedError

    def file_delete_base64(self, file_id):
        raise NotImplementedError

    def _invoke_statement(self, partition, statement, start_key, limit):
        operation, field, value = statement
        if operation == 'eq':
            return self._query_eq(partition, field, value, start_key, limit)
        elif operation == 'in':
            return self._query_in(partition, field, value, start_key, limit)
        else:
            raise BaseException('an operation must be <eq> or <in>')

    def _query_eq(self, partition, field, value, start_key, limit):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.get_inverted_queries(self.app_id, partition, field, value, 'eq', start_key, limit)
        items = response.get('Items', [])
        end_key = response.get('LastEvaluatedKey', None)
        ids = {item.get('item_id') for item in items}
        return ids, end_key

    def _query_in(self, partition, field, value, start_key, limit):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.get_inverted_queries(self.app_id, partition, field, value, 'in', start_key, limit)
        items = response.get('Items', [])
        end_key = response.get('LastEvaluatedKey', None)
        ids = {item.get('item_id') for item in items}
        return ids, end_key
