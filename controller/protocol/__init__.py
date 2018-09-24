
class Config:
    table_prefix = 'aws-interface-'


class Msg:
    success = 0, 'success'
    permission_denied = 1, 'permission denied'


class Response(dict):
    def __init__(self, msg, data=None):
        if data is not None:
            self['data'] = data
        message_code = msg[0]
        message_text = msg[1]
        self['message'] = {
            'code': message_code,
            'text': message_text
        }

    def get_data(self):
        return self['data']

    def get_message(self):
        return self['message']


class Request(dict):
    def get_param(self, key):
        raise NotImplementedError()

    def get_passport(self):
        raise NotImplementedError()


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

