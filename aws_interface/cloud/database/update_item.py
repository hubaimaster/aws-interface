#
# from cloud.permission import database_can_not_access_to_item
# from cloud.permission import Permission, NeedPermission
# from cloud.database.get_policy_code import match_policy_after_get_policy_code
# from cloud.message import error
# from cloud.database import util
#
# # Define the input output format of the function.
# # This information is used when creating the *SDK*.
# info = {
#     'input_format': {
#         'session_id': 'str',
#         'item_id': 'str',
#         'item': 'map',
#     },
#     'output_format': {
#         'success': 'bool'
#     },
#     'description': 'Update item'
# }
#
#
# @NeedPermission(Permission.Run.Database.update_item)
# def do(data, resource):
#     body = {}
#     params = data['params']
#     user = data['user']
#
#     item_id = params.get('item_id', None)
#     new_item = params.get('item', {})
#
#     item = resource.db_get_item(item_id)
#     # 시스템 파티션 접근 제한
#     if database_can_not_access_to_item(item['partition']):
#         body['error'] = error.PERMISSION_DENIED
#         return body
#
#     # 등록된 파티션이 아닌경우
#     if not resource.db_has_partition(item['partition']):
#         body['item'] = None
#         body['error'] = error.UNREGISTERED_PARTITION
#         return body
#
#     if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item):
#         # Put the value in the previous item that is not in the new field
#         for key in item:
#             if key not in new_item:
#                 new_item[key] = item[key]
#         # Remove field if value is None
#         new_item['partition'] = item['partition']
#         for key, value in new_item.copy().items():
#             if value is None:
#                 new_item.pop(key)
#
#         new_item = {key: value for key, value in new_item.items() if value != '' and value != {} and value != []}
#         index_keys = util.get_index_keys_to_index(resource, user, item['partition'], 'w')
#         success = resource.db_update_item(item_id, new_item, index_keys=index_keys)
#         body['success'] = success
#     else:
#         body['error'] = error.UPDATE_POLICY_VIOLATION
#     return body

from cloud.permission import database_can_not_access_to_item
from cloud.permission import Permission, NeedPermission
from cloud.database.get_policy_code import match_policy_after_get_policy_code
from cloud.message import error
from cloud.database import util

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'item_id': 'str',
        'item': 'map',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Update item version 2.0, Low update WCU consumed'
}


@NeedPermission(Permission.Run.Database.update_item)
def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    item_id = params.get('item_id', None)
    new_item = params.get('item', {})

    item = resource.db_get_item(item_id)
    # 시스템 파티션 접근 제한
    if database_can_not_access_to_item(item['partition']):
        body['error'] = error.PERMISSION_DENIED
        return body

    # 등록된 파티션이 아닌경우
    if not resource.db_has_partition(item['partition']):
        body['item'] = None
        body['error'] = error.UNREGISTERED_PARTITION
        return body

    # Remove null
    # for key, value in new_item.copy().items():
    #     if value is None:
    #         new_item.pop(key)

    # Put the value in the previous item that is not in the new field
    new_item = {key: value for key, value in new_item.items() if value != '' and value != {} and value != []}
    new_item = util.simplify_item(item, new_item)
    new_item['partition'] = item['partition']

    if match_policy_after_get_policy_code(resource, 'update', item['partition'], user, item, new_item=new_item):
        index_keys = util.get_index_keys_to_index(resource, user, item['partition'], 'w')
        success = resource.db_update_item_v2(item_id, new_item, index_keys=index_keys)
        body['success'] = success
    else:
        body['error'] = error.UPDATE_POLICY_VIOLATION
    return body
