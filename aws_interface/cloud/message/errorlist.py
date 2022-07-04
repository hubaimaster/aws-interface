"""
error.py 보다 진보된 에러처리
이게 raise 되면 루트 함수에서 body['error'] 로 라우팅 해줌
"""


class CloudLogicError(Exception):
    @classmethod
    def from_dict(cls, code_message_pair):
        code = code_message_pair.get('code', -1)
        message = code_message_pair.get('message', None)
        return CloudLogicError(code, message)

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __getattr__(self, item):
        return {
            'code': self.code,
            'message': self.message
        }

    def __str__(self):
        return repr(f'<SERVER ERROR> Code: [{str(self.code).rjust(6, "0")}] Message: [{self.message}]')


PERMISSION_DENIED = CloudLogicError.from_dict({
    'code': 1,
    'message': 'Permission denied'
})

GUEST_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 2,
    'message': 'Guest login has been deactivated'
})

NO_SUCH_GUEST = CloudLogicError.from_dict({
    'code': 3,
    'message': 'No such guest'
})

EMAIL_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 4,
    'message': 'Email login has been deactivated'
})

WRONG_PASSWORD = CloudLogicError.from_dict({
    'code': 5,
    'message': 'Password did not match'
})

NO_SUCH_ACCOUNT = CloudLogicError.from_dict({
    'code': 6,
    'message': 'No such account'
})

LOGOUT_FAILED = CloudLogicError.from_dict({
    'code': 7,
    'message': 'Logout failed'
})

PUT_USER_GROUP_FAILED = CloudLogicError.from_dict({
    'code': 8,
    'message': 'Insert user group failed'
})

EXISTING_ACCOUNT = CloudLogicError.from_dict({
    'code': 9,
    'message': 'Existing account'
})

FORBIDDEN_MODIFICATION = CloudLogicError.from_dict({
    'code': 10,
    'message': 'Forbidden modifications'
})

NO_SUCH_PARTITION = CloudLogicError.from_dict({
    'code': 11,
    'message': 'No such partition'
})

NUM_OF_BATCH_ITEMS_MUST_BE_LESS_THAN_128 = CloudLogicError.from_dict({
    'code': 12,
    'message': 'Number of item_ids must be less than 128'
})

LOG_CREATION_FAILED = CloudLogicError.from_dict({
    'code': 13,
    'message': 'Log creation failed'
})

INVALID_SESSION = CloudLogicError.from_dict({
    'code': 14,
    'message': 'Invalid session'
})

INVALID_FILE_KEY = CloudLogicError.from_dict({
    'code': 15,
    'message': 'Invalid file key'
})

INVALID_REQUEST = CloudLogicError.from_dict({
    'code': 16,
    'message': 'Invalid request, please check parameters'
})

FORBIDDEN_REQUEST = CloudLogicError.from_dict({
    'code': 17,
    'message': 'Forbidden request'
})

NO_SUCH_FUNCTION = CloudLogicError.from_dict({
    'code': 18,
    'message': 'No such function'
})

DEFAULT_USER_GROUP_CANNOT_BE_MODIFIED = CloudLogicError.from_dict({
    'code': 19,
    'message': 'Default user groups can not be modified'
})

EXISTING_FUNCTION = CloudLogicError.from_dict({
    'code': 20,
    'message': 'Function name already exists'
})

FUNCTION_ERROR = CloudLogicError.from_dict({
    'code': 21,
    'message': 'Function has errors: {}'
})

NO_SUCH_FUNCTION_TEST = CloudLogicError.from_dict({
    'code': 22,
    'message': 'No such function test'
})

NO_SUCH_POLICY_MODE = CloudLogicError.from_dict({
    'code': 23,
    'message': 'No such policy mode'
})

NO_SUCH_ITEM = CloudLogicError.from_dict({
    'code': 24,
    'message': 'No such item'
})

UNSUPPORTED_FILE_TYPE = CloudLogicError.from_dict({
    'code': 25,
    'message': 'Unsupported file type'
})

NO_SUCH_FILE = CloudLogicError.from_dict({
    'code': 26,
    'message': 'No such file'
})

ADMIN_GROUP_CANNOT_BE_MODIFIED = CloudLogicError.from_dict({
    'code': 27,
    'message': 'An admin group can not be modified'
})

NO_SUCH_LOGIN_METHOD = CloudLogicError.from_dict({
    'code': 28,
    'message': 'No such login method',
})

REGISTER_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 29,
    'message': 'Register policy violation',
})

EXISTING_TRIGGER = CloudLogicError.from_dict({
    'code': 30,
    'message': 'Existing trigger'
})

EXISTING_WEBHOOK = CloudLogicError.from_dict({
    'code': 31,
    'message': 'Existing webhook'
})

NO_SUCH_WEBHOOK = CloudLogicError.from_dict({
    'code': 32,
    'message': 'No such webhook'
})

EXISTING_SCHEDULE = CloudLogicError.from_dict({
    'code': 33,
    'message': 'Existing schedule'
})

NO_SUCH_SCHEDULE = CloudLogicError.from_dict({
    'code': 34,
    'message': 'No such schedule'
})

EXISTING_EMAIL_PROVIDER = CloudLogicError.from_dict({
    'code': 35,
    'message': 'Existing email provider'
})

NO_SUCH_EMAIL_PROVIDER = CloudLogicError.from_dict({
    'code': 36,
    'message': 'No such email provider'
})

