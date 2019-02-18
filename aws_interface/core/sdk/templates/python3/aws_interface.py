import requests
import json


class Client():
    def __init(self):
        with open('manifest.json', 'r') as fp:
            self.data = json.load(fp)

    @property
    def recipe_keys(self):
        return self.data['recipe_keys']

    def examples(self):
        print('Usage examples')
        apis = self.get_api_list()
        for api in apis:
            print('API Name: {}'.format(api['name']).center(80, '-'))

            api_info = api.get('info', {})
            sdk_dict = api_info.get('input_format')
            rest_dict = api_info
            sdk_example = 'call_api("{}", {})'.format( api['name'], json.dumps(sdk_dict, indent=4))
            rest_example = json.dumps(rest_dict, indent=4)

            print('[SDK Function Call Format]')
            print(sdk_example)
            print('[REST API Format]')
            print(rest_example)

    def get_recipe_manifest(self, recipe_key):
        if recipe_key not in self.recipe_keys:
            raise Exception('recipe_key must be in {}'.format(self.recipe_keys))
        else:
            return self.manifest[recipe_key]

    def get_api_list(self, recipe_key):
        manifest = self.get_recipe_manifest(recipe_key)
        return manifest['cloud_apis']

    def get_api_url(self, recipe_key):
        manifest = self.get_recipe_manifest(recipe_key)
        return manifest['rest_api_url']

    def call_api(self, recipe_key, api_name, data=None):
        manifest = self.get_recipe_manifest(recipe_key)
        if not data:
            data = {}
        url = self.get_api_url(recipe_key)
        data['cloud_api_name'] = api_name
        data = json.dumps(data)
        resp = _post(url, data)
        return resp.json()


def _post(url, data):
    response = requests.post(url, data)
    return response


if __name__ == '__main__':  # SHOW EXAMPLE
    Client().examples()
