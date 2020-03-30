import cloud.libs.simplejson as json


def _get_headers(content_type='application/json'):
    api_gateway_response_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Content-Type': content_type
    }
    return api_gateway_response_header


class AWSResponse(dict):
    def __init__(self, body, content_type='application/json', status_code=200):
        headers = _get_headers(content_type)
        self['statusCode'] = status_code
        self['headers'] = headers
        if isinstance(body, dict):
            self['body'] = json.dumps(body, default=lambda o: '<not serializable>')
        else:
            self['body'] = body
        self['isBase64Encoded'] = False
