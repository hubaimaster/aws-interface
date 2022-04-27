
from cloud.permission import Permission, NeedPermission, database_can_not_access_to_item
from cloud.message import error
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.shortuuid import uuid
from cloud.database import util
from concurrent.futures import ThreadPoolExecutor
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'items': '[dict]',
        'partition': 'str',
        'max_workers': 'int?'
    },
    'output_format': {
        'item_ids': '[str]',
        'error_list': '[dict]',
    },
    'description': 'Create items and return item_ids'
}


@NeedPermission(Permission.Run.Database.create_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    if user:
        user_id = user.get('id', None)
    else:
        user_id = None

    partition = params.get('partition', None)
    max_workers = params.get('max_workers', None)

    if database_can_not_access_to_item(partition):
        body['error'] = error.PERMISSION_DENIED
        return body

    # Check partition has been existed
    if not resource.db_has_partition(partition):
        body['error'] = error.NO_SUCH_PARTITION
        return body

    items = params.get('items', [])
    error_list = [None] * len(items)
    item_ids = [None] * len(items)

    index_keys = util.get_index_keys_to_index(resource, user, partition, 'w')
    sort_keys = util.get_sort_keys(resource)
    policy_code = get_policy_code(resource, partition, 'create')

    def try_put_item(idx, item):
        item['id'] = uuid()
        if 'owner' not in item:
            item['owner'] = user_id
        item = {key: value for key, value in item.items() if value != '' and value != {} and value != []}
        if match_policy(policy_code, user, item):
            resource.db_put_item(partition, item, item_id=item['id'], index_keys=index_keys, sort_keys=sort_keys)
            item_ids[idx] = item.get('id', None)
        else:
            error_list[idx] = error.PERMISSION_DENIED

    if not max_workers:
        max_workers = len(items)
    max_workers = int(max_workers) + 1
    max_workers = min(32, max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as exc:
        for _idx, _item in enumerate(items):
            exc.submit(try_put_item, _idx, _item)

    body['error_list'] = error_list
    body['item_ids'] = item_ids
    return body
