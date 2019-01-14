import boto3


def get_boto3_session(bundle):
    access_key = bundle['access_key']
    secret_key = bundle['secret_key']
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session


class ServiceController:
    def __init__(self, bundle, recipe):
        self.bundle = bundle
        self.recipe = recipe
        self.prefix = lambda: self.recipe.get_recipe_type() + '-' + self.recipe.get_recipe_id() + '-'
        self.common_init()

    def common_init(self):
        #  init object here .. assign bundle, recipe, boto3 session
        return

    def apply(self):
        raise NotImplementedError()

    def generate_sdk(self):
        raise NotImplementedError()


class AuthServiceController(ServiceController):
    def common_init(self):
        boto3_session = get_boto3_session(self.bundle)
        self.dynamodb = boto3_session.client('dynamodb')

    def apply(self):
        return

    def generate_sdk(self):
        return

