
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database import util
from concurrent.futures import ThreadPoolExecutor
import time

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'partition': 'str',
    },
    'output_format': {
        'indexed_count': 'int',
    },
    'description': 'Get items and its end_key to iterate'
}


@NeedPermission(Permission.Run.Database.reindex_partition)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']
    start = time.time()
    partition = params.get('partition', None)
    if not resource.db_has_partition(partition):
        body['error'] = error.NO_SUCH_PARTITION
        return body

    indexed_count = 0

    limit = 1000
    index_keys = util.get_index_keys_to_index(resource, user, partition, 'w')
    with ThreadPoolExecutor(max_workers=32) as ex:
        start_key = None
        items, start_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit)
        indexed_count += len(items)
        print('indexed_count:', indexed_count)
        for item in items:
            ex.submit(resource.db_update_item, item['id'], item, index_keys)
        while start_key:
            items, start_key = resource.db_get_items_in_partition(partition, start_key=start_key, limit=limit)
            indexed_count += len(items)
            print('indexed_count:', indexed_count)
            for item in items:
                ex.submit(resource.db_update_item, item['id'], item, index_keys)

    print('Complete re-indexing:', indexed_count)
    print('Duration:', (time.time() - start))
    body['indexed_count'] = indexed_count
    return body
