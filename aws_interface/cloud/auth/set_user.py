from cloud.response import Response

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'session_id': 'str',
        'user_id': 'str?',
        'field': 'str',
        'value': 'str?',
    },
    'output_format': {
        'success': 'bool',
        'message': 'str?',
    },
}


def do(data, resource):
    body = {}
    params = data['params']
    user = data['user']

    user_id = params.get('user_id', None)
    field = params.get('field')
    value = params.get('value', None)

    if 'admin' not in user['groups'] and user_id != user['id']:  # If requester id do not match user_id in params
        body['success'] = False
        body['message'] = 'permission denied'
        return Response(body)
    else:
        if user_id is None:
            user_id = user['id']

    user = resource.db_get_item(user_id)

    # For security
    if field in ['id', 'email', 'passwordHash', 'salt', 'groups', 'loginMethod']:
        body['success'] = False
        body['message'] = 'field [{}] cannot be modified'.format(field)
        return Response(body)
    else:
        user[field] = value
        resource.db_update_item(user_id, user)

        body['success'] = True
        body['user_id'] = user_id
        return Response(body)
