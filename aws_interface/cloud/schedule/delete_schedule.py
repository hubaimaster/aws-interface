
from cloud.permission import Permission, NeedPermission
from cloud.message.error import NO_SUCH_SCHEDULE

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'schedule_name': 'str',
    },
    'output_format': {
        'schedule_id': 'str',
    },
    'description': 'Delete scheduled operation.'
}


@NeedPermission(Permission.Run.Schedule.delete_schedule)
def do(data, resource):
    body = {}
    params = data['params']
    schedule_name = params.get('schedule_name')
    inst = [
        {'field': 'schedule_name', 'value': schedule_name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('schedule', inst)
    if items:
        schedule_relation_name = items[0].get('schedule_relation_name')
        message = resource.ev_delete_schedule(schedule_relation_name)
        resource.db_delete_item(items[0]['id'])
        body['message'] = message
        body['success'] = True
        return body
    else:
        body['error'] = NO_SUCH_SCHEDULE
        return body
