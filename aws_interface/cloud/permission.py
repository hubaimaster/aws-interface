from functools import wraps


system_partitions = ['user', 'log', 'logic-function', 'files', 'session', 'webhook']


def database_can_not_access_to_item(item):
    partition = item.get('partition', None)
    if not partition:
        return True
    if partition in system_partitions:
        return True
    else:
        return False


class Permission:
    DEFAULT_USER_GROUPS = ['user', 'admin']

    @classmethod
    def all(cls):
        """
        Get list of all permissions
        :return: [str]
        """
        all_permissions = []
        permission_cls_list = [
            cls.Run.Auth,
            cls.Run.Database,
            cls.Run.Storage,
            cls.Run.Logic,
            cls.Run.Log
        ]
        for permission_cls in permission_cls_list:
            obj = permission_cls()
            permissions = [getattr(obj, attr) for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
            all_permissions.extend(permissions)
        return all_permissions

    class Run:
        class Auth:
            attach_group_permission = 'run:cloud.auth.attach_group_permission'
            attach_user_group = 'run:cloud.auth.attach_user_group'
            delete_sessions = 'run:cloud.auth.delete_sessions'
            delete_user = 'run:cloud.auth.delete_user'
            delete_users = 'run:cloud.auth.delete_users'
            delete_user_group = 'run:cloud.auth.delete_user_group'
            detach_group_permission = 'run:cloud.auth.detach_group_permission'
            detach_user_group = 'run:cloud.auth.detach_user_group'
            get_email_login = 'run:cloud.auth.get_email_login'
            get_guest_login = 'run:cloud.auth.get_guest_login'
            get_me = 'run:cloud.auth.get_me'
            get_session = 'run:cloud.auth.get_session'
            get_session_count = 'run:cloud.auth.get_session_count'
            get_sessions = 'run:cloud.auth.get_sessions'
            get_user = 'run:cloud.auth.get_user'
            get_user_by_email = 'run:cloud.auth.get_user_by_email'
            get_user_count = 'run:cloud.auth.get_user_count'
            get_user_groups = 'run:cloud.auth.get_user_groups'
            get_users = 'run:cloud.auth.get_users'
            guest = 'run:cloud.auth.guest'
            login = 'run:cloud.auth.login'
            login_facebook = 'run:cloud.auth.login_facebook'
            logout = 'run:cloud.auth.logout'
            put_user_group = 'run:cloud.auth.put_user_group'
            register = 'run:cloud.auth.register'
            register_admin = 'run:cloud.auth.register_admin'
            set_login_method = 'run:cloud.auth.set_login_method'
            set_user = 'run:cloud.auth.set_user'
            set_me = 'run:cloud.auth.set_me'
            get_login_method = 'run:cloud.auth.get_login_method'
            change_password = 'run:cloud.auth.change_password'
            change_password_admin = 'run:cloud.auth.change_password_admin'
            find_password = 'run:cloud.auth.find_password'

        class Database:
            create_item = 'run:cloud.database.create_item'
            create_partition = 'run:cloud.database.create_partition'
            delete_item = 'run:cloud.database.delete_item'
            delete_items = 'run:cloud.database.delete_items'
            delete_partition = 'run:cloud.database.delete_partition'
            delete_partitions = 'run:cloud.database.delete_partitions'
            get_item = 'run:cloud.database.get_item'
            get_item_count = 'run:cloud.database.get_item_count'
            get_items = 'run:cloud.database.get_items'
            get_partitions = 'run:cloud.database.get_partitions'
            put_item_field = 'run:cloud.database.put_item_field'
            get_policy_code = 'run:cloud.database.get_policy_code'
            put_policy = 'run:cloud.database.put_policy'
            query_items = 'run:cloud.database.query_items'
            update_item = 'run:cloud.database.update_item'

        class Log:
            create_log = 'run:cloud.log.create_log'
            get_logs = 'run:cloud.log.get_logs'

        class Logic:
            create_function = 'run:cloud.logic.create_function'
            create_function_test = 'run:cloud.logic.create_function_test'
            create_trigger = 'run:cloud.logic.create_trigger'
            delete_function = 'run:cloud.logic.delete_function'
            delete_trigger = 'run:cloud.logic.delete_trigger'
            get_function = 'run:cloud.logic.get_function'
            get_function_file_paths = 'run:cloud.logic.get_function_file_paths'
            get_function_file = 'run:cloud.logic.get_function_file'
            get_function_tests = 'run:cloud.logic.get_function_tests'
            get_function_zip_b64 = 'run:cloud.logic.get_function_zip_b64'
            get_functions = 'run:cloud.logic.get_functions'
            get_trigger = 'run:cloud.logic.get_trigger'
            get_triggers = 'run:cloud.logic.get_triggers'
            put_function_file = 'run:cloud.logic.put_function_file'
            run_function = 'run:cloud.logic.run_function'
            update_function = 'run:cloud.logic.update_function'
            update_trigger = 'run:cloud.logic.update_trigger'
            delete_function_test = 'run:cloud.logic.delete_function_test'

            create_webhook = 'run:cloud.logic.create_webhook'
            delete_webhook = 'run:cloud.logic.delete_webhook'
            get_webhook = 'run:cloud.logic.get_webhook'
            get_webhook_url = 'run:cloud.logic.get_webhook_url'
            get_webhooks = 'run:cloud.logic.get_webhooks'

        class Storage:
            delete_b64 = 'run:cloud.storage.delete_b64'
            download_b64 = 'run:cloud.storage.download_b64'
            get_b64_info_items = 'run:cloud.storage.get_b64_info_items'
            upload_b64 = 'run:cloud.storage.upload_b64'
            get_policy_code = 'run:cloud.storage.get_policy_code'
            put_policy = 'run:cloud.storage.put_policy'

    default_user_permissions = [
        Run.Auth.get_me,
        Run.Auth.get_session,
        Run.Auth.guest,
        Run.Auth.login,
        Run.Auth.login_facebook,
        Run.Auth.logout,
        Run.Auth.register,
        Run.Auth.set_me,
        Run.Auth.get_login_method,

        Run.Database.create_item,
        Run.Database.delete_item,
        Run.Database.delete_items,
        Run.Database.get_item,
        Run.Database.get_item_count,
        Run.Database.get_items,
        Run.Database.put_item_field,
        Run.Database.query_items,
        Run.Database.update_item,

        Run.Log.create_log,

        Run.Logic.run_function,

        Run.Storage.delete_b64,
        Run.Storage.download_b64,
        Run.Storage.upload_b64,
    ]

    unknown_user_permissions = [
        Run.Auth.get_me,
        Run.Auth.get_session,
        Run.Auth.guest,
        Run.Auth.login,
        Run.Auth.login_facebook,
        Run.Auth.logout,
        Run.Auth.register,
        Run.Auth.set_me,
        Run.Auth.get_login_method,

        Run.Database.create_item,
        Run.Database.delete_item,
        Run.Database.delete_items,
        Run.Database.get_item,
        Run.Database.get_item_count,
        Run.Database.get_items,
        Run.Database.put_item_field,
        Run.Database.query_items,
        Run.Database.update_item,

        Run.Log.create_log,

        Run.Logic.run_function,

        Run.Storage.delete_b64,
        Run.Storage.download_b64,
        Run.Storage.upload_b64,
    ]

    def __init__(self, data, resource):
        self.data = data
        self.resource = resource

    def has(self, permission):
        has_permission = False
        user = self.data.get('user', None)
        if user:
            groups = user.get('groups', [])
            for group_name in groups:
                group = self.resource.db_get_item('user-group-{}'.format(group_name))
                permissions = []
                if group:
                    permissions = group.get('permissions', [])
                if permission in permissions:
                    has_permission = True
                if group_name == 'admin':
                    has_permission = True
        else:  # No session
            group_name = 'unknown'
            group = self.resource.db_get_item('user-group-{}'.format(group_name))
            permissions = self.unknown_user_permissions
            if group:
                permissions = group.get('permissions', [])
            if permission in permissions:
                has_permission = True
            if group_name == 'admin':
                has_permission = True
        return has_permission

    def need(self, permission):
        if self.has(permission):
            def wrapper(func):
                @wraps(func)
                def wrap(*args, **kwargs):
                    result = func(*args, **kwargs)
                    return result
                return wrap
            return wrapper
        else:
            raise PermissionError('Permission denied [{}]'.format(permission))


class NeedPermission:
    """Class Decorator to check user permissions
    """
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            data = args[0]
            resource = args[1]
            Permission(data, resource).need(self.permission)
            result = func(*args, **kwargs)
            return result
        return decorator
