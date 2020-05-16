from .base import API
from .utils import lambda_method, make_data


class NotificationAPI(API):
    @lambda_method
    def create_email_provider(self, name, description, url, port, email, password):
        import cloud.notification.create_email_provider as method
        params = {
            'name': name,
            'description': description,
            'url': url,
            'port': port,
            'email': email,
            'password': password,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_email_provider(self, name):
        import cloud.notification.delete_email_provider as method
        params = {
            'name': name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_email_provider(self, name):
        import cloud.notification.get_email_provider as method
        params = {
            'name': name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_email_providers(self, start_key=None):
        import cloud.notification.get_email_providers as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def send_email(self, email_provider_name, title, content, send_to):
        import cloud.notification.send_email as method
        params = {
            'email_provider_name': email_provider_name,
            'title': title,
            'content': content,
            'send_to': send_to,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def update_email_provider(self, name, description=None, url=None, port=None, email=None, password=None):
        import cloud.notification.update_email_provider as method
        params = {
            'name': name,
            'description': description,
            'url': url,
            'port': port,
            'email': email,
            'password': password,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def send_sms(self, message, phone_number):
        import cloud.notification.send_sms as method
        params = {
            'message': message,
            'phone_number': phone_number
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_slack_webhook(self, name, url):
        import cloud.notification.create_slack_webhook as method
        params = {
            'name': name,
            'url': url,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_slack_webhook(self, name):
        import cloud.notification.delete_slack_webhook as method
        params = {
            'name': name
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_slack_webhooks(self, start_key):
        import cloud.notification.get_slack_webhooks as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def send_slack_message(self, slack_webhook_name, text, username=None, icon_url=None, icon_emoji=None, channel=None):
        import cloud.notification.send_slack_message as method
        params = {
            'slack_webhook_name': slack_webhook_name,
            'text': text,
            'username': username,
            'icon_url': icon_url,
            'icon_emoji': icon_emoji,
            'channel': channel,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def create_system_notification(self, slack_webhook_name):
        import cloud.notification.create_system_notification as method
        params = {
            'slack_webhook_name': slack_webhook_name,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def delete_system_notification(self, system_notification_id):
        import cloud.notification.delete_system_notification as method
        params = {
            'system_notification_id': system_notification_id
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)

    @lambda_method
    def get_system_notifications(self, start_key):
        import cloud.notification.get_system_notifications as method
        params = {
            'start_key': start_key,
        }
        data = make_data(self.app_id, params)
        return method.do(data, self.resource)
