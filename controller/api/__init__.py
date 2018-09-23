from controller.protocol import Response, Msg, Config

# <-- apps -->
def create_backend_service(resource_cls, request):
    resource = resource_cls(request)
    table_name = request.get_param('table_name')

    resource.create_table(Config.table_prefix + table_name)
    return Response(Msg.success)


def get_backend_service_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


# <-- detail -->
def create_backend_service(resource_cls, request):
    resource = resource_cls(request)
    table_name = request.get_param('table_name')
    index_name = request.get_param('index_name')
    hash_key = request.get_param('hash_key')
    sort_key = request.get_param('sort_key')

    resource.create_table_index(table_name, index_name, hash_key, sort_key)
    return Response(Msg.success)


def get_backend_service_info(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError() #Return Member, Model..


def set_user_table_enabled(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


# <-- app-member -->
def create_user_table(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def create_user_property(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def create_user_group(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def create_user(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def delete_user(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def delete_user_group(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_user_group_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_user_property_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_user_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


#<-- app-model -->

def create_model_table(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def create_model(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_model_property_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_model_table_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def get_model_list(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def delete_model(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()


def delete_model_table(resource_cls, request):
    resource = resource_cls(request)
    raise NotImplementedError()



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
    create_backend_service(resource_cls, request)
