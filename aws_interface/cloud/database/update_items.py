
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
    error_list = [None] * len(pairs)
    success_list = [False] * len(pairs)

    policy_codes_by_partition = {}

    def update_work(idx, item_id):
        new_item = pairs[item_id]
        item = resource.db_get_item(item_id)
        if database_can_not_access_to_item(item):
            error_list[idx] = error.NO_SUCH_PARTITION
            return

        if item['partition'] in policy_codes_by_partition:
            policy_code = policy_codes_by_partition[item['partition']]
        else:
            policy_code = get_policy_code(resource, item['partition'], 'update')
            policy_codes_by_partition[item['partition']] = policy_code

        if match_policy(policy_code, user, new_item):
            # Put the value in the previous item that is not in the new field
            for key in item:
                if key not in new_item:
                    new_item[key] = item[key]
            # Remove field if value is None
            for key, value in new_item.copy().items():
                if value is None:
                    new_item.pop(key)

            new_item = {key: value for key, value in new_item.items() if value != '' and value != {} and value != []}
            index_keys = util.get_index_keys_to_index(resource, user, item['partition'], 'w')
            success = resource.db_update_item(item_id, new_item, index_keys=index_keys)
            success_list[idx] = success
        else:
            error_list[idx] = error.UPDATE_POLICY_VIOLATION

    with ThreadPoolExecutor(max_workers=len(pairs)) as exc:
        for _idx, _item_id in enumerate(pairs):
            exc.submit(update_work, _idx, _item_id)

    body['error_list'] = error_list
    body['success_list'] = success_list
    return body
