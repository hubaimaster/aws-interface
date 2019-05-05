from abc import ABCMeta
from resource.sdk import generate


class ResourceAllocator(metaclass=ABCMeta):
    def __init__(self, credential, app_id):
        self.credential = credential
        self.app_id = app_id

    def get_credential(self):
        return self.credential

    def get_app_id(self):
        return self.app_id

    def generate_sdk(self, platform):
        return generate(self.get_rest_api_url(), platform)

    # API, create and terminate.
    def create(self):
        """
        Apply/deploy the recipe to AWS backend services. This includes
        setting up interfaces through AWS Lambda and API Gateway.
        :return:
        """
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def get_rest_api_url(self):
        raise NotImplementedError


class IDDict(dict):
    def __hash__(self):
        return hash(self['id'])


class Resource(metaclass=ABCMeta):
    def __init__(self, credential, app_id):
        self.credential = credential
        self.app_id = app_id

    # backend resource cost
    def cost_for(self, start, end):
        raise NotImplementedError

    def cost_and_usage_for(self, start, end):
        raise NotImplementedError

    # DB ops
    def db_create_partition(self, partition):
        raise NotImplementedError

    def db_has_partition(self, partition):
        raise NotImplementedError

    def db_delete_partition(self, partition):
        raise NotImplementedError

    def db_delete_item(self, item_id):
        raise NotImplementedError

    def db_delete_item_batch(self, item_ids):
        raise NotImplementedError

    def db_get_item(self, item_id):
        raise NotImplementedError

    def db_get_items(self, item_ids):
        raise NotImplementedError

    def db_get_items_in_partition(self, partition, start_key=None, limit=None, reverse=False):
        raise NotImplementedError

    def db_put_item(self, partition, item, item_id=None, creation_date=None):
        """This is connected with db_get_count"""
        raise NotImplementedError

    def db_update_item(self, item_id, item):
        raise NotImplementedError

    def db_get_count(self, partition):
        raise NotImplementedError

    def db_get_item_ids_equal(self, partition, field, value, start_key, limit):
        raise NotImplementedError

    # File ops
    def file_download_bin(self, file_id):
        raise NotImplementedError

    def file_upload_bin(self, file_id, file_base64):
        raise NotImplementedError

    def file_delete_bin(self, file_id):
        raise NotImplementedError

    # Server-less ops
    def sl_create_function(self, function_name, runtime, handler, zip_file_bin):
        raise NotImplementedError

    def sl_delete_function(self, function_name):
        raise NotImplementedError

    def sl_update_function(self, function_name, zip_file_bin):
        raise NotImplementedError

    def sl_invoke_function(self, function_name, payload):
        """
        :param function_name:
        :param payload: Parameters that function required
        :return: error:str|None, response_payload:dict|None
        """
        raise NotImplementedError

    # SHOULD NOT RE-IMPLEMENT
    def db_query(self, partition, instructions, start_index=0, limit=100):
        """:return:items:list,end_key:str"""
        # TODO 상위레이어에서 쿼리를 순차적으로 실행가능한 instructions 으로 만들어 전달 -> ORM 클래스 만들기

        def get_items():
            item_set = set()
            for idx, option_statement in enumerate(instructions):
                if isinstance(option_statement, list):
                    option = option_statement[0]
                    statement = (option_statement[1], option_statement[2], option_statement[3])
                elif isinstance(option_statement, tuple):
                    (option, statement) = option_statement
                elif isinstance(option_statement, dict):
                    option = option_statement['option']
                    statement = (option_statement['field'], option_statement['condition'], option_statement['value'])
                else:
                    raise BaseException('Unknown instruction type')

                instruction_type = self._db_instruction_type(statement, option)
                if instruction_type == 'index':
                    if option == 'and':
                        item_set &= set(self._db_index_items(statement, partition))
                    elif option == 'or' or option is None:
                        item_set |= set(self._db_index_items(statement, partition))
                elif instruction_type == 'filter':
                    if option == 'and':
                        item_set = set(self._db_filter_items(statement, item_set))
                    elif option == 'or' or option is None:
                        raise BaseException('You cannot use option [or] on filtering')
                elif instruction_type == 'scan':
                    if option == 'and':
                        item_set &= set(self._db_scan_items(statement, partition))
                    elif option == 'or' or option is None:
                        item_set |= set(self._db_scan_items(statement, partition))
            return list(item_set)
        if not limit:
            limit = 100
        if not start_index:
            start_index = 0
        items = get_items()
        items = items[start_index: start_index + limit]
        items = self._db_batch_fake_items_to_real(items)

        end_index = start_index + limit
        return list(items), end_index

    def _db_instruction_type(self, statement, option):
        field, condition, value = statement
        if option == 'and':
            if condition == 'eq':
                return 'index'
            else:
                return 'filter'
        elif option == 'or':
            if condition == 'eq':
                return 'index'
            else:
                return 'scan'
        elif option is None:
            if condition == 'eq':
                return 'index'
            else:
                return 'scan'
        else:
            raise BaseException('No such option : [{}]'.format(option))

    def _db_get_fake_item(self, item_id):
        return {
            'id': item_id,
            '_is_fake': True
        }

    def _db_batch_fake_items_to_real(self, items):
        item_ids = [item['id'] for item in items]
        bulk_size = 100
        items = []
        for i in range(0, len(item_ids), bulk_size):
            items.extend(self.db_get_items(item_ids[i:i+bulk_size]))
        for item in items:
            yield IDDict(item)

    def _db_index_items(self, statement, partition):
        field, condition, value = statement
        start_key = None
        while True:
            if condition == 'eq':
                item_ids, start_key = self.db_get_item_ids_equal(partition, field, value, start_key, 10000)
                for item_id in item_ids:
                    yield IDDict(self._db_get_fake_item(item_id))
            else:
                raise BaseException('You cannot use condition : [{}] for indexing'.format(condition))
            if start_key is None:
                break

    def _db_filter_items(self, statement, items):
        field, condition, value = statement
        items = self._db_batch_fake_items_to_real(items)
        for item in items:
            item_value = item.get(field, None)
            if not item_value:
                continue
            else:
                if condition == 'eq':
                    if value == item_value:
                        yield item
                elif condition == 'in':
                    if value in item_value:
                        yield item
                elif condition == 'gt':
                    if isinstance(item_value, str):
                        if str(value) < str(item_value):
                            yield item
                    else:
                        if float(value) < float(item_value):
                            yield item
                elif condition == 'ls':
                    if isinstance(item_value, str):
                        if str(value) > str(item_value):
                            yield item
                    else:
                        if float(value) > float(item_value):
                            yield item
                elif condition == 'ge':
                    if isinstance(item_value, str):
                        if str(value) <= str(item_value):
                            yield item
                    else:
                        if float(value) <= float(item_value):
                            yield item
                elif condition == 'le':
                    if isinstance(item_value, str):
                        if str(value) >= str(item_value):
                            yield item
                    else:
                        if float(value) >= float(item_value):
                            yield item
                else:
                    raise BaseException('No such condition : [{}]'.format(condition))

    def _db_scan_items(self, statement, partition):
        start_key = None
        while True:
            items, start_key = self.db_get_items_in_partition(partition, start_key)
            for item in self._db_filter_items(statement, items):
                yield IDDict(item)
            if start_key is None:
                break
