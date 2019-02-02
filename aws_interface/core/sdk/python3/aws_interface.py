import requests
import json


def show_api_list():  # Just call it. It will help you !
    print('Those are examples of aws_interface usage')
    apis = get_api_list()
    for api in apis:
        print('------>API name:{}', api['name'])
        print('ex:>>> call_api("{}", {})'.format(api['name'], {'email': 'str', 'password': 'str'}))


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


def call_api(api_name, data):
    url = get_api_url()
    data['cloud_api_name'] = api_name
    data = json.dumps(data)
    resp = post(url, data)
    return resp.json()


if __name__ == '__main__':  # EXAMPLE
    resp = call_api("login", {'email': 'str', 'password': 'str'})
    print(resp)