import requests
import json
import base64
import os


class Client:
    def __init__(self, url=None):
        self.url = '{{REST_API_URL}}'
        if url:
            self.url = url
        self.session_id = None
        self.guest_id = None

    @classmethod
    def _post(cls, url, data):
        response = requests.post(url, data)
        return response

    def _call_api(self, service_type, function_name, data=None):
        if not data:
            data = {}
        data['module_name'] = 'cloud.{}.{}'.format(service_type, function_name)
        if self.session_id:
            data['session_id'] = self.session_id
        data = json.dumps(data)
        resp = self._post(self.url, data)
        return resp.json().get('body', {'error': '404', 'message': 'NO RESPONSE'})

    def _auth(self, api_name, data):
        self.log_create_log('auth', api_name, None)
        return self._call_api('auth', api_name, data)

    def _database(self, api_name, data):
        self.log_create_log('database', api_name, None)
        return self._call_api('database', api_name, data)

    def _storage(self, api_name, data):
        self.log_create_log('storage', api_name, None)
        return self._call_api('storage', api_name, data)

    def _logic(self, api_name, data):
        return self._call_api('logic', api_name, data)

    def _log(self, api_name, data):
        return self._call_api('log', api_name, data)

    def auth_register(self, email, password, extra={}):
        response = self._auth('register', {
            'email': email,
            'password': password,
            'extra': extra
        })
        return response

    def auth_login(self, email, password):
        response = self._auth('login', {
            'email': email,
            'password': password
        })
        self.session_id = response.get('session_id', None)
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

    def auth_guest(self, guest_id=None):
        data = {}
        if guest_id:
            data['guest_id'] = guest_id
        response = self._auth('guest', data)
        self.session_id = response.get('session_id', None)
        return response

    def database_create_item(self, partition, item, read_groups, write_groups):
        response = self._database('create_item', {
            'item': item,
            'partition': partition,
            'read_groups': read_groups,
            'write_groups': write_groups,
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

    def database_update_item(self, item_id, item, read_groups, write_groups):
        response = self._database('update_item', {
            'item_id': item_id,
            'item': item,
            'read_groups': read_groups,
            'write_groups': write_groups,
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

    def _storage_upload_b64_chunk(self, parent_file_id, file_name, file_b64, read_groups, write_groups):
        response = self._storage('upload_b64', {
            'parent_file_id': parent_file_id,
            'file_name': file_name,
            'file_b64': file_b64,
            'read_groups': read_groups,
            'write_groups': write_groups,
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

    def storage_upload_file(self, file_path, read_groups, write_groups):
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
            result = self._storage_upload_b64_chunk(parent_file_id, file_name, base64_chunk, read_groups, write_groups)
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


def examples():
    email = 'email@example.com'
    password = 'password'
    client = Client()

    response = client.auth_register(email, password)
    print('auth_register response: {}'.format(response))

    response = client.auth_login(email, password)
    print('auth_login response: {}'.format(response))

    response = client.database_create_item({
        'type': 'test',
    }, 'test', read_groups=['owner'], write_groups=['owner'])
    print('database_create_item response: {}'.format(response))

    response = client.storage_upload_file('aws_interface.py', read_groups=['owner'], write_groups=['owner'])
    print(response)

    client.storage_download_file(response['file_id'], 'download')


