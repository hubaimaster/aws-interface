import requests
import json


def examples():  # Just call it. It will help you !
    print('Those are examples of aws_interface usage')
    apis = get_api_list()
    for api in apis:
        print('------> API name: {}'.format(api['name']))
        print('------> call_api("{}", {})'.format(api['name'], api.get('info', {}).get('input_format')))
        print('REST API Format: {}'.format(api.get('info', {})))
        print('')


def get_api_list():
    with open('info.json', 'r') as fp:
        json_data = json.load(fp)
        apis = json_data['cloud_apis']
        return apis


def get_api_url():
    with open('info.json', 'r') as fp:
        json_data = json.load(fp)
        url = json_data['rest_api_url']
        return url


def post(url, data):
    response = requests.post(url, data)
    return response


def call_api(api_name, data=None):
    if not data:
        data = {}
    url = get_api_url()
    data['cloud_api_name'] = api_name
    data = json.dumps(data)
    resp = post(url, data)
    return resp.json()


if __name__ == '__main__':  # SHOW EXAMPLE
    examples()