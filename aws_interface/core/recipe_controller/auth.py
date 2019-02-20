from .base import RecipeController


class AuthRecipeController(RecipeController):
    RECIPE = 'auth'

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
