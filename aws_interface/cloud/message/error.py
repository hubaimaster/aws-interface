"""
Error code and message definitions
"""
PERMISSION_DENIED = {
    'code': 1,
    'message': 'Permission denied'
}
GUEST_LOGIN_INVALID = {
    'code': 2,
    'message': 'Guest login has been deactivated'
}
NO_SUCH_GUEST = {
    'code': 3,
    'message': 'No such guest'
}
EMAIL_LOGIN_INVALID = {
    'code': 4,
    'message': 'Email login has been deactivated'
}
WRONG_PASSWORD = {
    'code': 5,
    'message': 'Password did not match'
}
NO_SUCH_ACCOUNT = {
    'code': 6,
    'message': 'No such account'
}
LOGOUT_FAILED = {
    'code': 7,
    'message': 'Logout failed'
}
PUT_USER_GROUP_FAILED = {
    'code': 8,
    'message': 'Insert user group failed'
}
EXISTING_ACCOUNT = {
    'code': 9,
    'message': 'Existing account'
}
FORBIDDEN_MODIFICATION = {
    'code': 10,
    'message': 'Forbidden modifications'
}
NO_SUCH_PARTITION = {
    'code': 11,
    'message': 'No such partition'
}
NUM_OF_BATCH_ITEMS_MUST_BE_LESS_THAN_128 = {
    'code': 12,
    'message': 'Number of item_ids must be less than 128'
}
LOG_CREATION_FAILED = {
    'code': 13,
    'message': 'Log creation failed'
}
INVALID_SESSION = {
    'code': 14,
    'message': 'Invalid session'
}
INVALID_FILE_KEY = {
    'code': 15,
    'message': 'Invalid file key'
}
INVALID_REQUEST = {
    'code': 16,
    'message': 'Invalid request, please check parameters'
}
FORBIDDEN_REQUEST = {
    'code': 17,
    'message': 'Forbidden request'
}
NO_SUCH_FUNCTION = {
    'code': 18,
    'message': 'No such function'
}
DEFAULT_USER_GROUP_CANNOT_BE_MODIFIED = {
    'code': 19,
    'message': 'Default user groups can not be modified'
}
EXISTING_FUNCTION = {
    'code': 20,
    'message': 'Function name already exists'
}
FUNCTION_ERROR = {
    'code': 21,
    'message': 'Function has errors: {}'
}
NO_SUCH_FUNCTION_TEST = {
    'code': 22,
    'message': 'No such function test'
}
NO_SUCH_POLICY_MODE = {
    'code': 23,
    'message': 'No such policy mode'
}
NO_SUCH_ITEM = {
    'code': 24,
    'message': 'No such item'
}
UNSUPPORTED_FILE_TYPE = {
    'code': 25,
    'message': 'Unsupported file type'
}