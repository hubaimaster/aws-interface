from abc import ABCMeta
from resource import get_resource


class API(metaclass=ABCMeta):
    """
    Make sure to set SC_CLASS when you inherit this class.
    """
    SC_CLASS = None

    def __init__(self, vendor, credentials, app_id):
        """
        :param credentials:
        :param app_id:
        """
        self.credentials = credentials
        self.app_id = app_id

        resource = get_resource(vendor, credentials, app_id)
        # self.service_controller = type(self).SC_CLASS(resource, app_id)
        self.resource = resource
