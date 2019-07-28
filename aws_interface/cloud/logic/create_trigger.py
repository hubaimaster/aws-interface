
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
    runnable = params.get('runnable', True)

    item = dict()
    item['trigger_name'] = trigger_name
    item['trigger_type'] = trigger_type
    item['function_name'] = function_name
    item['description'] = description
    item['runnable'] = runnable

    if trigger_type == 'webhook':
        webhook_name = 'webhook-{}'.format(trigger_name)
        redirection_uri = params.get('redirection_uri')
        redirection = resource.ag_create_redirection(webhook_name, redirection_uri)
        item['config'] = {
            'redirection': redirection
        }

    item_ids, _ = resource.db_get_item_id_and_orders(partition, 'trigger_name', trigger_name)
    if item_ids:
        body['error'] = error.EXISTING_TRIGGER
        return body
    else:
        resource.db_put_item(partition, item)
        body['trigger_name'] = trigger_name
        return body
