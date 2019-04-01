import requests
import json


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

    def database_get_items(self, partition):
        response = self._database('get_items', {
            'partition': partition
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

    def storage_create_folder(self, parent_path, folder_name, read_groups, write_groups):
        response = self._storage('create_folder', {
            'parent_path': parent_path,
            'folder_name': folder_name,
            'read_groups': read_groups,
            'write_groups': write_groups,
        })
        return response

    def storage_delete_path(self, path):
        response = self._storage('delete_path', {
            'path': path
        })
        return response

    def storage_download_file(self, file_path):
        response = self._storage('download_file', {
            'file_path': file_path
        })
        return response

    def storage_get_folder_list(self, path, start_key=None):
        response = self._storage('get_folder_list', {
            'path': path,
            'start_key': start_key,
        })
        return response

    def storage_upload_file(self, parent_path, file_bin, file_name, read_groups, write_groups):
        response = self._storage('upload_file', {
            'parent_path': parent_path,
            'file_bin': file_bin,
            'file_name': file_name,
            'read_groups': read_groups,
            'write_groups': write_groups,
        })
        return response


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


if __name__ == '__main__':  # SHOW EXAMPLE
    example()
