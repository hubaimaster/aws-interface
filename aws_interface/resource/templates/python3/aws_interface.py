import requests
import json
import base64
import os


class Client:
    def __init__(self):
        self.session_id = None
        self.guest_id = None
        with open('manifest.json', 'r') as fp:
            self.manifest = json.load(fp)

    @property
    def _recipe_keys(self):
        return self.manifest['recipe_keys']

    def _get_recipe_manifest(self, recipe_key):
        if recipe_key not in self._recipe_keys:
            raise Exception('recipe_key must be in {}'.format(self._recipe_keys))
        else:
            return self.manifest[recipe_key]

    def _get_api_list(self, recipe_key):
        manifest = self._get_recipe_manifest(recipe_key)
        return manifest['cloud_apis']

    def _get_api_url(self, recipe_key):
        manifest = self._get_recipe_manifest(recipe_key)
        return manifest['rest_api_url']

    def _call_api(self, recipe_key, api_name, data=None):
        manifest = self._get_recipe_manifest(recipe_key)
        if not data:
            data = {}
        url = self._get_api_url(recipe_key)
        data['cloud_api_name'] = api_name
        data['recipe_key'] = recipe_key
        if self.session_id:
            data['session_id'] = self.session_id
        data = json.dumps(data)
        resp = _post(url, data)
        return resp.json().get('body', {'error': '404', 'message': 'NO RESPONSE'})

    def _auth(self, api_name, data):
        return self._call_api('auth', api_name, data)

    def _database(self, api_name, data):
        return self._call_api('database', api_name, data)

    def _storage(self, api_name, data):
        return self._call_api('storage', api_name, data)

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

    # def auth_delete_user(self):

    def database_create_item(self, item, partition, read_groups, write_groups):
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

    def database_query_items(self, partition, query, start_key=None, limit=None):
        response = self._database('query_items', {
            'partition': partition,
            'query': query,
            'start_key': start_key,
            'limit': limit,
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

    def storage_upload_file(self, file_path, read_groups=['owner', 'user'], write_groups=['owner']):
        def divide_chunks(text, n):
            for i in range(0, len(text), n):
                yield text[i:i + n]

        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file_obj:
            raw_base64 = file_obj.read()

        raw_base64 = base64.b64encode(raw_base64)
        raw_base64 = raw_base64.decode('utf-8')

        base64_chunks = divide_chunks(raw_base64, 1024 * 1024 * 6)  # 4mb
        parent_file_id = None
        for base64_chunk in base64_chunks:
            result = self._storage_upload_b64_chunk(parent_file_id, file_name, base64_chunk, read_groups, write_groups)
            parent_file_id = result.get('file_id')
        return result


def _post(url, data):
    response = requests.post(url, data)
    return response


def example():
    email = 'email@example.com'
    password = 'password'
    client = Client()

    response = client.auth_register(email, password)
    print('auth_register response: {}'.format(response))

    response = client.auth_login(email, password)
    print('auth_login response: {}'.format(response))

    response = client.database_create_item({
        'type': 'test',
    }, 'test', ['owner'], ['owner'])
    print('database_create_item response: {}'.format(response))

    response = client.storage_upload_file('manifest.json')
    print(response)

    client.storage_download_file(response['file_id'], 'download')


if __name__ == '__main__':  # SHOW EXAMPLE
    example()
