
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
from cloud.auth._constant import LOGIN_METHODS
from cloud.message import error

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'login_method': 'str',

        'enabled': 'bool',
        'default_group_name': 'str',
        'register_policy_code?': 'str',
    },
    'output_format': {

    },
    'description': 'Set information of login method'
}


@NeedPermission(Permission.Run.Auth.set_login_method)
def do(data, resource):
    body = {}
    params = data['params']
    login_method = params.get('login_method')
    enabled = params['enabled']
    default_group_name = params['default_group_name']
    register_policy_code = params.get('register_policy_code', None)

    if login_method not in LOGIN_METHODS:
        body['error'] = error.NO_SUCH_LOGIN_METHOD
        return Response(body)

    if enabled == 'true':
        enabled = True
    elif enabled == 'false':
        enabled = False

    item = {
        'enabled': enabled,
        'default_group_name': default_group_name,
        'register_policy_code': register_policy_code,
    }
    item_id = 'auth-login-method-{}'.format(login_method)
    if not resource.db_put_item('meta-info', item, item_id):
        resource.db_update_item(item_id, item)

    return Response(body)
