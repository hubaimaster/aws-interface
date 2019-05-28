
from cloud.response import Response
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
        'error?': {
            'code': 'int',
            'message': 'str',
        }
    }
}


@NeedPermission(Permission.Run.Log.create_log)
def do(data, resource):
    partition = 'log'
    body = {}
    params = data['params']
    user = data.get('user', None)

    event_source = params.get('event_source')
    event_name = params.get('event_name')
    event_param = params.get('event_param')

    if user:
        item = dict()
        item['event_name'] = event_name
        item['event_param'] = event_param
        item['event_source'] = event_source
        item['owner'] = user.get('id')

        success = resource.db_put_item(partition, item)
        if success:
            return Response(body)
        else:
            body['error'] = error.LOG_CREATION_FAILED
            return Response(body)
    else:
        body['error'] = error.INVALID_SESSION
        return Response(body)
