
from cloud.permission import Permission, NeedPermission
from cloud.message import error

import smtplib
import ssl

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email_provider_name': 'str',
        'title': 'str',
        'content': 'str',
        'send_to': 'str',
    },
    'output_format': {
        'success': 'bool',
    },
    'description': 'Send email via email provider name'
}


def send_email(provider_url, provider_port, provider_email, provider_password, title, content, send_to):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(provider_url, provider_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(provider_email, provider_password)
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (provider_email, send_to, title, content)
            message = message.encode('utf-8')
            server.sendmail(provider_email, send_to, message)
            server.quit()
            return True
    except Exception as ex:
        print(ex)
        return False


@NeedPermission(Permission.Run.Notification.send_email)
def do(data, resource):
    body = {}
    params = data['params']

    email_provider_name = params.get('email_provider_name')
    title = params.get('title')
    content = params.get('content')
    send_to = params.get('send_to')

    inst = [
        {'field': 'name', 'value': email_provider_name, 'option': None, 'condition': 'eq'}
    ]
    items, _ = resource.db_query('email_provider', inst)
    if items:
        item = items[0]
        url = item.get('url')
        port = item.get('port')
        email = item.get('email')
        password = item.get('password')
        success = send_email(url, port, email, password, title, content, send_to)
        body['success'] = success
        return body
    else:
        body['error'] = error.NO_SUCH_EMAIL_PROVIDER
        return body
