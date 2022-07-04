
from cloud.permission import Permission, NeedPermission
from cloud.message import errorlist

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'partition': 'str',
        'mode': '"create" | "read" | "update" | "delete"',
        'code': 'str',
    },
    'output_format': {
        'result': 'Creation result'
    },
    'description': 'Put policy in the partition'
}

SERVICE = 'meta-info#database_policy'
POLICY_MODES = ['create', 'read', 'update', 'delete']


@NeedPermission(Permission.Run.FastDatabase.put_policy)
def do(data, resource):
    body = {}
    params = data['params']

    partition_to_apply = params.get('partition', None)
    mode = params.get('mode', None)
    code = params.get('code', None)

    # 필수 파라메터 체크
    if not partition_to_apply:
        raise errorlist.NEED_PARTITION

    if not mode:
        raise errorlist.NEED_MODE

    if not code:
        raise errorlist.NEED_CODE

    # 없는 모드 추가 시도시
    if mode not in POLICY_MODES:
        raise errorlist.NO_SUCH_POLICY_MODE

    pk = f'{SERVICE}@{partition_to_apply}'
    sk = f'{mode}'
    item = {
        'partition_to_apply': partition_to_apply,
        'mode': mode,
        'code': code,
    }

    body['result'] = resource._fdb_put_item_low_level(pk, sk, item)
    return body
