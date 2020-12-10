from jinja2 import Environment, PackageLoader, select_autoescape
import documentation.build as docs
import traceback
import subprocess
import boto3
import os
import json


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(BASE_DIR, 'secret')
SECRETS_BASE = os.path.join(SECRETS_DIR, 'base.json')

try:
    secrets_base = json.load(open(SECRETS_BASE, 'rt'))
except FileNotFoundError:
    subprocess.call('python generate_secrets.py')
    secrets_base = json.load(open(SECRETS_BASE, 'rt'))
    """
    raise ImproperlyConfigured('Could not find secret file {}'.format(SECRETS_BASE))
    """


env = Environment(
  loader=PackageLoader('source', 'templates'),
  autoescape=select_autoescape(['html', 'xml', 'md'])
)

index_template = env.get_template('index.html.md')
errors_template = env.get_template('_errors.md')


def generate_api_info():
    import importlib
    from cloud.lambda_function import CALLABLE_MODULE_WHITE_LIST
    context = {}
    services = []
    target_services = ['auth', 'database', 'storage', 'log', 'logic', 'schedule', 'notification']
    for target_service in target_services:
        cloud_service_name = 'cloud.{}'.format(target_service)
        module = importlib.import_module(cloud_service_name)
        service_info = module.info
        functions = []
        for function in sorted(CALLABLE_MODULE_WHITE_LIST):
            if function.startswith('{}.'.format(cloud_service_name)):
                try:
                    function_module = importlib.import_module(function)
                    function_info = function_module.info
                    function_info['name'] = function
                    if 'session_id' not in function_info['input_format']:
                        function_info['input_format']['session_id?'] = 'str'
                    function_info['output_format']['error?'] = {
                      'code': 'int',
                      'message': 'str',
                    }
                    functions.append(function_info)
                except Exception as ex:
                    print(ex)
                    print(traceback.format_exc())
        service_info['functions'] = functions
        services.append(service_info)
    context['services'] = services
    return context


def generate_error_info():
    context = {}
    import cloud.message.error as error
    error_vars = [item for item in dir(error) if not item.startswith("__")]
    errors = [getattr(error, error_var) for error_var in error_vars]
    errors = sorted(errors, key=lambda x: x['code'])
    context['errors'] = errors
    return context


def write_api_info():
    index_result = index_template.render(generate_api_info())
    with open('source/index.html.md', 'w+') as fp:
        fp.write(index_result)

    errors_result = errors_template.render(generate_error_info())
    with open('source/includes/_errors.md', 'w+') as fp:
        fp.write(errors_result)

    # bundle exec middleman server
    subprocess.call(['bundle exec middleman build'], shell=True)


def upload_directory(path, bucketname):
    AWS_ACCESS_KEY_ID = secrets_base['AWS_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY = secrets_base['AWS_SECRET_KEY']
    s3_client = boto3.client("s3", region_name="ap-northeast-2",
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             )
    paths = []
    for root, dirs, files in os.walk(path):

        directory_name = root.replace(path, "")
        if directory_name.startswith('/'):
            directory_name = directory_name[1:]
        for file in files:
            upload_file = os.path.join(directory_name, file)
            print(upload_file)
            extra_args = {
                'ACL': 'public-read',
                'CacheControl': "max-age=0,no-cache,no-store,must-revalidate"
            }
            if str(file).endswith('.html'):
                extra_args['ContentType'] = 'text/html'
            if str(file).endswith('.css'):
                extra_args['ContentType'] = 'text/css'
            s3_client.upload_file(os.path.join(root, file), bucketname, upload_file,
                                  ExtraArgs=extra_args)
            paths.append('/%s/%s' % (directory_name, file))
    paths = list(map(lambda x: x.replace('//', '/'), paths))
    return paths


def invalidate_cache(dist_id, paths):
    import time
    AWS_ACCESS_KEY_ID = secrets_base['AWS_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY = secrets_base['AWS_SECRET_KEY']
    client = boto3.client("cloudfront", region_name="ap-northeast-2",
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             )
    response = client.create_invalidation(
    DistributionId=dist_id,
    InvalidationBatch={
        'Paths': {
            'Quantity': len(paths),
            'Items': paths
        },
        'CallerReference': '{}'.format(time.time())
    })
    return response


def deploy():
    write_api_info()
    path = os.path.dirname(os.path.abspath(docs.__file__))
    bucketname = 'docs.aws-interface.com'
    paths = upload_directory(path, bucketname)
    print(paths)
    invalidate_cache('E17MKTBI8D65H', paths)


if __name__ == '__main__':
    deploy()
