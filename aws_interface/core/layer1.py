from core.layer2 import *


class RecipeController:
    def __init__(self, boto3_session):
        self.boto3_session = boto3_session
        self.recipe = dict()
        self.read_recipe_from_aws()

    def get_recipe(self):
        return self.recipe

    def read_recipe_from_aws(self):
        return NotImplementedError()

    def apply_recipe_to_aws(self):
        return NotImplementedError()

    def generate_sdk(self):
        return NotImplementedError()


class AuthRecipeController(RecipeController):
    def read_recipe_from_aws(self):
        auth = AuthServiceController(self.boto3_session)
        self.recipe = auth.read_recipe()

    def apply_recipe_to_aws(self):
        auth = AuthRecipeController(self.boto3_session)
        auth.save_recipe(self.recipe)
        auth.apply_recipe(self.recipe)

    #Recipe..
    def create_user_group(self, group_name):
        error = None
        if 'groups' not in self.recipe:
            self.recipe['groups'] = []
        if group_name in self.recipe['groups']:
            error = '이미 그룹이 존재합니다'
        self.recipe['groups'].append(group_name)
        self.save_recipe_to_aws()
        self.apply_recipe_to_aws()
        return error, True

    def get_user_groups(self):
        if 'groups' not in self.recipe:
            self.recipe['groups'] = []
        return None, self.recipe['groups']