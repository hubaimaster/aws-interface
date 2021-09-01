
from cloud.permission import Permission, NeedPermission
from concurrent.futures import ThreadPoolExecutor


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'user_ids': ['str'],
        'max_workers': 'int?'
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Delete users'
}


@NeedPermission(Permission.Run.Auth.delete_users)
def do(data, resource):
    body = {}
    params = data['params']

    user_ids = params.get('user_ids', [])

    item_ids = user_ids
    max_workers = params.get('max_workers', None)
    success_list = [False] * len(item_ids)

    def delete_item(idx, item_id):
        item = resource.db_get_item(item_id)

        # user 파티션이 아닌경우
        if item['partition'] != 'user':
            success_list[idx] = False
            return
        success = resource.db_delete_item(item_id)
        success_list[idx] = success

    if not max_workers:
        max_workers = len(item_ids)
    max_workers = int(max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _idx, _item_id in enumerate(item_ids):
            executor.submit(delete_item, _idx, _item_id)

    body['success_list'] = success_list
    return body
