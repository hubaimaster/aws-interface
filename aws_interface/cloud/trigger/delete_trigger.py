
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'trigger_id': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Create trigger [System will call function when <module_name> invoked.]'
}


@NeedPermission(Permission.Run.Trigger.delete_trigger)
def do(data, resource):
    body = {}
    params = data['params']
    user = data.get('user', None)

    trigger_id = params.get('trigger_id')
    success = resource.db_delete_item(trigger_id)
    body['success'] = success
    return body
