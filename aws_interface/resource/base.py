from abc import ABCMeta
from resource.sdk import generate


class ResourceAllocator(metaclass=ABCMeta):
    def __init__(self, credential, app_id, recipes):
        self.credential = credential
        self.app_id = app_id
        self.recipes = recipes

    def get_recipes(self):
        return self.recipes

    def get_credential(self):
        return self.credential

    def get_app_id(self):
        return self.app_id

    def generate_sdk(self, platform):
        return generate(self, platform)

    # API, create and terminate.
    def create(self):
        """
        Apply/deploy the recipe to AWS backend services. This includes
        setting up interfaces through AWS Lambda and API Gateway.
        :return:
        """
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def get_rest_api_url(self):
        raise NotImplementedError

    def get_logs(self):
        raise NotImplementedError


class Resource(metaclass=ABCMeta):
    def __init__(self, credential, app_id):
        self.credential = credential
        self.app_id = app_id

    # backend resource cost
    def cost_for(self, start, end):
        raise NotImplementedError

    def cost_and_usage_for(self, start, end):
        raise NotImplementedError

    # DB ops
    def db_create_partition(self, partition):
        raise NotImplementedError

    def db_delete_partition(self, partition):
        raise NotImplementedError

    def db_delete_item(self, item_id):
        raise NotImplementedError

    def db_delete_item_batch(self, item_ids):
        raise NotImplementedError

    def db_get_item(self, item_id):
        raise NotImplementedError

    def db_get_items(self, partition, start_key=None, limit=None, reverse=False):
        raise NotImplementedError

    def db_query(self, partition, instructions, start_key=None, limit=None, reverse=False):
        """:return:items:list,end_key:str"""
        raise NotImplementedError

    def db_put_item(self, partition, item, item_id=None, creation_date=None):
        """This is connected with db_get_count"""
        raise NotImplementedError

    def db_update_item(self, item_id, item):
        raise NotImplementedError

    def db_get_count(self, partition):
        raise NotImplementedError

    # File ops
    def file_download_base64(self, file_id):
        raise NotImplementedError

    def file_upload_base64(self, file_id, file_base64):
        raise NotImplementedError

    def file_delete_base64(self, file_id):
        raise NotImplementedError
