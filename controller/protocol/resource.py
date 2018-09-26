
class Resource(dict):
    def __init__(self, request):
        raise NotImplementedError()

    def create_table(self, name):
        raise NotImplementedError()

    def create_table_index(self, table_name, index_name, hash_key, sort_key):
        raise NotImplementedError()

    def create_item(self, table_name, item_json):
        raise NotImplementedError()

    def get_table_list(self, prefix):
        raise NotImplementedError()

    def get_table(self, name):
        raise NotImplementedError()

    def set_table_value(self, table_name, key, value):
        raise NotImplementedError()

    def get_table_value(self, table_name, key):
        raise NotImplementedError()
