
from cloud.response import Response


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
    },
    'output_format': {
        'success': 'bool',
    }
}


def do(data, resource):
    body = {}
    params = data['params']

    session_ids = params.get('session_ids', [])
    success = resource.db_delete_item_batch(session_ids)
    body['success'] = success
    return Response(body)
