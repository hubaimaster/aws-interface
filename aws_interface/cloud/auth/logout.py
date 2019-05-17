
from cloud.response import Response
from cloud.crypto import Hash

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'message': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']

    session_id = params.get('session_id', None)
    resource.db_delete_item(Hash.sha3_512(session_id))
    body['message'] = '로그아웃 되었습니다.'
    return Response(body)
