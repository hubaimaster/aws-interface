
from cloud.response import Response
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {

    },
    'output_format': {
        'item': {
            'count': 'int'
        }
    },
    'description': 'Return count of all users'
}


@NeedPermission(Permission.Run.Auth.get_user_count)
def do(data, resource):
    body = {}
    partition = 'user'
    count = resource.db_get_count(partition)
    body['item'] = {
        'count': count
    }
    return Response(body)
