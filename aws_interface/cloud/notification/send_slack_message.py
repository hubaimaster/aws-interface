
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from requests import post
import json


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'slack_webhook_name': 'str',
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
    'description': 'Create slack webhook.'
}


@NeedPermission(Permission.Run.Notification.send_slack_message)
def do(data, resource):
    params = data['params']
    user = data.get('user', None)

    slack_webhook_name = params.get('slack_webhook_name')
    username = params.get('username', None)
    icon_url = params.get('icon_url', None)
    icon_emoji = params.get('icon_emoji', None)
    text = params.get('text')
    channel = params.get('channel', None)
    return send_slack_message(resource, slack_webhook_name, text, username, icon_url, icon_emoji, channel)


def send_slack_message(resource, slack_webhook_name, text, username, icon_url, icon_emoji, channel):
    body = {}
    query = [{
        'condition': 'eq',
        'field': 'name',
        'value': slack_webhook_name,
        'option': None
    }]
    items, _ = resource.db_query('slack_webhook', query)
    if items:
        item = items[0]
        webhook_url = item.get('url')
        data = {
            'text': text
        }
        if username:
            data['username'] = username
        if icon_url:
            data['icon_url'] = icon_url
        if icon_emoji:
            data['icon_emoji'] = icon_emoji
        if channel:
            data['channel'] = channel
        data = json.dumps(data)
        result = post(webhook_url, data)
        body['result'] = result
    else:
        body['error'] = error.NO_SUCH_SLACK_WEBHOOK
        body['success'] = False

    return body
