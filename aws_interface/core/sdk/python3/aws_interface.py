import requests
import json


def examples():  # Just call it. It will help you !
    print('Those are examples of aws_interface usage')
    apis = get_api_list()
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
