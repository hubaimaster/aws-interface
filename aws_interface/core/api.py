from core.recipecontroller import *
from core.servicecontroller import *


class API:
    def __init__(self, bundle, recipe_json_string=None):
        self.bundle = bundle
        self.recipe = None
        if recipe_json_string:
            self.recipe = RecipeController()
            self.recipe.load_json_string(recipe_json_string)
        self.service_controller = None
        self.common_init()  # Set recipe and service_controller
        if self.recipe is None:
            print('You should assign recipe on common_init()')
            raise NotImplementedError()
        if self.service_controller is None:
            print('You should assign service_controller on common_init()')
            raise NotImplementedError()

    def apply(self):
        self.service_controller.apply()

    def get_recipe(self):
        return self.recipe

    def common_init(self):
        raise NotImplementedError()


class AuthAPI(API):
    def common_init(self):
        if self.recipe is None:
            self.recipe = AuthRecipeController()
        self.service_controller = AuthServiceController(self.bundle, self.recipe)

    # Recipe
    def get_user_groups(self):
        user_groups = self.recipe.get_user_groups()
        return user_groups

    def put_user_group(self, group_name):
        return self.recipe.put_user_group(group_name)

    def delete_user_group(self, group_name):
        raise NotImplementedError()

    # Service
    def create_user(self, email, password, extra):
        raise NotImplementedError()

    def put_user(self, user_id, email, password, extra):
        raise NotImplementedError()

    def delete_user(self, user_id):
        raise NotImplementedError()

    def get_user(self, user_id):
        raise NotImplementedError()

    def search_user_ids(self, query): # query ex : 'kim' in col('name') and 21 is col('age')
        raise NotImplementedError()


class DatabaseAPI(API):
    def common_init(self):
        if self.recipe is None:
            self.recipe = DatabaseRecipeController()
        return

    # Recipe
    def get_tables(self):
        tables = self.recipe.get_tables()
        raise tables

    def put_table(self, table_name):
        self.recipe.put_table(table_name)
        return

    def delete_table(self, table_name):
        raise NotImplementedError()

    def get_table(self, table_name):
        table = self.recipe.get_table(table_name)
        return table

    # Service
    def get_item(self, item_id):
        raise NotImplementedError()

    def search_item_ids(self, query):
        raise NotImplementedError()

    def create_item(self, item_json):
        raise NotImplementedError()

    def delete_item(self, item_id):
        raise NotImplementedError()