FACEBOOK_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 37,
    'message': 'Facebook login invalid'
})

NAVER_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 38,
    'message': 'Naver login invalid'
})

KAKAO_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 39,
    'message': 'Kakao login invalid'
})

GOOGLE_LOGIN_INVALID = CloudLogicError.from_dict({
    'code': 40,
    'message': 'Google login invalid'
})

EXISTING_ACCOUNT_VIA_OTHER_LOGIN_METHOD = CloudLogicError.from_dict({
    'code': 41,
    'message': 'Existing account via other login method'
})

EXISTING_SORT_KEY = CloudLogicError.from_dict({
    'code': 42,
    'message': 'Existing sort index key'
})

EXISTING_SLACK_WEBHOOK_NAME = CloudLogicError.from_dict({
    'code': 43,
    'message': 'Existing slack webhook name'
})

NO_SUCH_SLACK_WEBHOOK = CloudLogicError.from_dict({
    'code': 44,
    'message': 'No such slack webhook'
})

QUERY_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 45,
    'message': 'Query policy violation'
})

JOIN_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 46,
    'message': 'Join policy violation'
})

UPDATE_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 47,
    'message': 'Update policy violation',
})

DELETE_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 48,
    'message': 'Delete policy violation',
})

CREATE_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 49,
    'message': 'Create policy violation',
})

NOT_USER_PARTITION = CloudLogicError.from_dict({
    'code': 50,
    'message': 'Not a user partition'
})

READ_POLICY_VIOLATION = CloudLogicError.from_dict({
    'code': 51,
    'message': 'Read policy violation',
})

UNREGISTERED_PARTITION = CloudLogicError.from_dict({
    'code': 52,
    'message': 'Unregistered partition',
})

SESSION_SECURITY_VIOLATION = CloudLogicError.from_dict({
    'code': 53,
    'message': 'This is a group that has session security hardened. '
               'Session access was rejected because '
               'it was different from the region you accessed when logging in.',
})

SESSION_NOT_VERIFICATION = CloudLogicError.from_dict({
    'code': 54,
    'message': 'Session security hardened. '
               'Session access was rejected because '
               'it was different from the region you accessed when logging in.',
})

INVALID_ITEM_ID = CloudLogicError.from_dict({
    'code': 55,
    'message': 'Invalid item_id'
})

LOGIN_IS_REQUIRED = CloudLogicError.from_dict({
    'code': 56,
    'message': 'Login is required'
})

CANNOT_RUN_ON_NON_SERVERLESS = CloudLogicError.from_dict({
    'code': 57,
    'message': 'You can run this function on serverless service only'
})

REQUIRED_PARAMS_NOT_EXIST = CloudLogicError.from_dict({
    'code': 58,
    'message': 'You should input all required parameters. See https://docs.aws-interface.com'
})

EXISTING_PARTITION = CloudLogicError(
    59, 'Partition already exists'
)

ITEM_MUST_BE_DICTIONARY = CloudLogicError(
    60, 'ITEM_MUST_BE_DICTIONARY'
)

KEY_CANNOT_START_WITH_UNDER_BAR = CloudLogicError(
    61, 'ITEM KEY CANNOT START WITH UNDER_BAR'
)

ITEM_PK_SK_PAIR_ALREADY_EXIST = CloudLogicError(
    62, 'A combination of <item._pk & item._sk> must be unique'
)

ITEM_ID_PAIRS_MUST_BE_DICTIONARY = CloudLogicError(
    63, 'ITEM_ID_PAIRS_MUST_BE_DICTIONARY'
)

ITEM_PARTITION_NOT_MATCH = CloudLogicError(
    64, 'ITEM_PARTITION_NOT_MATCH'
)

INVALID_PK_GROUP = CloudLogicError(
    65, 'INVALID_PK_GROUP'
)

NEED_SORT_CONDITION = CloudLogicError(
    66, 'NEED <sort_condition> param'
)

NEED_SK_GROUP = CloudLogicError(
    67, 'NEED <sk_group> param'
)

NEED_PARTITION = CloudLogicError(
    68, 'NEED <partition> param'
)
NEED_SK_FIELD = CloudLogicError(
    69, 'NEED <sk_field> param'
)
NEED_SK_VALUE = CloudLogicError(
    70, 'NEED <sk_value> param'
)
NEED_ITEM_ID = CloudLogicError(
    71, 'Need <item_id> param'
)
NEED_ITEM = CloudLogicError(
    72, 'Need <item> param'
)
ITEM_ID_PAIRS = CloudLogicError(
    73, 'Need <item_id_pairs> param'
)
NEED_PK_GROUP = CloudLogicError(
    74, 'Need <pk_group> param'
)
NEED_PK_FIELD = CloudLogicError(
    75, 'Need <pk_field> param'
)
NEED_PK_VALUE = CloudLogicError(
    76, 'Need <pk_value> param'
)

NEED_MODE = CloudLogicError(
    77, 'Need <mode> param'
)

NEED_CODE = CloudLogicError(
    78, 'Need <code> param'
)

NEED_ITEM_IDS = CloudLogicError(
    79, 'Need <item_ids> param'
)
NEED_ITEMS = CloudLogicError(
    80, 'Need <items> param'
)
ITEM_ID_MUST_BE_STRING = CloudLogicError(
    81, '<item_id> must be string type'
)