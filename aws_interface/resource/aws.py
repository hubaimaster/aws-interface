import importlib
import os
import shutil
import tempfile
from resource.wrapper.boto3_wrapper import get_boto3_session, Lambda, APIGateway, IAM, DynamoDB, CostExplorer, S3
from resource.base import ResourceAllocator, Resource


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
        self._create_dynamo_db_table()
        self._create_lambda_function()
        self._create_rest_api_connection()
        self._create_bucket()

    def terminate(self):
        self._remove_dynamo_db_table()
        self._remove_lambda_function()
        self._remove_rest_api_connection()
        self._remove_bucket()

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

    def db_get_items(self, item_ids):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.get_items(self.app_id, item_ids)
        return result.get('Items', [])

    def db_get_items_in_partition(self, partition, exclusive_start_key=None, limit=100, reverse=False):
        dynamo = DynamoDB(self.boto3_session)
        result = dynamo.get_items_in_partition(self.app_id, partition, exclusive_start_key, limit, reverse)
        end_key = result.get('LastEvaluatedKey', None)
        items = result.get('Items', [])
        return items, end_key

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

    def db_get_item_ids_equal(self, partition, field, value, start_key, limit):
        dynamo = DynamoDB(self.boto3_session)
        response = dynamo.get_inverted_queries(self.app_id, partition, field, value, 'eq', start_key, limit)
        items = response.get('Items', [])
        end_key = response.get('LastEvaluatedKey', None)
        ids = {item.get('item_id') for item in items}
        return ids, end_key

    # File ops
    def file_download_bin(self, file_id):
        s3 = S3(self.boto3_session)
        binary = s3.download_bin(self.app_id, file_id)
        return binary

    def file_upload_bin(self, file_id, binary):
        s3 = S3(self.boto3_session)
        result = s3.upload_bin(self.app_id, file_id, binary)
        return bool(result)

    def file_delete_bin(self, file_id):
        s3 = S3(self.boto3_session)
        result = s3.delete_bin(self.app_id, file_id)
        return bool(result)

    # Server-less ops
    def sl_create_function(self, function_name, runtime, handler, zip_file_bin):
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)
        role_name = '{}'.format(self.app_id)
        role_arn = iam.create_role_and_attach_policies(role_name)
        name = '{}-{}'.format(self.app_id, function_name)
        desc = 'aws-interface-logic'
        result = lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file_bin)
        return bool(result)

    def sl_delete_function(self, function_name):
        lambda_client = Lambda(self.boto3_session)
        name = '{}-{}'.format(self.app_id, function_name)
        result = lambda_client.delete_function(name)
        return bool(result)

    def sl_update_function(self, function_name, zip_file_bin):
        lambda_client = Lambda(self.boto3_session)
        name = '{}-{}'.format(self.app_id, function_name)
        result = lambda_client.update_function_code(name, zip_file_bin)
        return bool(result)

    def sl_invoke_function(self, function_name, payload):
        lambda_client = Lambda(self.boto3_session)
        name = '{}-{}'.format(self.app_id, function_name)
        result = lambda_client.invoke_function(name, payload)
        error = result.get('FunctionError', None)
        response_payload = result.get('Payload', None)
        return response_payload, error
