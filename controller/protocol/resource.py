
class Resource(dict):
    def __init__(self, request):
        self.request = request
        raise NotImplementedError()

    def create_table(self, service_name):
        raise NotImplementedError()

    def create_table_index(self, service_name, hash_key, sort_key):
        raise NotImplementedError()

    def create_item(self, service_name, item_json):
        raise NotImplementedError()

    def get_table_list(self, service_name):
        raise NotImplementedError()

    def get_table(self, service_name):
        raise NotImplementedError()

    def set_table_value(self, service_name, key, value):
        raise NotImplementedError()

    def get_table_value(self, service_name, key):
        raise NotImplementedError()

    def deploy_table(self, service_name):
        raise NotImplementedError()
