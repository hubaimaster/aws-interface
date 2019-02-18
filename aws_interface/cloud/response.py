

def _get_header(content_type='application/json'):
    api_gateway_response_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Requested-With',
        'Access-Control-Allow-Credentials': True,
        'Content-Type': content_type
    }
    return api_gateway_response_header


class Response(dict):
    def __init__(self, body, content_type='application/json', status_code=200):
        header = _get_header(content_type)
        self['statusCode'] = status_code
        self['header'] = header
        self['body'] = body
