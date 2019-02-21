import importlib
import os
import shutil
from abc import ABCMeta
import boto3
from cloud.aws import *


def create_lambda_zipfile_bin(app_id, recipe, dir_name, root_name='cloud'):
    output_filename = tempfile.mktemp()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy lambda dir into temp/root_name folder
        shutil.copytree(dir_name, '{}/{}'.format(tmp_dir, root_name))

        # Copy recipe from recipe_controller
        with open(os.path.join(tmp_dir, root_name, 'recipe.json'), 'w+') as file:
            file.write(recipe)

        # Write txt file included app_id
        with open(os.path.join(tmp_dir, root_name, 'app_id.txt'), 'w+') as file:
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


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    region_name = bundle.get('region_name', 'ap-northeast-2')  # TODO
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region_name,
    )
    return session


class ServiceController(metaclass=ABCMeta):
    """
    Make sure to set RECIPE when you inherit this class.
    """
    RECIPE = None

    def __init__(self, bundle, app_id):
        """
        Initiate service controller. Make sure to call this from the
        __init__ method of child classes.

        :param bundle:
        Dict containing keys to initialize boto3 session. May include
        access_key, secret_key, region_name

        :param app_id:
        """
        assert(type(self).RECIPE is not None)

        self.boto3_session = get_boto3_session(bundle)
        self.app_id = app_id

    def apply_cloud_api(self, recipe_controller):
        """
        Update AWS Lambda functions

        Upload python scripts for the APIs specified in the recipe to AWS Lambda in compressed format.
        The original python scripts are located in cloud/<recipe_type>

        :return:
        """
        recipe_type = recipe_controller.get_recipe()
        print('[{}:{}] apply_cloud_api: START'.format(self.app_id, recipe_type))

        role_name = '{}-{}'.format(recipe_type, self.app_id)
        lambda_client = Lambda(self.boto3_session)
        iam = IAM(self.boto3_session)
        role_arn = iam.create_role_and_attach_policies(role_name)

        name = '{}-{}'.format(recipe_type, self.app_id)
        desc = 'aws-interface cloud API'
        runtime = 'python3.6'
        handler = 'cloud.lambda_function.handler'

        module_name = 'cloud'
        module = importlib.import_module(module_name)
        module_path = os.path.dirname(module.__file__)

        recipe = recipe_controller.to_json()
        zip_file = create_lambda_zipfile_bin(self.app_id, recipe, module_path)

        success = True
        try:
            lambda_client.create_function(name, desc, runtime, role_arn, handler, zip_file)
        except BaseException as ex:
            # print(ex)
            # print('Function might already exist, Try updating function code.')
            try:
                print('[{}:{}] apply_cloud_api: {}'.format(self.app_id, recipe_type, 'RETRY'))
                lambda_client.update_function_code(name, zip_file)
            except BaseException as ex:
                success = False
                # print(ex)
                # print('Update function failed')

        print('[{}:{}] apply_cloud_api: {}'.format(self.app_id, recipe_type, 'COMPLETE' if success else 'FAIL'))

    def deploy_cloud_api(self, recipe_controller):
        """
        Update AWS API Gateway settings

        Update settings in AWS API Gateway, to enable an http gateway to call the AWS Lambda functions
        that were uploaded via apply_cloud_api().

        Background: AWS API Gateway can be used to set up http endpoints so that client apps can call
        functions in AWS Lambda, using http requests.

        :return:
        """
        recipe_type = recipe_controller.get_recipe()
        api_name = '{}-{}'.format(recipe_type, self.app_id)
        func_name = '{}-{}'.format(recipe_type, self.app_id)
        print('[{}:{}] deploy_cloud_api: START'.format(self.app_id, recipe_type))
        api_gateway = APIGateway(self.boto3_session)
        api_gateway.connect_with_lambda(api_name, func_name)
        print('[{}:{}] deploy_cloud_api: COMPLETE'.format(self.app_id, recipe_type))

    def get_rest_api_url(self, recipe_controller):
        api_client = APIGateway(self.boto3_session)
        recipe_type = recipe_controller.get_recipe()
        api_name = '{}-{}'.format(recipe_type, self.app_id)
        func_name = '{}-{}'.format(recipe_type, self.app_id)
        api_url = api_client.get_rest_api_url(api_name, func_name)
        return api_url

    def apply(self, recipe_controller):
        """
        Apply/deploy the recipe to AWS backend services. This includes
        setting up interfaces through AWS Lambda and API Gateway.

        To add recipe-specific actions, override this method and REMEMBER TO
        CALL THE BASE METHOD.

        :param recipe_controller:
        :return:
        """
        self.apply_cloud_api(recipe_controller)
        self.deploy_cloud_api(recipe_controller)
