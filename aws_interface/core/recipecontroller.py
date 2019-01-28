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

    def put_cloud_api(self, name, module, permission='all'):  # 'cloud.auth.login'
        if 'cloud_apis' not in self.data:
            self.data['cloud_apis'] = {}
        self.data['cloud_apis'][name] = {
            'name': name,
            'permission': permission,
            'module': module,
        }
        return True

    def get_cloud_apis(self):
        cloud_apis = self.data.get('cloud_apis', [])
        return cloud_apis.values()


class BillRecipeController(RecipeController):
    def common_init(self):
        self.data['recipe_type'] = 'bill'


class AuthRecipeController(RecipeController):
    def common_init(self):
        self.data['recipe_type'] = 'auth'
        # put system default groups
        self._init_user_group()
        self._init_cloud_api()

    def _init_user_group(self):
        self.default_groups = {
            'all': '기본그룹, 로그인 하지 않은 익명 그룹입니다.',
            'admin': '기본그룹, 모든 권한을 가지고 있습니다.',
            'owner': '기본그룹, 자신이 작성한 데이터에 대해 모든 권한을 가지고 있습니다.',
            'user': '기본그룹, 회원 가입한 일반 사용자 그룹입니다.'
        }
        for name in self.default_groups:
            description = self.default_groups[name]
            self.put_user_group(name, description)

    def _init_cloud_api(self):
        self.put_cloud_api('login', 'cloud.auth.login')
        self.put_cloud_api('logout', 'cloud.auth.logout')
        self.put_cloud_api('register', 'cloud.auth.register')
        self.put_cloud_api('get_user', 'cloud.auth.get_user')
        self.put_cloud_api('get_user_count', 'cloud.auth.get_user_count', permission='admin')
        self.put_cloud_api('set_user', 'cloud.auth.set_user', permission='owner')
        self.put_cloud_api('delete_user', 'cloud.auth.delete_user', permission='owner')

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

    def get_email_login(self):
        if not self.data.get('login_method', {}).get('email_login', None):
            self.set_email_login(True, 'user')
        return self.data['login_method']['email_login']

    def get_guest_login(self):
        if not self.data.get('login_method', {}).get('guest_login', None):
            self.set_guest_login(True, 'user')
        return self.data['login_method']['guest_login']


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
