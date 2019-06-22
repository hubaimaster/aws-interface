
from cloud.response import Response
from cloud.permission import Permission, NeedPermission
import base64


# Define the input output format of the function.
# This information is used when creating the *SDK*.
info = {
    'input_format': {
        'function_name': 'str',
    },
    'output_format': {
        'item?': {
            'base64': 'str',
        },
        'error?': {
            'code': 'int',
            'message': 'str',
        },
    }
}


@NeedPermission(Permission.Run.Logic.get_function_zip_b64)
def do(data, resource):
    partition = 'logic-function'
    body = {}
    params = data['params']

    function_name = params.get('function_name')

    items, _ = resource.db_query(partition,
                                 [{'option': None, 'field': 'function_name', 'value': function_name,
                                   'condition': 'eq'}])

    if len(items) == 0:
        body['message'] = 'function_name: {} did not exist'.format(function_name)
        return Response(body)
    else:
        item = items[0]
        zip_file_id = item['zip_file_id']
        file_b64 = resource.file_download_bin(zip_file_id)
        file_b64 = base64.b64encode(file_b64)
        file_b64 = file_b64.decode('utf-8')
        body['item'] = {
            'base64': file_b64,
        }
        return Response(body)
