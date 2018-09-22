from controller.protocol import Response, Msg, Config


def create_backend_service(resource_cls, request):
    resource = resource_cls(request)
    table_name = request.get_param('table_name')

    resource.create_table(Config.table_prefix + table_name)
    return Response(Msg.success)


def create_backend_service_model(resource_cls, request):
    resource = resource_cls(request)
    table_name = request.get_param('table_name')
    index_name = request.get_param('index_name')
    hash_key = request.get_param('hash_key')
    sort_key = request.get_param('sort_key')

    resource.create_table_index(table_name, index_name, hash_key, sort_key)
    return Response(Msg.success)


if __name__ == '__main__':
    import controller.aws as aws

    resource_cls = aws.AwsResource
    ACCESSKEY = 'AKIAITLSY742M3WP5HRA'
    SECRETKEY = 'c+L1O5g7HZDcYYs2VchKVxT+Emkxp3yVAOyC'
    REGION = 'ap-northeast-2'

    request = aws.AwsRequest(ACCESSKEY, SECRETKEY, REGION, {'table_name': 'test_table'})
    #create_backend_service(resource_cls, request)

    request = aws.AwsRequest(ACCESSKEY, SECRETKEY, REGION, {'table_name': 'test_table',
                                                            'index_name': 'test_index',
                                                            'hash_key': 'part',
                                                            'sort_key': 'creationDate'})
    create_backend_service_model(resource_cls, request)
