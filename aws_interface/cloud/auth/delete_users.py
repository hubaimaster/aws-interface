
from cloud.response import Response
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_ids': ['str'],
    },
    'output_format': {

    }
}


@NeedPermission(Permission.Run.Auth.delete_users)
def do(data, resource):
    body = {}
    params = data['params']

    user_ids = params.get('user_ids', [])
    _ = resource.db_delete_item_batch(user_ids)

    return Response(body)
