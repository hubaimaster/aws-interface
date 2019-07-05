
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.shortuuid import uuid
import base64

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
        'trigger_type': 'str',
        'description?': 'str',
        'option?': 'map',
        'runnable?': 'bool',
    },
    'output_format': {
        'trigger_name?': 'str',
    },
    'description': 'Create trigger (When the trigger is executed, the associated function is called)'
}


@NeedPermission(Permission.Run.Logic.create_trigger)
def do(data, resource):
    partition = 'logic-trigger'
    body = {}
    params = data['params']

    trigger_name = params.get('trigger_name')
    trigger_type = params.get('trigger_type')
    function_name = params.get('function_name')
    description = params.get('description', None)
    option = params.get('option')
    runnable = params.get('runnable', True)

    item = dict()
    item['trigger_name'] = trigger_name
    item['trigger_type'] = trigger_type
    item['function_name'] = function_name
    item['description'] = description
    item['option'] = option
    item['runnable'] = runnable

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'trigger_name', trigger_name)
    if item_ids:
        body['error'] = error.EXISTING_TRIGGER
        return Response(body)
    else:
        resource.db_put_item(partition, item)
        body['trigger_name'] = trigger_name
        return Response(body)
