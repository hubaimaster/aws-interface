
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from uuid import uuid4

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'system_notification_id': 'str',
    },
    'output_format': {
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Delete slack webhook for system notification. (Such as error notice..)'
}


@NeedPermission(Permission.Run.Notification.delete_system_notification)
def do(data, resource):
    body = {}
    params = data['params']

    system_notification_id = params.get('system_notification_id')

    success = resource.db_delete_item(system_notification_id)
    body['success'] = success

    return body
