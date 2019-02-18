import json
import importlib
from abc import ABCMeta, abstractmethod


class RecipeController(metaclass=ABCMeta):
    """
    Make sure to set RECIPE_TYPE when you inherit this class.
    """
    RECIPE_TYPE = None

    def __init__(self):
        """
        To add recipe-specific actions, override __init__. Make sure to
        CALL THIS BASE __init__ FUNCTION.
        """
        self.data = dict()
        assert (type(self).RECIPE_TYPE is not None)
        self.data['recipe_type'] = type(self).RECIPE_TYPE

    def to_json(self):
        return json.dumps(self.data)

    def load_json_string(self, json_string):
        self.data = json.loads(json_string)
        # self.common_init() this should be named something like update()
        # currently, there is no use for this
        # consider redesigning the __init__ function to accept a data variable

    def get_recipe_type(self):
        return type(self).RECIPE_TYPE

    def put_cloud_api(self, name, module, permissions=['all']):  # 'cloud.auth.login'
        if 'cloud_apis' not in self.data:
            self.data['cloud_apis'] = {}
        try:
            info = importlib.import_module(module).info
        except:
            print('{} module does not have an info variable'.format(name))
            info = {}
        self.data['cloud_apis'][name] = {
            'name': name,
            'permissions': permissions,
            'module': module,
            'info': info
        }
        return True

    def get_cloud_apis(self):
        cloud_apis = self.data.get('cloud_apis', {})
        return cloud_apis.values()


class BillRecipeController(RecipeController):
    RECIPE_TYPE = 'bill'


class AuthRecipeController(RecipeController):
    RECIPE_TYPE = 'auth'

    def __init__(self):
        super(AuthRecipeController, self).__init__()
        self._init_user_group()
        self._init_cloud_api()
        self._init_login_method()

    def _init_user_group(self):
        self.default_groups = {
            'admin': '기본그룹, 모든 권한을 가지고 있습니다.',
            'owner': '기본그룹, 자신이 작성한 데이터에 대해 모든 권한을 가지고 있습니다.',
            'user': '기본그룹, 회원 가입한 일반 사용자 그룹입니다.'
        }
        for name in self.default_groups:
            description = self.default_groups[name]
            self.put_user_group(name, description)

    def _init_cloud_api(self):
        self.put_cloud_api('login', 'cloud.auth.login')
        self.put_cloud_api('guest', 'cloud.auth.guest')
        self.put_cloud_api('logout', 'cloud.auth.logout')
        self.put_cloud_api('register', 'cloud.auth.register')
        self.put_cloud_api('get_user', 'cloud.auth.get_user')
        self.put_cloud_api('get_user_count', 'cloud.auth.get_user_count', permissions=['admin'])
        self.put_cloud_api('set_user', 'cloud.auth.set_user', permissions=['owner'])
        self.put_cloud_api('delete_user', 'cloud.auth.delete_user', permissions=['owner'])

    def _init_login_method(self):
        self.get_email_login()
        self.get_guest_login()

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
    RECIPE_TYPE = 'database'

    def __init__(self):
        super(DatabaseRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('create_item', 'cloud.database.create_item')
        self.put_cloud_api('delete_item', 'cloud.database.delete_item')
        self.put_cloud_api('get_item', 'cloud.database.get_item')
        self.put_cloud_api('get_items', 'cloud.database.get_items')
        self.put_cloud_api('put_item_field', 'cloud.database.put_item_field')
        self.put_cloud_api('update_item', 'cloud.database.update_item')
        self.put_cloud_api('get_item_count', 'cloud.database.get_item_count')

    def put_partition(self, partition_name):
        if 'partitions' not in self.data:
            self.data['partitions'] = {}
        self.data['partitions'][partition_name] = {
            'name': partition_name
        }

    def get_partitions(self):
        partitions = self.data.get('partitions', {})
        return partitions

    def get_partition(self, partition_name):
        partitions = self.get_partitions()
        partition = partitions.get(partition_name, None)
        return partition

    def delete_partition(self, partition_name):
        if 'partitions' not in self.data:
            self.data['partitions'] = {}
        self.data['partitions'].pop(partition_name)
        return True


class StorageRecipeController(RecipeController):
    RECIPE_TYPE = 'storage'

    def __init__(self):
        super(StorageRecipeController, self).__init__()
        self._init_cloud_api()

    def _init_cloud_api(self):
        self.put_cloud_api('create_folder', 'cloud.storage.create_folder')
        self.put_cloud_api('upload_file', 'cloud.storage.upload_file')
        self.put_cloud_api('delete_folder', 'cloud.storage.delete_folder')
        self.put_cloud_api('delete_file', 'cloud.storage.delete_file')
        self.put_cloud_api('download_file', 'cloud.storage.download_file')
