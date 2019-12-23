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
