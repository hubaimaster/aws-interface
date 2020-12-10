
from cloud.permission import Permission, NeedPermission


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'email': 'str'
    },
    'output_format': {
        'has_account': 'bool'
    },
    'description': 'Check account exist'
}


@NeedPermission(Permission.Run.Auth.has_account)
def do(data, resource):
    body = {}
    params = data['params']
    email = params.get('email', None)

    items, end_key = resource.db_query('user', [{'option': None, 'field': 'email', 'value': email, 'condition': 'eq'}])
    if items:
        item = items[0]
        login_method = item.get('login_method', None)
        body['has_account'] = True
        body['login_method'] = login_method
    else:
        body['has_account'] = False
    return body
