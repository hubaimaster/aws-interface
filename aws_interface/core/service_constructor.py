
class ServiceConstructor:
    def __init__(self, boto3_session, recipe):
        self.boto3_session = boto3_session
        self.recipe = recipe
        self.prefix = lambda: self.recipe.get_recipe_type() + '-' + self.recipe.get_recipe_id()
        self.common_init()

    def common_init(self):
        raise NotImplementedError()

    def apply(self):
        raise NotImplementedError()

    def generate_sdk(self):
        raise NotImplementedError()


class AuthServiceConstructor(ServiceConstructor):
    def common_init(self):
        self.dynamodb = self.boto3_session.client('dynamodb')

    def apply(self):
        return

    def create_user_table(self):
        table_name = self.prefix()
        table_list = self.dynamodb.list_tables()
        print('table_list:', table_list)

    def generate_sdk(self):
        return

