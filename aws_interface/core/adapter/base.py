from abc import ABCMeta
from core.api import *
from resource import get_resource_allocator
from contextlib import contextmanager
from sdk.python3.aws_interface import Client
from shortuuid import uuid
from secrets import token_urlsafe


class Adapter(metaclass=ABCMeta):
    """
    allocation_status: 'busy' | 'able'
    """
    allocation_status = 'able'

    def _get_app_id(self):
        raise NotImplementedError

    def _get_credential(self):
        raise NotImplementedError

    def _get_vendor(self):
        raise NotImplementedError

    @contextmanager
    def open_api(self, api_class):
        """
            You can do this:
            with adapter.open_api(api_class) as api:
                api.method_in_api_class(...)
        """
        api = api_class(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_auth(self):
        """
            You can do this:
            with adapter.open_api_auth() as auth:
            use(auth)
        """
        api = AuthAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_bill(self):
        api = BillAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_database(self):
        api = DatabaseAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_storage(self):
        api = StorageAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_logic(self):
        api = LogicAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_log(self):
        api = LogAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_schedule(self):
        api = ScheduleAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_notification(self):
        api = NotificationAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_trigger(self):
        api = TriggerAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    @contextmanager
    def open_api_fast_database(self):
        api = FastDatabaseAPI(self._get_vendor(), self._get_credential(), self._get_app_id())
        yield api

    def generate_sdk(self, platform):
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        return allocator.generate_sdk(platform)

    def allocate_resource(self):
        if self.allocation_status == 'able':
            self.allocation_status = 'busy'
            allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
            allocator.create()
            self.allocation_status = 'able'
            return True

    def get_allocation_status(self):
        """
        :return: 'busy' | 'able'
        """
        return self.allocation_status

    def terminate_resource(self):
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        allocator.terminate()

    @DeprecationWarning
    def get_sdk(self):
        """
        This function should be destroyed.
        You should have to use open_sdk(..) instead.
        :return:
        """
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        client = Client(allocator.get_rest_api_url())
        return client

    @contextmanager
    def open_sdk(self):
        """
        Return SDK object that has been logged-in as group in groups
        :param groups: Groups the logged in user belongs to
        :return: Client
        """
        client = Client()
        client.session_id = self.generate_session_id(['admin'])
        client.url = self.get_rest_api_url()
        # print('client.url:', client.url, ', client.session_id:', client.session_id)
        with self.open_api_auth() as auth_api:
            yield client
            resp = client.auth_get_me()
            user_id = resp.get('item').get('id')
            client.auth_logout()
            auth_api.delete_user(user_id)

    def generate_session_id(self, groups):
        with self.open_api_auth() as auth_api:
            email = '{}@system.com'.format(uuid())
            password = '{}'.format(token_urlsafe(32))
            auth_api.create_user(email, password, {
                'role': 'Admin session for running function'
            })
            session_id = auth_api.create_session(email, password)['session_id']
            user_id = auth_api.get_user_by_email(email)['item']['id']
            for group in groups:
                auth_api.attach_user_group(user_id, group)
            return session_id

    def get_rest_api_url(self):
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        return allocator.get_rest_api_url()
