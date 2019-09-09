
from cloud.permission import Permission, NeedPermission
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',

        'event_source': 'str',
        'event_name': 'str',
        'event_param': 'str',
    },
    'output_format': {
        'success': 'bool'
    },
    'description': 'Create log'
}


def create_event(resource, user, name, param, source):
    item = dict()
    item['event_name'] = name
    item['event_param'] = param
    item['event_source'] = source
    if user and user.get('id', None):
        item['owner'] = user.get('id')
    success = resource.db_put_item('log', item)
    return success


@NeedPermission(Permission.Run.Log.create_log)
def do(data, resource):

    body = {}
    params = data['params']
    user = data.get('user', None)

    event_source = params.get('event_source')
    event_name = params.get('event_name')
    event_param = params.get('event_param')

    if user:
        success = create_event(resource, user, event_name, event_param, event_source)
        body['success'] = success
        if success:
            return body
        else:
            body['error'] = error.LOG_CREATION_FAILED
            return body
    else:
        body['error'] = error.INVALID_SESSION
        return body
