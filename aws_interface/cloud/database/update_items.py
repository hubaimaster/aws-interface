from cloud.permission import database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.database.get_policy_code import get_policy_code, match_policy
from cloud.message import error
from cloud.database import util
from concurrent.futures import ThreadPoolExecutor


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'pairs': '[item_id: item]',
        'max_workers': 'int?'
    },
    'output_format': {
        'success_list': '[bool]',
        'error_list': '[dict]',
    },
    'description': 'Update items'
}


@NeedPermission(Permission.Run.Database.update_items)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    pairs = params.get('pairs', None)
    max_workers = params.get('max_workers', None)
    error_list = [None] * len(pairs)
    success_list = [False] * len(pairs)

    policy_codes_by_partition = {}

    partitions = resource.db_get_partitions()
    partition_names = [partition['name'] for partition in partitions]
    sort_keys = util.get_sort_keys(resource)

    def update_work(idx, item_id):
        new_item = pairs[item_id]
        item = resource.db_get_item(item_id)
        # 아이템 없는 경우
        if not item:
            error_list[idx] = error.NO_SUCH_ITEM
            return
        # 시스템 파티션 접근 제한
        if database_can_not_access_to_item(item['partition']):
            error_list[idx] = error.PERMISSION_DENIED
            return
        # 등록된 파티션이 아닌경우
        if item['partition'] not in partition_names:
            error_list[idx] = error.UNREGISTERED_PARTITION
            return

        if item['partition'] in policy_codes_by_partition:
            policy_code = policy_codes_by_partition[item['partition']]
        else:
            policy_code = get_policy_code(resource, item['partition'], 'update')
            policy_codes_by_partition[item['partition']] = policy_code

        # Remove field if value is None
        # for key, value in new_item.copy().items():
        #     if value is None:
        #         new_item.pop(key)

        new_item = {key: value for key, value in new_item.items() if value != '' and value != {} and value != []}
        new_item = util.simplify_item(item, new_item)
        new_item['partition'] = item.get('partition', None)
        new_item['creation_date'] = item.get('creation_date', None)

        if match_policy(policy_code, user, item, new_item=new_item):
            index_keys = util.get_index_keys_to_index(resource, user, item['partition'], 'w')

            # 소트키는 무조건 업데이트시 포함해야함.
            for sort_key in sort_keys:
                s_key = sort_key.get('sort_key', None)
                if s_key and s_key not in new_item and item.get(s_key, None) is not None:
                    new_item[s_key] = item.get(s_key, None)

            success = resource.db_update_item_v2(item_id, new_item, index_keys=index_keys, sort_keys=sort_keys)
            success_list[idx] = success
        else:
            error_list[idx] = error.UPDATE_POLICY_VIOLATION
    if not max_workers:
        max_workers = len(pairs)
    max_workers = int(max_workers) + 1
    max_workers = min(32, max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as exc:
        for _idx, _item_id in enumerate(pairs):
            exc.submit(update_work, _idx, _item_id)

    body['error_list'] = error_list
    body['success_list'] = success_list
    return body
