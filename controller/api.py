from controller.config import Message
from controller.config import Variable as Config
from controller.config import Key


class Response(dict):
    def __init__(self, msg, data=None):
        if data is not None:
            self['data'] = data
        message_code = msg[0]
        message_text = msg[1]
        self['message'] = {
            'code': message_code,
            'text': message_text
        }

    def get_data(self):
        return self['data']

    def get_message(self):
        return self['message']


class API:
    def __init__(self, resource_cls):
        self.resource_cls = resource_cls

    # <-- apps -->
    def create_backend_service(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        resource.create_table(service_name)
        return Response(Message.success)

    def get_backend_service_list(self, request):
        resource = self.resource_cls(request)
        table_list = resource.get_table_list()
        return Response(Message.success, {'items': table_list})


    # <-- detail -->
    def get_backend_service(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        table = resource.get_table(service_name)
        return Response(Message.success, {'item': table})

    def set_user_table_enabled(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        enabled = resource.get_param('enabled')
        if enabled == 'false' or enabled == 'False' or enabled == 0:
            enabled = False
        else:
            enabled = True
        resource.set_table_value(service_name, Key.user_table_enabled, enabled)
        return Response(Message.success)

    def get_backend_service_sdk(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        platform = request.get_param('platform')
        raise NotImplementedError()


    # <-- app-member -->
    def create_user_table(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        resource.create_table_index(service_name, 'user')
        return Response(Message.success)


    def create_user_property(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        data_type = request.get_param('data_type')
        read_group_name = request.get_param('read_group_name')
        write_group_name = request.get_param('write_group_name')
        p_list = resource.get_table_value(service_name, Key.user_property_list)
        p = {
            'name': name,
            'data_type': data_type,
            'read_group_name': read_group_name,
            'write_group_name': write_group_name,
        }
        p_list.append(p)
        resource.set_table_value(service_name, Key.user_property_list, p_list)
        return Response(Message.success)


    def create_user_group(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        desc = request.get_param('desc')
        g_list = resource.get_table_value(service_name, Key.user_group_list)
        for g in g_list:
            if g['name'] == name:
                g_list.remove(g)
        g = {
            'name': name,
            'desc': desc,
        }
        g_list.append(g)
        resource.set_table_value(service_name, Key.user_group_list, g_list)
        return Response(Message.success)


    def delete_user_group(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        g_list = resource.get_table_value(service_name, Key.user_group_list)
        for g in g_list:
            if g['name'] == name:
                g_list.remove(g)
        resource.set_table_value(service_name, Key.user_group_list, g_list)
        return Response(Message.success)


    def get_user_group_list(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        g_list = resource.get_table_value(service_name, Key.user_group_list)
        return Response(Message.success, {'items': g_list})


    def get_user_property_list(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        p_list = resource.get_table_value(service_name, Key.user_property_list)
        return Response(Message.success, {'items': p_list})


    #<-- app-model -->
    def create_model_table(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        hash_key = Config.model_table + name
        sort_key = Key.creationDate
        resource.create_table_index(service_name, name, hash_key, sort_key)
        return Response(Message.success)


    def get_model_property_list(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        model_table_name = resource.get_param('model_table_name')
        ref_key = Key.model_property_list + '_' + model_table_name
        p_list = resource.get_table_value(service_name, ref_key)
        return Response(Message.success, {'items': p_list})


    def get_model_table_list(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        t_list = resource.get_table_list(service_name)
        return Response(Message.success, {'items': t_list})


    def delete_model_table(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        name = resource.get_param('name')
        resource.delete_table_index(service_name, name)
        return Response(Message.success)


if __name__ == '__main__':
    from controller.aws.aws_resource import AwsResource
    from controller.aws.aws_request import AwsRequest

    ACCESSKEY = 'AKIAITLSY742M3WP5HRA'
    SECRETKEY = 'c+L1O5g7HZDcYYs2VchKVxT+Emkxp3yVAOyC'
    REGION = 'ap-northeast-2'

    request = AwsRequest(ACCESSKEY, SECRETKEY, REGION, {'table_name': 'test_table',
                                                            'index_name': 'test_index',
                                                            'hash_key': 'part',
                                                            'sort_key': 'creationDate'})

    api = API(AwsResource)
    api.create_backend_service(request)
