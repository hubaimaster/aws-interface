from controller.protocol.request import Request


class AwsRequest(Request):
    def __init__(self, access_key, secret_key, region, params):
        self['passport'] = {'access_key': access_key,
                            'secret_key': secret_key,
                            'region': region}
        self['params'] = params

    def get_param(self, key):
        if key in self['params']:
            return self['params'][key]
        else:
            raise BaseException(key, 'not in', self['params'])

    def get_passport(self):
        return self['passport']

