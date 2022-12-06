
from cloud.permission import Permission, NeedPermission

# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
    },
    'output_format': {
        'success': 'bool'
    }
}


@NeedPermission(Permission.Run.Logic.delete_function)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')
    function_version = params.get('function_version', 0)

    if function_version is None:
        function_version = 0

    query = [{'option': None, 'field': 'function_name', 'value': function_name, 'condition': 'eq'}]
    items, _ = resource.db_query(partition, query, reverse=True)
    for item in items:
        if int(item.get('function_version', -1)) == int(function_version):
            success = resource.db_delete_item(item['id'])
            if item.get('use_standalone', False):
                # standalone 함수는 resource 로 함수 객체 삭제
                standalone_function_name = f'{function_name}_{function_version}'
                delete_stand_alone_response = resource.function_delete_stand_alone_function(standalone_function_name)
                body['delete_stand_alone_response'] = delete_stand_alone_response
            body['success'] = success

    return body
