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
NO_SUCH_FILE = {
    'code': 26,
    'message': 'No such file'
}
ADMIN_GROUP_CANNOT_BE_MODIFIED = {
    'code': 27,
    'message': 'An admin group can not be modified'
}
NO_SUCH_LOGIN_METHOD = {
    'code': 28,
    'message': 'No such login method',
}
REGISTER_POLICY_VIOLATION = {
    'code': 29,
    'message': 'Register policy violation',
}
EXISTING_TRIGGER = {
    'code': 30,
    'message': 'Existing trigger'
}
EXISTING_WEBHOOK = {
    'code': 31,
    'message': 'Existing webhook'
}
NO_SUCH_WEBHOOK = {
    'code': 32,
    'message': 'No such webhook'
}
EXISTING_SCHEDULE = {
    'code': 33,
    'message': 'Existing schedule'
}
NO_SUCH_SCHEDULE = {
    'code': 34,
    'message': 'No such schedule'
}
EXISTING_EMAIL_PROVIDER = {
    'code': 35,
    'message': 'Existing email provider'
}
NO_SUCH_EMAIL_PROVIDER = {
    'code': 36,
    'message': 'No such email provider'
}
FACEBOOK_LOGIN_INVALID = {
    'code': 37,
    'message': 'Facebook login invalid'
}
NAVER_LOGIN_INVALID = {
    'code': 38,
    'message': 'Naver login invalid'
}
KAKAO_LOGIN_INVALID = {
    'code': 39,
    'message': 'Kakao login invalid'
}
GOOGLE_LOGIN_INVALID = {
    'code': 40,
    'message': 'Google login invalid'
}
EXISTING_ACCOUNT_VIA_OTHER_LOGIN_METHOD = {
    'code': 41,
    'message': 'Existing account via other login method'
}
EXISTING_SORT_KEY = {
    'code': 42,
    'message': 'Existing sort index key'
}
EXISTING_SLACK_WEBHOOK_NAME = {
    'code': 43,
    'message': 'Existing slack webhook name'
}
NO_SUCH_SLACK_WEBHOOK = {
    'code': 44,
    'message': 'No such slack webhook'
}
QUERY_POLICY_VIOLATION = {
    'code': 45,
    'message': 'Query policy violation'
}
JOIN_POLICY_VIOLATION = {
    'code': 46,
    'message': 'Join policy violation'
}
UPDATE_POLICY_VIOLATION = {
    'code': 47,
    'message': 'Update policy violation',
}
DELETE_POLICY_VIOLATION = {
    'code': 48,
    'message': 'Delete policy violation',
}
CREATE_POLICY_VIOLATION = {
    'code': 49,
    'message': 'Create policy violation',
}
NOT_USER_PARTITION = {
    'code': 50,
    'message': 'Not a user partition'
}
READ_POLICY_VIOLATION = {
    'code': 51,
    'message': 'Read policy violation',
}
UNREGISTERED_PARTITION = {
    'code': 52,
    'message': 'Unregistered partition',
}
SESSION_SECURITY_VIOLATION = {
    'code': 53,
    'message': 'This is a group that has session security hardened. '
               'Session access was rejected because '
               'it was different from the region you accessed when logging in.',
}

SESSION_NOT_VERIFICATION = {
    'code': 54,
    'message': 'Session security hardened. '
               'Session access was rejected because '
               'it was different from the region you accessed when logging in.',
}

INVALID_ITEM_ID = {
    'code': 55,
    'message': 'Invalid item_id'
}

LOGIN_IS_REQUIRED = {
    'code': 56,
    'message': 'Login is required'
}

CANNOT_RUN_ON_NON_SERVERLESS = {
    'code': 57,
    'message': 'You can run this function on serverless service only'
}

REQUIRED_PARAMS_NOT_EXIST = {
    'code': 58,
    'message': 'You should input all required parameters. See https://docs.aws-interface.com'
}