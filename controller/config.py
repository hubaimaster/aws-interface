
class Variable:
    table_prefix = 'resource-interface-'
    model_table = 'model-table-'


class Key:
    user_table_enabled = 'user_table_enabled'
    user_property_list = 'user_property_list'
    user_group_list = 'user_group_list'
    model_property_list = 'model_property_list'

    creationDate = 'creationDate'


class Message:
    success = 0, 'success'
    permission_denied = 1, 'permission denied'

