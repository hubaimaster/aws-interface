from controller.config import Message
from controller.config import Enum
from time import sleep


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


class Executor:
    def __init__(self, delay=7, limit=3):
        self.delay = delay
        self.limit = limit

    def run(self, func, *params):
        for i in range(self.limit):
            sleep(self.delay)
            try:
                func(*params)
                print('Executing success!')
                break
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message, 'on count', i)
                if type(ex).__name__ != 'ResourceInUseException':
                    break
                else:
                    continue


class API:
    def __init__(self, resource_cls):
        self.resource_cls = resource_cls
        self.executor = Executor()

    # <-- apps -->
    def create_backend_service(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')

        self.executor.run(resource.create_table, service_name)
        self.executor.run(resource.create_table_index, service_name, Enum.modelPartition, Enum.creationDate)

        resource.set_table_value(service_name, 'member_enabled', True)
        resource.set_table_value(service_name, 'model_enabled', True)

        return Response(Message.success)

    def get_backend_service_list(self, request):
        resource = self.resource_cls(request)
        table_list = resource.get_table_list()
        return Response(Message.success, {'items': table_list})

    #TODO
    # <-- detail -->
    def get_backend_service(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        name = service_name
        member_enabled = resource.get_table_value(service_name, 'member_enabled')
        model_enabled = resource.get_table_value(service_name, 'model_enabled')
        return Response(Message.success, {'item': {
            'name': name,
            'member_enabled': member_enabled,
            'model_enabled': model_enabled,
        }})

    def set_user_table_enabled(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        enabled = resource.get_param('enabled')
        if enabled == 'false' or enabled == 'False' or enabled == 0:
            enabled = False
        else:
            enabled = True
        resource.set_table_value(service_name, Enum.user_table_enabled, enabled)
        return Response(Message.success)

    def get_backend_service_sdk(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        platform = request.get_param('platform')
        raise NotImplementedError()


    def create_user_property(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        data_type = request.get_param('data_type')
        read_group_name = request.get_param('read_group_name')
        write_group_name = request.get_param('write_group_name')
        p_list = resource.get_table_value(service_name, Enum.user_property_list)
        p = {
            'name': name,
            'data_type': data_type,
            'read_group_name': read_group_name,
            'write_group_name': write_group_name,
        }
        p_list.append(p)
        resource.set_table_value(service_name, Enum.user_property_list, p_list)
        return Response(Message.success)


    def create_user_group(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        desc = request.get_param('desc')
        g_list = resource.get_table_value(service_name, Enum.user_group_list)
        for g in g_list:
            if g['name'] == name:
                g_list.remove(g)
        g = {
            'name': name,
            'desc': desc,
        }
        g_list.append(g)
        resource.set_table_value(service_name, Enum.user_group_list, g_list)
        return Response(Message.success)


    def delete_user_group(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        g_list = resource.get_table_value(service_name, Enum.user_group_list)
        for g in g_list:
            if g['name'] == name:
                g_list.remove(g)
        resource.set_table_value(service_name, Enum.user_group_list, g_list)
        return Response(Message.success)


    def get_user_group_list(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        g_list = resource.get_table_value(service_name, Enum.user_group_list)
        return Response(Message.success, {'items': g_list})


    def get_user_property_list(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        p_list = resource.get_table_value(service_name, Enum.user_property_list)
        return Response(Message.success, {'items': p_list})


    #<-- app-model -->
    def create_model_table(self, request):
        resource = self.resource_cls(request)
        service_name = request.get_param('service_name')
        name = request.get_param('name')
        m_list = resource.get_table_value(service_name, 'model_list')
        if m_list is None: m_list = []
        m_list.append(name)
        resource.set_table_value(service_name, 'model_list', m_list)
        return Response(Message.success)


    def get_model_property_list(self, request):
        resource = self.resource_cls(request)
        service_name = resource.get_param('service_name')
        model_table_name = resource.get_param('model_table_name')
        ref_key = Enum.model_property_list + '_' + model_table_name
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
