
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'count_system_user': 'bool'
    },
    'output_format': {
        'item': {
            'count': 'int'
        }
    },
    'description': 'Return count of all users'
}


@NeedPermission(Permission.Run.Auth.get_user_count)
def do(data, resource):
    body = {}
    params = data.get('params', {})
    count_system_user = params.get('count_system_user', False)
    partition = 'user'
    count = resource.db_get_count(partition)
    if not count_system_user:
        query = [{
            'condition': 'in',
            'option': 'or',
            'field': 'email',
            'value': '@system.com'
        }]
        items, start_key = resource.db_query(partition, query, None, limit=10000)
        count -= len(items)
        while start_key:
            items, start_key = resource.db_query(partition, query, start_key, limit=10000)
            count -= len(items)
    body['item'] = {
        'count': count
    }
    return body
