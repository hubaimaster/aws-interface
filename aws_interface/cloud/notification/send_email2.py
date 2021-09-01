
from cloud.permission import Permission, NeedPermission
from concurrent.futures import ThreadPoolExecutor
import cloud.libs.emails as emails
import time


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email_from': 'str',
        'name_from': 'str',
        'email_to_list': 'list',

        'title': 'str',
        'content': 'str',

        'host': 'str',
        'port': 'int',
        'user': 'str',
        'password': 'str',
        'max_sending_amount_per_second': 'int=14',
    },
    'output_format': {
        'result': {
            'email_to[0]': 'bool',
            'email_to[1]': 'bool',
            '...': 'bool',
        },
    },
    'description': 'Send email directly, Max len of email_to must be less equal than 100'
}


TIMEOUT = 3


def _send_email(email_from, email_to, title, content, host, port, user, password, timeout):
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


def _send_emails(email_from, name_from, email_to_list, title, content, host, port, user, password,
                 max_sending_amount_per_second, timeout):
    result = []
    port = int(port)
    timeout = int(timeout)
    if isinstance(email_to_list, str):
        email_to_list = [email_to_list]

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=50) as exc:
        def work(email_to):
            resp = _send_email((name_from, email_from), email_to, title, content, host, port, user, password, timeout)
            if resp.status_code == 250:
                result.append({'email': email_to, 'success': True})
            else:
                result.append({'email': email_to, 'success': False})
        for idx, _email_to in enumerate(email_to_list):
            if idx % (max_sending_amount_per_second - 1) == 0:
                offset = time.time() - start_time
                time.sleep(1 - offset)
                start_time = time.time()
            exc.submit(work, _email_to)
    return result


def send_emails_safe(email_from, name_from, email_to_list, title, content, host, port, user, password,
                     max_sending_amount_per_second, timeout, retry_count=0):
    results = _send_emails(email_from, name_from, email_to_list, title, content, host, port, user, password,
                           max_sending_amount_per_second, timeout)
    email_to_list = [result['email'] for result in results if not result['success']]
    if len(email_to_list) == 0:
        return results
    else:
        if retry_count < 5:
            time.sleep(1)
            return send_emails_safe(email_from, name_from, email_to_list, title, content, host, port, user, password,
                                    max_sending_amount_per_second, timeout, retry_count + 1)
        else:
            return results


@NeedPermission(Permission.Run.Notification.send_email2)
def do(data, resource):
    body = {}
    params = data['params']

    email_from = params.get('email_from')
    name_from = params.get('name_from')
    email_to_list = params.get('email_to_list')
    title = params.get('title')
    content = params.get('content')
    host = params.get('host')
    port = params.get('port')
    user = params.get('user')
    password = params.get('password')
    max_sending_amount_per_second = int(params.get('max_sending_amount_per_second', 14))
    timeout = TIMEOUT

    results = send_emails_safe(email_from, name_from, email_to_list, title, content, host, port, user, password,
                               max_sending_amount_per_second, timeout)
    body['results'] = results
    return body
