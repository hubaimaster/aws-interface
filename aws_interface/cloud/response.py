

def _get_header(content_type='application/json'):
    api_gateway_response_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Content-Type': content_type
    }
    return api_gateway_response_header


class Response(dict):
    def __init__(self, body, content_type='application/json', status_code=200):
        header = _get_header(content_type)
        self['statusCode'] = status_code
        self['header'] = header
        self['body'] = body
        if 'error' in body:
            self['error'] = body['error']