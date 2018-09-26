
class Request(dict):
    def get_param(self, key):
        raise NotImplementedError()

    def get_passport(self):
        raise NotImplementedError()
