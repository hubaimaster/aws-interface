
from concurrent.futures import ThreadPoolExecutor
from cloud.permission import Permission, NeedPermission, database_can_not_access_to_item
from cloud.database.get_policy_code import match_policy, get_policy_code
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_ids': '[str]',
        'max_workers': 'int?'
    },
    'output_format': {
        'success_list': '[bool]'
    },
    'description': 'Delete items'
}


@NeedPermission(Permission.Run.Database.delete_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_ids = params.get('item_ids', [])
    max_workers = params.get('max_workers', None)
    success_list = [False] * len(item_ids)

    # if len(item_ids) > 128:
    #     body['error'] = error.NUM_OF_BATCH_ITEMS_MUST_BE_LESS_THAN_128
    #     print(body['error'])
    #     return body

    policy_codes_by_partition = {}

    def delete_item(idx, item_id):
        item = resource.db_get_item(item_id)

        # 시스템 파티션 접근 제한
        if database_can_not_access_to_item(item['partition']):
            success_list[idx] = False
            return
        # 등록된 파티션이 아닌경우
        if not resource.db_has_partition(item['partition']):
            success_list[idx] = False
            return

        if item['partition'] in policy_codes_by_partition:
            policy_code = policy_codes_by_partition[item['partition']]
        else:
            policy_code = get_policy_code(resource, item['partition'], 'delete')
            policy_codes_by_partition[item['partition']] = policy_code

        if item and match_policy(policy_code, user, item):
            success = resource.db_delete_item(item_id)
            success_list[idx] = success
    if not max_workers:
        max_workers = len(item_ids)
    max_workers = int(max_workers) + 1
    max_workers = min(32, max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _idx, _item_id in enumerate(item_ids):
            executor.submit(delete_item, _idx, _item_id)

    body['success_list'] = success_list
    return body
