import requests
import json
import base64
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'aws_interface_config.json')
SESSION_FILE = os.path.join(BASE_DIR, 'aws_interface_session.json')


class Client(object):
    def __init__(self, config_path=CONFIG_PATH):
        config = self.get_config(config_path)
        self.session_id = config.get('session_id', None)
        self.url = config.get('rest_api_url', None)
        self.load_session()

    @classmethod
    def get_config(cls, config_path):
        if os.path.exists(config_path):
            with open(config_path, 'r') as fp:
                config_json = json.load(fp)
                return config_json
        else:
            return {}

    def save_session(self, filename=SESSION_FILE):
        try:
            if self.session_id:
                with open(filename, 'w+') as fp:
                    fp.write(self.session_id)
        except Exception as ex:
            pass

    def load_session(self, filename=SESSION_FILE):
        try:
            with open(filename, 'r') as fp:
                if not self.session_id:
                    session_id = fp.read()
                    self.session_id = session_id
        except Exception as ex:
            pass

    @classmethod
    def _post(cls, url, data):
        response = requests.post(url, data)
        return response

    def call_api(self, module_name, data=None):
        if not data:
            data = {}
        data['module_name'] = module_name
        if self.session_id:
            data['session_id'] = self.session_id
        data = json.dumps(data)
        resp = self._post(self.url, data)
        return resp.json()

    def _auth(self, api_name, data):
        return self.call_api('cloud.auth.{}'.format(api_name), data)

    def _database(self, api_name, data):
        return self.call_api('cloud.database.{}'.format(api_name), data)

    def _storage(self, api_name, data):
        return self.call_api('cloud.storage.{}'.format(api_name), data)

    def _logic(self, api_name, data):
        return self.call_api('cloud.logic.{}'.format(api_name), data)

    def _log(self, api_name, data):
        return self.call_api('cloud.log.{}'.format(api_name), data)

    def auth_register(self, email, password, extra={}):
        response = self._auth('register', {
            'email': email,
            'password': password,
            'extra': extra
        })
        return response

    def auth_login(self, email, password, save_session=True):
        response = self._auth('login', {
            'email': email,
            'password': password
        })
        self.session_id = response.get('session_id', None)
        if save_session:
            self.save_session()
        return response

    def auth_login_facebook(self, access_token, save_session=True):
        response = self._auth('login_facebook', {
            'access_token': access_token,
        })
        self.session_id = response.get('session_id', None)
        if save_session:
            self.save_session()
        return response

    def auth_get_user(self, user_id):
        response = self._auth('get_user', {
            'user_id': user_id
        })
        return response

    def auth_get_me(self):
        response = self._auth('get_me', {
        })
        return response

    def auth_get_users(self, start_key=None):
        response = self._auth('get_users', {
            'start_key': start_key,
        })
        return response

    def auth_logout(self):
        response = self._auth('logout', {
            'session_id': self.session_id
        })
        self.session_id = None
        return response

    def auth_guest(self, guest_id=None, save_session=True):
        data = {}
        if guest_id:
            data['guest_id'] = guest_id
        response = self._auth('guest', data)
        self.session_id = response.get('session_id', None)
        if save_session:
            self.save_session()
        return response

    def database_create_item(self, partition, item):
        response = self._database('create_item', {
            'item': item,
            'partition': partition,
        })
        return response

    def database_delete_item(self, item_id):
        response = self._database('delete_item', {
            'item_id': item_id
        })
        return response

    def database_get_item(self, item_id):
        response = self._database('get_item', {
            'item_id': item_id
        })
        return response

    def database_get_item_count(self, partition, field=None, value=None):
        response = self._database('get_item_count', {
            'partition': partition,
            'field': field,
            'value': value,
        })
        return response

    def database_get_items(self, partition, start_key=None, limit=None):
        response = self._database('get_items', {
            'partition': partition,
            'start_key': start_key,
            'limit': limit,
        })
        return response

    def database_put_item_field(self, item_id, field_name, field_value):
        response = self._database('put_item_field', {
            'item_id': item_id,
            'field_name': field_name,
            'field_value': field_value,
        })
        return response

    def database_update_item(self, item_id, item):
        response = self._database('update_item', {
            'item_id': item_id,
            'item': item,
        })
        return response

    def database_query_items(self, partition, query, start_key=None, limit=100, reverse=False):
        response = self._database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
            'reverse': reverse,
        })
        return response

    def _storage_delete_b64(self, file_id):
        response = self._storage('delete_b64', {
            'file_id': file_id
        })
        return response

    def _storage_download_b64_chunk(self, file_id):
        response = self._storage('download_b64', {
            'file_id': file_id
        })
        return response

    def _storage_upload_b64_chunk(self, parent_file_id, file_name, file_b64):
        response = self._storage('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
        })
        return response

    def storage_delete_file(self, file_id):
        self._storage_delete_b64(file_id)

    def storage_download_file(self, file_id, download_path):
        """
        :param file_id: file_id that is uploaded on aws via storage_upload_file
        :param download_path: str
        :return:
        """
        string_file_b64 = None
        file_name = 'file'
        while file_id:
            result = self._storage_download_b64_chunk(file_id)
            file_id = result.get('parent_file_id', None)
            file_name = result.get('file_name', file_name)
            if string_file_b64:
                string_file_b64 = result.get('file_b64') + string_file_b64
            else:
                string_file_b64 = result.get('file_b64')

        string_b64 = string_file_b64.encode('utf-8')
        file_bin = base64.b64decode(string_b64)

        with open(download_path, 'wb+') as file_obj:
            file_obj.seek(0)
            file_obj.write(file_bin)

    def storage_upload_file(self, file_path):
        def div_chunks(file_path_to_chunk, n):
            with open(file_path_to_chunk, 'rb') as file_obj:
                while True:
                    raw_bytes = file_obj.read(n)
                    if raw_bytes:
                        b64_chunk = base64.b64encode(raw_bytes)
                        b64_chunk = b64_chunk.decode('utf-8')
                        yield b64_chunk
                    else:
                        break
        file_name = os.path.basename(file_path)
        base64_chunks = div_chunks(file_path, 1024 * 1024 * 3)
        parent_file_id = None
        for base64_chunk in base64_chunks:
            result = self._storage_upload_b64_chunk(parent_file_id, file_name, base64_chunk)
            parent_file_id = result.get('file_id')
        return result

    def logic_run_function(self, function_name, payload):
        response = self._logic('run_function', {
            'function_name': function_name,
            'payload': payload,
        })
        return response

    def log_create_log(self, event_source, event_name, event_param):
        response = self._log('create_log', {
            'event_source': event_source,
            'event_name': event_name,
            'event_param': event_param,
        })
        return response


