from abc import ABCMeta
from resource.sdk import generate


class ResourceAllocator(metaclass=ABCMeta):
    def __init__(self, credential, app_id, recipes):
        self.credential = credential
        self.app_id = app_id
        self.recipes = recipes

    def get_recipes(self):
        return self.recipes

    def get_credential(self):
        return self.credential

    def get_app_id(self):
        return self.app_id

    def generate_sdk(self, platform):
        return generate(self, platform)

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

    def get_logs(self):
        raise NotImplementedError


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

    def db_delete_partition(self, partition):
        raise NotImplementedError

    def db_delete_item(self, item_id):
        raise NotImplementedError

    def db_delete_item_batch(self, item_ids):
        raise NotImplementedError

    def db_get_item(self, item_id):
        raise NotImplementedError

    def db_get_items(self, partition, start_key=None, limit=None, reverse=False):
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

    def db_get_item_ids_include(self, partition, field, value, start_key, limit):
        raise NotImplementedError

    # File ops
    def file_download_base64(self, file_id):
        raise NotImplementedError

    def file_upload_base64(self, file_id, file_base64):
        raise NotImplementedError

    def file_delete_base64(self, file_id):
        raise NotImplementedError

    # SHOULD NOT RE-IMPLEMENT
    def db_query(self, partition, instructions, start_keys=None, limit=100):
        """:return:items:list,end_key:str"""
        # TODO 상위레이어에서 쿼리를 순차적으로 실행가능한 instructions 으로 만들어 전달 -> ORM 클래스 만들기
        all_item_ids = set()
        print(instructions)
        if start_keys is None:
            start_keys = [None] * len(instructions)

        def q(temp_start_keys):
            item_ids = set()
            end_keys = []
            for idx, option_statement in enumerate(instructions):
                if isinstance(option_statement, list):
                    option = option_statement[0]
                    statement = (option_statement[1], option_statement[2], option_statement[3])
                elif isinstance(option_statement, tuple):
                    (option, statement) = option_statement
                elif isinstance(option_statement, dict):
                    option = option_statement['option']
                    statement = (option_statement['field'], option_statement['condition'], option_statement['value'])
                start_key = temp_start_keys[idx]
                ids, end_key = self._invoke_statement(partition, statement, start_key, limit)
                end_keys.append(end_key)
                if option == 'and':
                    item_ids &= ids
                elif option == 'or':
                    item_ids |= ids
                else:
                    item_ids |= ids
            return item_ids, end_keys

        _end_keys = [None] * len(instructions)
        while limit > len(all_item_ids):
            _item_ids, _end_keys = q(start_keys)
            all_item_ids |= _item_ids
            if all(end_key is None for end_key in _end_keys):
                _end_keys = None
                break
        all_item_ids = list(all_item_ids)
        items = [self.db_get_item(item_id) for item_id in all_item_ids]
        return items, _end_keys

    def _invoke_statement(self, partition, statement, start_key, limit):
        field, condition, value = statement
        if condition == 'eq':
            return self.db_get_item_ids_equal(partition, field, value, start_key, limit)
        elif condition == 'in':
            return self.db_get_item_ids_include(partition, field, value, start_key, limit)
        else:
            raise BaseException('an operation must be <eq> or <in> not <', condition, '>')
