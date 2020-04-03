
from cloud.permission import Permission, NeedPermission
from concurrent.futures import ThreadPoolExecutor
import cloud.libs.emails as emails

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email_from': 'str',
        'name_from': 'str',
        'email_to': 'list',

        'title': 'str',
        'content': 'str',

        'host': 'str',
        'port': 'int',
        'user': 'str',
        'password': 'str',

        'timeout': 'int'
    },
    'output_format': {
        'result': {
            'email_to[0]': 'bool',
            'email_to[1]': 'bool',
            '...': 'bool',
        },
    },
    'description': 'Send email directly'
}


def send_email(email_from, email_to, title, content, host, port, user, password, timeout):
    message = emails.html(
        html=content,
        subject=title,
        mail_from=email_from,
    )

    resp = message.send(
        to=email_to,
        smtp={
            "host": host,
            "port": port,
            "timeout": timeout,
            "user": user,
            "password": password,
            "tls": True,
        },
    )
    return resp


@NeedPermission(Permission.Run.Notification.send_email2)
def do(data, resource):
    body = {}
    params = data['params']

    email_from = params.get('email_from')
    name_from = params.get('name_from')
    email_to_list = params.get('email_to')

    title = params.get('title')
    content = params.get('content')

    host = params.get('host')
    port = params.get('port')
    user = params.get('user')
    password = params.get('password')

    timeout = params.get('timeout', 10)

    port = int(port)
    timeout = int(timeout)
    if isinstance(email_to_list, str):
        email_to_list = [email_to_list]

    with ThreadPoolExecutor(max_workers=32) as exc:
        for _email_to in email_to_list:
            def work(email_to):
                resp = send_email((name_from, email_from), email_to, title, content, host, port, user, password, timeout)
                if resp.status_code == 250:
                    body['result'][email_to] = True
                else:
                    body['result'][email_to] = False
            exc.submit(work, _email_to)
    return body
