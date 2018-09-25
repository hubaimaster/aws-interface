from controller.protocol import Response, Msg, Config


class API:
    def __init__(self, resource_cls):
        self.resource_cls = resource_cls

    # <-- apps -->
    def create_backend_service(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')

        resource.create_table(Config.table_prefix + service_name)
        return Response(Msg.success)


    def get_backend_service_list(self, request):
        resource = self.resource_cls(request)
        table_list = resource.get_table_list()
        raise NotImplementedError()


    # <-- detail -->
    def get_backend_service(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError() #Return Member, Model..


    def set_user_table_enabled(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    # <-- app-member -->
    def create_user_table(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def create_user_property(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def create_user_group(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def create_user(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def delete_user(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def delete_user_group(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_user_group_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_user_property_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_user_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    #<-- app-model -->
    def create_model_table(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def create_model(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_model_property_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_model_table_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def get_model_list(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def delete_model(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()


    def delete_model_table(self, request):
        resource = self.resource_cls(request)
        raise NotImplementedError()



if __name__ == '__main__':
    import controller.aws as aws

    resource_cls = aws.AwsResource
    ACCESSKEY = 'AKIAITLSY742M3WP5HRA'
    SECRETKEY = 'c+L1O5g7HZDcYYs2VchKVxT+Emkxp3yVAOyC'
    REGION = 'ap-northeast-2'

    request = aws.AwsRequest(ACCESSKEY, SECRETKEY, REGION, {'table_name': 'test_table',
                                                            'index_name': 'test_index',
                                                            'hash_key': 'part',
                                                            'sort_key': 'creationDate'})

    api = API(resource_cls)
    api.create_backend_service(request)
