
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'schedule_name': 'str',
    },
    'output_format': {
        'item': {
            '...': '...'
        },
    },
    'description': 'Get information of schedule.'
}


@NeedPermission(Permission.Run.Schedule.get_schedule)
def do(data, resource):
    body = {}
    params = data['params']
    schedule_name = params.get('schedule_name')
    inst = [
        {'field': 'schedule_name', 'value': schedule_name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('schedule', inst)
    if items:
        body['item'] = items[0]
        return body
    else:
        body['error'] = error.NO_SUCH_SCHEDULE
