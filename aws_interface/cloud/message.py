

class Error:
    permission_denied = {'code': 1, 'message': 'Permission denied'}
    guest_login_invalid = {'code': 2, 'message': 'Guest login has been deactivated'}
    no_such_guest = {'code': 3, 'message': 'No such guest'}
    email_login_invalid = {'code': 4, 'message': 'Email login has been deactivated'}
    wrong_password = {'code': 5, 'message': 'Password did not match'}
    no_such_account = {'code': 6, 'message': 'No such account'}
    logout_failed = {'code': 7, 'message': 'Logout failed'}
    put_user_group_failed = {'code': 8, 'message': 'Insert user group failed'}
    existing_account = {'code': 9, 'message': 'Existing account'}
    forbidden_modification = {'code': 10, 'message': 'Forbidden modifications'}
    no_such_partition = {'code': 11, 'message': 'No such partition'}
    number_of_batch_items_must_be_less_than_128 = {'code': 12, 'message': 'Number of item_ids must be less than 128'}
    log_creation_failed = {'code': 13, 'message': 'Log creation failed'}
    invalid_session = {'code': 14, 'message': 'Invalid session'}
    invalid_file_key = {'code': 15, 'message': 'Invalid file key'}
    invalid_request = {'code': 16, 'message': 'Invalid request, please check parameters'}
    forbidden_request = {'code': 17, 'message': 'Forbidden request'}
    no_such_function = {'code': 18, 'message': 'No such function'}
    default_user_group_cannot_be_modified = {'code': 19, 'message': 'Default user groups can not be modified'}
    existing_function = {'code': 20, 'message': 'Function name already exists'}
    function_error = {'code': 21, 'message': 'Function has errors: \n{}'}
    no_such_function_test = {'code': 22, 'message': 'No such function test'}
