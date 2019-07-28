
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
    'description': 'Return count of all sessions'
}


@NeedPermission(Permission.Run.Auth.get_session_count)
def do(data, resource):
    body = {}
    partition = 'session'
    count = resource.db_get_count(partition)
    body['item'] = {
        'count': count
    }
    return body
