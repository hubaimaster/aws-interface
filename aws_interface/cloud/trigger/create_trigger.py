
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'trigger_name': 'str',
        'module_name': 'str',
        'function_name': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Create trigger [System will call function when <module_name> invoked.]'
}


@NeedPermission(Permission.Run.Trigger.create_trigger)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    trigger_name = params.get('trigger_name')
    module_name = params.get('module_name')
    function_name = params.get('function_name')

    trigger = {
        'trigger_name': trigger_name,
        'module_name': module_name,
        'function_name': function_name,
    }

    success = resource.db_put_item('trigger', trigger, trigger_name)
    body['success'] = success
    return body
