
from cloud.response import Response
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'permissions': ['str'],
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    permissions = sorted(Permission.all())
    body['permissions'] = permissions
    return Response(body)
