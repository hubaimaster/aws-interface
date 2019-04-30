
from cloud.response import Response

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
        'success': 'bool',
    }
}


def do(data, resource):
    partition = 'log'
    body = {}
    params = data['params']
    user = data['user']

    event_source = params.get('event_source')
    event_name = params.get('event_name')
    event_param = params.get('event_param')

    item = dict()
    item['event_name'] = event_name
    item['event_param'] = event_param
    item['event_source'] = event_source
    item['owner'] = user.get('id', None)

    success = resource.db_put_item(partition, item)

    body['success'] = success
    return Response(body)
