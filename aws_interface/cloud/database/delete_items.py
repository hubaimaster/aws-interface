
from cloud.response import Response
from concurrent.futures import ThreadPoolExecutor
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.database.get_policy_code import match_policy, get_policy_code

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

    policy_codes_by_partition = {}
    with ThreadPoolExecutor(max_workers=32) as executor:
        for _item_id in item_ids:
            def delete_item(item_id):
                item = resource.db_get_item(item_id)
                if item['partition'] in policy_codes_by_partition:
                    policy_code = policy_codes_by_partition[item['partition']]
                else:
                    policy_code = get_policy_code(resource, item['partition'], 'delete')
                    policy_codes_by_partition[item['partition']] = policy_code

                if item and match_policy(policy_code, user, item):
                    resource.db_delete_item(item_id)
            executor.submit(delete_item, _item_id)

    return Response(body)
