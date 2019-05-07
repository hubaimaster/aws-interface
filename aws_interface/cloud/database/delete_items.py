
from cloud.response import Response
from cloud.util import has_write_permission
from concurrent.futures import ThreadPoolExecutor
# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': 'list',
    },
    'output_format': {
        'success': 'bool',
        'message': 'str',
    }
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    success = True

    item_ids = params.get('item_ids', [])
    if len(item_ids) > 128:
        body['message'] = 'number of item_ids must be less than 128'
        body['success'] = False
        return Response(body)

    with ThreadPoolExecutor(max_workers=32) as executor:
        for _item_id in item_ids:
            def delete_item(item_id):
                item = resource.db_get_item(item_id)
                if item and has_write_permission(user, item):
                    resource.db_delete_item(item_id)
            executor.submit(delete_item, _item_id)

    body['success'] = success
    return Response(body)
