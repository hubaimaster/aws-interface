
class Variable:
    table_prefix = 'aws-interface-'
    index_prefix = 'aws-interface-index-'
    model_table = 'aws-interface-model-'


class Enum:
    user_table_enabled = 'user_table_enabled'
    user_property_list = 'user_property_list'
    user_group_list = 'user_group_list'
    model_property_list = 'model_property_list'

    modelPartition = 'modelPartition'
    creationDate = 'creationDate'
    tableValue = 'tableValue'


class Message:
    success = 0, 'success'
    permission_denied = 1, 'permission denied'

