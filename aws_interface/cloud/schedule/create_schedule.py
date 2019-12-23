
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'schedule_name': 'str',
        'schedule_expression': '"cron(str str str str str str str)" | rate(str)',
        'function_name': 'str',
        'payload': {
            '...': '...'
        }
    },
    'output_format': {
        'schedule_id': 'str',
    },
    'description': 'Depending on the schedule_expression, the function executes at a delay or a specified time. ' +
                   'schedule_expression must be cron or rate expression. [http://www.cronmaker.com/]'
}


@NeedPermission(Permission.Run.Schedule.create_schedule)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    session_id = params.get('session_id', None)
    schedule_name = params.get('schedule_name')
    schedule_expression = params.get('schedule_expression')
    function_name = params.get('function_name')
    payload = params.get('payload', {})

    schedule_params = {
        'module_name': 'cloud.logic.run_function',
        'payload': payload,
        'function_name': function_name,
        'session_id': session_id
    }
    inst = [
        {'field': 'schedule_name', 'value': schedule_name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('schedule', inst)
    if items:
        body['error'] = error.EXISTING_SCHEDULE
        return body

    message = resource.ev_put_schedule(schedule_name, schedule_expression, schedule_params)
    success = resource.db_put_item('schedule', {
        'session_id': session_id,
        'schedule_name': schedule_name,
        'schedule_expression': schedule_expression,
        'function_name': function_name,
        'payload': payload
    })
    body['message'] = message
    body['success'] = success
    return body
