from abc import ABCMeta


class ServiceController(metaclass=ABCMeta):
    """
    Make sure to set RECIPE when you inherit this class.
    """
    SERVICE_TYPE = None

    def __init__(self, resource, app_id):
        """
        Initiate service controller. Make sure to call this from the
        __init__ method of child classes.

        :param bundle:
        Dict containing keys to initialize boto3 session. May include
        access_key, secret_key, region_name

        :param app_id:
        """
        assert(type(self).SERVICE_TYPE is not None)
        self.app_id = app_id
        self.resource = resource
