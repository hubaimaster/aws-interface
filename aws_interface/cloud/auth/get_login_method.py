
from cloud.permission import Permission, NeedPermission
from cloud.message import error
from cloud.auth._constant import LOGIN_METHODS
import inspect
from cloud.env import safe_to_run_code


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'login_method': 'str',
    },
    'output_format': {
        'item': {
            'enabled': 'bool',
            'default_group_name': 'str',
            'register_policy_code': 'str',
        },
    },
    'description': 'Return login method status'
}


def match_policy(policy_code, extra, password_meta):
    # If admin user can invoke custom code via exec and eval, It can cause serious security issues.
    # This is because the admin user can run code on the dashboard server.
    if not safe_to_run_code():
        return True
    exec(policy_code)
    result = eval('can_register(extra, password_meta)')
    return result


def get_default_policy_code(mode):
    """ Assign default item that has default policy code
    """
    if mode == 'email_login':
        import cloud.auth.policy.register_email as source
        policy_code = inspect.getsource(source)
    elif mode == 'guest_login':
        import cloud.auth.policy.register_guest as source
        policy_code = inspect.getsource(source)
    elif mode == 'facebook_login':
        import cloud.auth.policy.register_facebook as source
        policy_code = inspect.getsource(source)
    elif mode == 'google_login':
        import cloud.auth.policy.register_google as source
        policy_code = inspect.getsource(source)
    elif mode == 'naver_login':
        import cloud.auth.policy.register_naver as source
        policy_code = inspect.getsource(source)
    elif mode == 'kakao_login':
        import cloud.auth.policy.register_kakao as source
        policy_code = inspect.getsource(source)
    else:
        raise BaseException('No such policy code mode: [{}]'.format(mode))
    return policy_code


@NeedPermission(Permission.Run.Auth.get_login_method)
def do(data, resource):
    body = {}
    params = data['params']
    login_method = params.get('login_method')  # email_login, guest_login, facebook_login
    if login_method not in LOGIN_METHODS:
        body['error'] = error.NO_SUCH_LOGIN_METHOD
        return body

    item = resource.db_get_item('auth-login-method-{}'.format(login_method))
    default_policy_code = get_default_policy_code(login_method)

    if not item:
        item = {
            'enabled': True,
            'default_group_name': 'user',
            'register_policy_code': default_policy_code,
        }
        resource.db_put_item('meta-info', item, login_method)
    if item.get('register_policy_code', None) is None:
        item['register_policy_code'] = default_policy_code

    body['item'] = item
    return body
