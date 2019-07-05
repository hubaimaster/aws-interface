
from cloud.response import Response
from cloud.crypto import Hash
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Sign-out and remove session'
}


@NeedPermission(Permission.Run.Auth.logout)
def do(data, resource):
    body = {}
    params = data['params']

    session_id = params.get('session_id', None)
    if resource.db_delete_item(Hash.sha3_512(session_id)):
        body['success'] = True
        return Response(body)
    else:
        body['success'] = False
        body['error'] = error.LOGOUT_FAILED
        return Response(body)
