
from cloud.response import Response
from cloud.permission import has_write_permission
from concurrent.futures import ThreadPoolExecutor
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': 'list',
    },
    'output_format': {
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Database.delete_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_ids = params.get('item_ids', [])
    if len(item_ids) > 128:
        body['error'] = error.NUM_OF_BATCH_ITEMS_MUST_BE_LESS_THAN_128
        return Response(body)

    with ThreadPoolExecutor(max_workers=32) as executor:
        for _item_id in item_ids:
            def delete_item(item_id):
                item = resource.db_get_item(item_id)
                if item and has_write_permission(user, item):
                    resource.db_delete_item(item_id)
            executor.submit(delete_item, _item_id)

    return Response(body)
