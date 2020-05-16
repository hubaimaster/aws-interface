
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'start_key': 'str?',
        'reverse': 'bool?',
        'limit': 'int?'
    },
    'output_format': {
        'items': 'list',
        'end_key': 'str'
    },
    'description': 'Get all list of schedules.'
}


@NeedPermission(Permission.Run.Schedule.get_schedules)
def do(data, resource):
    body = {}
    params = data['params']
    start_key = params.get('start_key', None)
    reverse = params.get('reverse', False)
    limit = params.get('limit', 100)
    inst = []
    items, end_key = resource.db_query('schedule', inst, start_key=start_key, reverse=reverse, limit=limit)
    body['items'] = items
    body['end_key'] = end_key
    return body
