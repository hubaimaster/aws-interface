
from cloud.permission import Permission, NeedPermission
from cloud.auth import get_policy_code

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key?': 'str',
        'limit?': 'int',
        'show_system_user?': 'bool',
        'query?': 'list'
    },
    'output_format': {
        'items': [{
            'id': 'str',
            'creationDate': 'int',
            'email': 'str',
            'passwordHash': 'str',
            'salt': 'str',
            'group': 'str',
            '...': '...',
        }, ],
        'end_key?': 'str'
    },
    'description': 'Return all users in system'
}


@NeedPermission(Permission.Run.Auth.get_users)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    start_key = params.get('start_key', None)
    limit = params.get('limit', 100)
    show_system_user = params.get('show_system_user', False)
    query = params.get('query', [])

    partition = 'user'
    if show_system_user:
        pass
    else:
        query.append({
            'condition': 'nin',
            'field': 'email',
            'value': '@system.com',
            'option': 'and'
        })

    items, end_key = resource.db_query(partition, query, start_key=start_key, limit=limit, reverse=True)
    policy_code = get_policy_code.get_policy_code(resource, partition, 'read')
    filtered = []
    for item in items:
        if get_policy_code.match_policy(policy_code, user, item):
            filtered.append(item)

    body['items'] = filtered
    body['end_key'] = end_key
    return body
