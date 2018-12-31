
class ServiceController:
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session

    def read_recipe(self):
        return NotImplementedError()

    def save_recipe(self, recipe):
        return NotImplementedError()

    def apply_recipe(self, recipe):
        return NotImplementedError()


class AuthServiceController(ServiceController):
    def read_recipe(self):
        return

    def save_recipe(self, recipe):
        return

    def apply_recipe(self, recipe):
        return


    def create_user(self, email, password, extra):
        return