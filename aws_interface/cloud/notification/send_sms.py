
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'message': 'str',
        'phone_number': 'str',
    },
    'output_format': {
        'response': 'dict',
    },
    'description': 'Send text message via sms protocol'
}


@NeedPermission(Permission.Run.Notification.send_sms)
def do(data, resource):
    body = {}
    params = data['params']

    message = params.get('message')
    phone_number = params.get('phone_number')

    try:
        resp = resource.sms_send_message(phone_number, message)
        body['response'] = resp
    except Exception as ex:
        body['error'] = str(ex)

    return body

