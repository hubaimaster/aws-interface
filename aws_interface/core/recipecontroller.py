import json
import uuid


class RecipeController:
    def __init__(self):
        self.data = dict()
        self.common_init()

    def common_init(self):
        #  init object here
        return

    def to_json(self):
        return json.dumps(self.data)

    def load_json_string(self, json_string):
        self.data = json.loads(json_string)

    def get_recipe_type(self):
        return self.data.get('recipe_type', None)

    def add_api(self, name, description, code_path):
        if 'apis' not in self.data:
            self.data['apis'] = {}
        self['apis'][name] = {
            'name': name,
            'description': description,
            'package': 'core.cloudcode.auth',
            'handler': 'get_user.run'
        }
        raise NotImplementedError()



class BillRecipeController(RecipeController):
    def common_init(self):
        self.data['recipe_type'] = 'bill'


class AuthRecipeController(RecipeController):
    def common_init(self):
        self.data['recipe_type'] = 'auth'
        # put system default groups
        self._init_user_group()

    def _init_user_group(self):
        self.default_groups = {
            'admin': '모든 읽기/쓰기 권한을 가지고 있습니다.',
            'owner': '자신이 작성한 데이터에 대해 모든 권한을 가지고 있습니다.',
            'user': '일반 사용자 그룹입니다.'
        }
        for name in self.default_groups:
            description = self.default_groups[name]
            self.put_user_group(name, description)

    def put_user_group(self, name, description):
        if 'user_groups' not in self.data:
            self.data['user_groups'] = {}
        self.data['user_groups'][name] = description
        return True

    def get_user_groups(self):
        user_groups = self.data.get('user_groups', self.default_groups)
        user_groups = [{
            'name': name,
            'description': user_groups[name]
        } for name in user_groups]
        return user_groups

    def delete_user_group(self, name):
        if name in self.default_groups:
            return False
        if 'user_groups' not in self.data:
            self.data['user_groups'] = {}
        self.data['user_groups'].pop(name)
        return True

    def set_email_login(self, enabled, default_group_name):
        if 'login_method' not in self.data:
            self.data['login_method'] = {}
        self.data['login_method']['email_login'] = {
            'enabled': enabled,
            'default_group_name': default_group_name,
        }
        return True

    def set_guest_login(self, enabled, default_group_name):
        if 'login_method' not in self.data:
            self.data['login_method'] = {}
        self.data['login_method']['guest_login'] = {
            'enabled': enabled,
            'default_group_name': default_group_name,
        }
        return True


class DatabaseRecipeController(RecipeController):
    def common_init(self):
        self.data['recipe_type'] = 'database'

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