class Condition(object):
    equal = 'eq'
    include = 'in'
    greater_than = 'gt'
    greater_than_or_equal = 'ge'
    less_than = 'ls'
    less_than_or_equal = 'le'


class Query(list):
    """Generate query list
    """
    def __init__(self, condition=None, field=None, value=None):
        super(Query, self).__init__()
        if condition and field:
            self._add(None, condition, field, value)

    def _add(self, logical_operator, condition, field, value):
        if len(self) == 0:
            logical_operator = None
        self.append({'option': logical_operator,  'condition': condition, 'field': field, 'value': value})
        return self

    def add_or(self, condition, field, value):
        """
        :param field: Field name to operate
        :param value: Field value to operate
        :param condition:
        :return:
        """
        return self._add('or', condition, field, value)

    def add_and(self, condition, field, value):
        """
        :param field: Field name to operate
        :param value: Field value to operate
        :param condition:
        :return:
        """
        return self._add('and', condition, field, value)


def examples():
    email = 'email@example.com'
    password = 'password'
    client = Client()

    response = client.auth_register(email, password)
    print('authRegister response: {}'.format(response))

    response = client.auth_login(email, password)
    print('auth_login response: {}'.format(response))

    response = client.database_create_item('test', {'type': 'test'})
    print('database_create_item response: {}'.format(response))
    item_id = response['item_id']

    response = client.database_update_item(item_id, {
        'man': 'ok',
    })
    print(response)

    response = client.database_get_item(item_id)
    print(response)

    response = client.storage_upload_file('aws_interface.py')
    print(response)

    client.storage_download_file(response['file_id'], 'download')

    query = Query(Condition.equal, 'man', 'ok')\
        .add_or(Condition.include, 'man', 'o')\
        .add_and(Condition.include, 'type', 'test')

    response = client.database_query_items('test', query)
    for item in response['items']:
        print(item)


if __name__ == '__main__':
    examples()
