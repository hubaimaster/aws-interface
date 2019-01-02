import json
import uuid


class Recipe:
    def __init__(self):
        self.data = dict()
        self.__set_recipe_id(str(uuid.uuid4()))
        self.common_init()

    def common_init(self):
        raise NotImplementedError()

    def to_json(self):
        return json.dumps(self.data)

    def from_json_string(self, json_string):
        self.data = json.loads(json_string)

    def get_recipe_id(self):
        return self.data.get('recipe_id', None)

    def __set_recipe_id(self, recipe_id):
        self.data['recipe_id'] = recipe_id

    def get_recipe_type(self):
        return self.data.get('recipe_type', None)

    def __set_recipe_type(self, recipe_type):
        self.data['recipe_type'] = recipe_type


class AuthRecipe(Recipe):
    def common_init(self):
        self.__set_recipe_type('auth')

    def put_user_group(self, group_name):
        restricts = ['admin', 'owner']
        if group_name in restricts:
            return False
        if 'user_groups' not in self.data:
            self.data['user_groups'] = []
        self.data['user_groups'].append(group_name)
        self.data['user_groups'] = list(set(self.data['user_groups']))
        return True

    def get_user_groups(self):
        user_groups = self.data.get('user_groups', [])
        return user_groups

    def put_user_column(self, column_name, value_type, read_groups, write_groups):
        if 'user_columns' not in self.data:
            self.data['user_columns'] = {}
        self.data['user_columns'][column_name] = {
            'value_type': value_type,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        return True

    def get_user_columns(self):
        user_columns = self.data.get('user_columns', {})
        return user_columns

    def get_user_column(self, column_name):
        columns = self.get_user_columns()
        column = columns.get(column_name, None)
        return column


class DatabaseRecipe(Recipe):
    def common_init(self):
        self.__set_recipe_type('database')

    def put_table(self, table_name):
        if 'tables' not in self.data:
            self.data['tables'] = {}
        self.data['tables'][table_name] = {}

    def get_tables(self):
        tables = self.data.get('tables', {})
        return tables

    def get_table(self, table_name):
        tables = self.get_tables()
        table = tables.get(table_name, None)
        return table

    def put_column(self, table_name, column_name, value_type, read_groups, write_groups):
        if 'tables' not in self.data:
            self.data['tables'] = {}
        if table_name not in self.data['tables']:
            self.data['tables'][table_name] = {}
        if 'columns' not in self.data['tables'][table_name]:
            self.data['tables'][table_name]['columns'] = {}

        self.data['tables'][table_name]['columns'][column_name] = {
            'value_type': value_type,
            'read_groups': read_groups,
            'write_groups': write_groups,
        }
        return True

    def get_columns(self, table_name):
        table = self.get_table(table_name)
        columns = table.get('columns', {})
        return columns

    def get_column(self, table_name, column_name):
        columns = self.get_columns(table_name)
        column = columns.get(column_name, None)
        return column