from abc import ABCMeta
from core.api import *
from resource import get_resource_allocator
from contextlib import contextmanager
from sdk.python3.aws_interface import Client
from shortuuid import uuid


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
    def open_sdk(self, groups=['admin']):
        """
        Return SDK object that has been logged-in as group in groups
        :param groups: Groups the logged in user belongs to
        :return: Client
        """
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        client = Client(allocator.get_rest_api_url())
        with self.open_api_auth() as auth_api:
            email = '{}@admin.com'.format(uuid())
            password = '{}'.format(uuid())
            auth_api.create_user(email, password, {})
            client.auth_login(email, password)
            resp = client.auth_get_me()
            user_id = resp.get('item').get('id')
            for group in groups:
                auth_api.attach_user_group(user_id, group)
            yield client
            client.auth_logout()
            auth_api.delete_user(user_id)
