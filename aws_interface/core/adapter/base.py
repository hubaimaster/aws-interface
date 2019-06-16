from abc import ABCMeta
from core.api import *
from resource import get_resource_allocator
from contextlib import contextmanager
from sdk.python3.aws_interface import Client


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

    def get_sdk(self):
        allocator = get_resource_allocator(self._get_vendor(), self._get_credential(), self._get_app_id())
        client = Client(allocator.get_rest_api_url())
        return client
