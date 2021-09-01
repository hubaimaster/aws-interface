
from concurrent.futures import ThreadPoolExecutor
from cloud.permission import Permission, NeedPermission
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.message import error
from cloud.database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': '[str]',
        'max_workers': 'int?',
        'join': "{\"user_id\": \"user\", "
                " \"info.user_id\": \"info.user\","
                " \"info_user_id\": \"user\", ...}"
    },
    'output_format': {
        'items': '[dict]',
        'errors': '[dict]'
    },
    'description': 'Batch get items'
}


@NeedPermission(Permission.Run.Database.batch_get_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_ids = params.get('item_ids', [])
    max_workers = params.get('max_workers', None)
    join = params.get('join', {})

    # if len(item_ids) > 128:
    #     body['error'] = error.NUM_OF_BATCH_ITEMS_MUST_BE_LESS_THAN_128
    #     print(body['error'])
    #     return body

    read_policy_codes_by_partition = {}
    join_policy_codes_by_partition = {}
    items_to_return = [None] * len(item_ids)
    errors = [None] * len(item_ids)

    def get_item(idx, item_id):
        item = resource.db_get_item(item_id)

        # 시스템 파티션 접근 제한 읽기에선 허용.
        # if database_can_not_access_to_item(item['partition']):
        #     items_to_return[idx] = None
        #     errors[idx] = error.PERMISSION_DENIED
        #     return
        # 등록된 파티션이 아닌경우
        if not resource.db_has_partition(item['partition']):
            items_to_return[idx] = None
            errors[idx] = error.UNREGISTERED_PARTITION
            return

        if item['partition'] in read_policy_codes_by_partition:
            policy_code = read_policy_codes_by_partition[item['partition']]
        else:
            policy_code = get_policy_code(resource, item['partition'], 'read')
            read_policy_codes_by_partition[item['partition']] = policy_code

        if item and match_policy(policy_code, user, item):
            items_to_return[idx] = item
        else:
            errors[idx] = error.READ_POLICY_VIOLATION
            return

        # Join 유효성 검사
        if item['partition'] in join_policy_codes_by_partition:
            join_policy_code = join_policy_codes_by_partition[item['partition']]
        else:
            join_policy_code = get_policy_code(resource, item['partition'], 'join')
            join_policy_codes_by_partition[item['partition']] = join_policy_code

        if match_policy(join_policy_code, user, join):
            util.join_item(resource, user, item, join)
        else:
            errors[idx] = error.JOIN_POLICY_VIOLATION
            return

    if not max_workers:
        max_workers = len(item_ids)
    max_workers = int(max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _idx, _item_id in enumerate(item_ids):
            executor.submit(get_item, _idx, _item_id)

    body['items'] = items_to_return
    body['errors'] = errors
    return body
