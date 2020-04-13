
from cloud.permission import Permission, NeedPermission
from cloud.notification import send_slack_message

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'username': 'str?',
        'icon_url': 'str?',
        'icon_emoji': 'str?',
        'text': 'str',
        'channel': 'str?',
    },
    'output_format': {
        'error': 'dict?',
        'success': 'bool'
    },
    'description': 'Send system notification through slack webhook.'
}


@NeedPermission(Permission.Run.Notification.send_slack_message_as_system_notification)
def do(data, resource):
    params = data['params']
    user = data.get('user', None)

    username = params.get('username', None)
    icon_url = params.get('icon_url', None)
    icon_emoji = params.get('icon_emoji', None)
    text = params.get('text')
    channel = params.get('channel', None)
    return send_system_slack_message(resource, text, icon_url, icon_emoji, username, channel)


def send_system_slack_message(resource, text, icon_url=None, icon_emoji=None, username=None, channel=None):
    query = []
    resps = []
    items, _ = resource.db_query('system_notification_slack_webhook', query)
    print('items', items)
    for item in items:
        try:
            slack_webhook_name = item.get('slack_webhook_name')
            resp = send_slack_message.send_slack_message(resource, slack_webhook_name, text, username, icon_url, icon_emoji, channel)
            resps.append(resp)
        except Exception as ex:
            print(ex)
    return resps
