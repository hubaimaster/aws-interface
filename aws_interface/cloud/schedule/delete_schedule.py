
from cloud.permission import Permission, NeedPermission


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

    message = resource.ev_delete_schedule(schedule_name)
    body['message'] = message
    return body
