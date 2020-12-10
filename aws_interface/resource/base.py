from abc import ABCMeta
from concurrent.futures import ThreadPoolExecutor
import time
import json
import copy
from collections.abc import Iterable


class ResourceAllocator(metaclass=ABCMeta):
    def __init__(self, credential, app_id):
        self.credential = credential
        self.app_id = app_id

    def get_credential(self):
        return self.credential

    def get_app_id(self):
        return self.app_id

    def generate_sdk(self, platform):
        from sdk import generate
        return generate(self.get_rest_api_url(), platform)

    # API, create and terminate.
    def create(self):
        """
        Apply/deploy the recipe to backend services like aws, azure, gcp, ... This includes
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

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Resource(metaclass=ABCMeta):
    def __init__(self, credential, app_id):
        self.credential = credential
        self.app_id = app_id

    def get_rest_api_url(self):
        raise NotImplementedError

    def create_webhook_url(self, name):
        """
        Create url string (Literally just string) like https://...?gateway=name
        or https://.../gateway/name (Because of to match available url format type of the various vendors
        Ex: AWS using query parameters to make integrated request)
        used to make webhooks ...
        :param name: An identifier seed to make url
        :return: Url string to be created
        """
        raise NotImplementedError

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

    def db_create_sort_index(self, sort_key, sort_key_type):
        """
        Create sort index table
        :param sort_key: str ('creation_date', 'score', ...)
        :param sort_key_type: 'N' | 'S'
        :return:
        """
        raise NotImplementedError

    def db_get_items_in_partition(self, partition, order_by='creation_date', order_min=None, order_max=None,
                                  start_key=None, limit=None, reverse=False,
                                  sort_min=None, sort_max=None):
        """
        :param partition:
        :param order_by:
        :param order_min:
        :param order_max:
        :param start_key:
        :param limit:
        :param reverse:
        :param sort_min:
        :param sort_max:
        :return:
        """
        raise NotImplementedError

    def db_put_item(self, partition, item, item_id=None, creation_date=None, index_keys=None):
        """This is connected with db_get_count"""
        raise NotImplementedError

    def db_update_item(self, item_id, item, index_keys=None):
        raise NotImplementedError

    def db_get_count(self, partition, field=None, value=None):
        raise NotImplementedError

    def db_get_item_id_and_orders(self, partition, field, value,
                                  order_by='creation_date', order_min=None, order_max=None,
                                  start_key=None, limit=100, reverse=False,
                                  sort_min=None, sort_max=None):
        """
        item_id 와 order 필드 값들을 빠르게 가져와야함
        :param partition: 대상을 가져올 파티션
        :param field: 필드
        :param value: 값
        :param order_by: 이 필드를 기준으로 reverse 에 따라 오름/내림차순 정렬
        :param order_min: order_by 가 이 값 이상인 아이템만 반환하고 Endkey 도 그에따라 반환
        :param order_max: order_by 가 이 값 이하인 아이템만 반환하고 Endkey 도 그에따라 반환
        :param start_key: 탐색 시작점
        :param limit: 반환되는 아이템 리스트 길이
        :param reverse: False 면 오름차순, True 면 내림차순
        :param sort_min:
        :param sort_max:
        :return: [{'item_id' : str, order_field: str}, ...]
        """
        raise NotImplementedError

    # File ops
    def file_download_bin(self, file_id):
        raise NotImplementedError

    def file_upload_bin(self, file_id, binary):
        raise NotImplementedError

    def file_delete_bin(self, file_id):
        raise NotImplementedError

    # SHOULD NOT RE-IMPLEMENT
    def db_query(self, partition, instructions=None, start_key=None, limit=100, reverse=False, order_by='creation_date',
                 index_keys=None):
        """:return:items:list,end_key:str"""
        # TODO 상위레이어에서 쿼리를 순차적으로 실행가능한 instructions 으로 만들어 전달 -> ORM 클래스 만들기
        if instructions and instructions[0]:
            if isinstance(instructions[0], tuple) and instructions[0][0] == 'and':
                instructions[0] = (None, (instructions[0][1][0], instructions[0][1][1], instructions[0][1][2]))
            elif isinstance(instructions[0], dict) and instructions[0].get('option', None) == 'and':
                instructions[0]['option'] = None
            elif isinstance(instructions[0], list) and instructions[0][0] == 'and':
                instructions[0][0] = None
        else:
            instructions = [{'field': 'partition', 'value': partition, 'condition': 'eq', 'option': None}]

        def get_items(_start_key_list, _sub_limit):
            if not _start_key_list:
                _start_key_list = [None] * len(instructions)
            _end_key_list = [None] * len(instructions)
            item_set = set()
            order_min = None
            order_max = None
            for idx, option_statement in enumerate(instructions):
                if isinstance(option_statement, list):
                    option = option_statement[0]
                    statement = (option_statement[1], option_statement[2], option_statement[3])
                elif isinstance(option_statement, tuple):
                    (option, statement) = option_statement
                elif isinstance(option_statement, dict):
                    option = option_statement.get('option', None)
                    statement = (option_statement['field'], option_statement['condition'], option_statement['value'])
                else:
                    raise BaseException('Unknown instruction type')

                instruction_type = self._db_instruction_type(idx, statement, option, index_keys=index_keys)
                if instruction_type == 'index':
                    if option == 'and':
                        pairs, _end_key_list[idx] = self._db_index_items(statement, partition, order_by, order_min,
                                                                         order_max, _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None:
                            if reverse and pairs:
                                order_min = pairs[-1][order_by]
                            elif pairs:
                                order_max = pairs[-1][order_by]
                        if idx == 0:
                            # 0번째 inst. option 이 and 이면 무시
                            item_set = set(pairs)
                        item_set &= set(pairs)

                    elif option == 'or' or option is None:
                        pairs, _end_key_list[idx] = self._db_index_items(statement, partition, order_by, order_min,
                                                                         order_max, _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None:
                            if reverse and pairs:
                                order_min = pairs[-1][order_by]
                            elif pairs:
                                order_max = pairs[-1][order_by]
                        item_set |= set(pairs)

                elif instruction_type == 'filter':
                    if option == 'and':
                        item_set = set(self._db_filter_items(statement, item_set))
                    elif option == 'or' or option is None:
                        raise BaseException('You cannot use option [or] on filtering')
                elif instruction_type == 'scan':
                    if option == 'and':
                        pairs, _end_key_list[idx] = self._db_scan_items(statement, partition, order_by, order_min, order_max,
                                                                        _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None:
                            if reverse and pairs:
                                order_min = pairs[-1][order_by]
                            elif pairs:
                                order_max = pairs[-1][order_by]
                        pairs = [IDDict(item) for item in self._db_filter_items(statement, pairs)]
                        item_set &= set(pairs)
                    elif option == 'or' or option is None:
                        pairs, _end_key_list[idx] = self._db_scan_items(statement, partition, order_by, order_min, order_max,
                                                                        _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None:
                            if reverse and pairs:
                                order_min = pairs[-1][order_by]
                            elif pairs:
                                order_max = pairs[-1][order_by]
                        pairs = [IDDict(item) for item in self._db_filter_items(statement, pairs)]
                        item_set |= set(pairs)
            item_set = list(item_set)
            item_set = sorted(item_set, key=lambda x: (x[order_by], x['id']), reverse=reverse)
            return item_set, _end_key_list

        if start_key:
            start_key_list = start_key.get('key_list', None)
            start_item_id = start_key.get('last_item_id', None)
        else:
            start_key_list = None
            start_item_id = None

        sub_limit = 500
        if not limit:
            limit = 100

        ct = time.time()

        all_items = []
        start_index = 0
        while True:
            # 탐색
            items, end_key_list = get_items(start_key_list, sub_limit)

            # 첫번째 아이템 인덱스 구하기
            if start_item_id:
                for idx, item in enumerate(items):
                    item_id = item['id']
                    if item_id == start_item_id:
                        start_index = idx + 1
                        break

            # 아이템 추가
            all_items.extend(items)
            no_more_end_key = all([(end_key is None) or (end_key is False) for end_key in end_key_list])
            if no_more_end_key:
                break
            split_count = len(all_items[start_index: start_index + limit])
            if split_count >= limit:
                break
            start_key_list = end_key_list

        all_items = list(set(all_items))
        all_items = sorted(all_items, key=lambda x: (x[order_by], x['id']), reverse=reverse)

        if len(all_items) > start_index + limit:
            no_more_items = False
        else:
            no_more_items = True
            start_key_list = end_key_list

        all_items = all_items[start_index: start_index + limit]
        all_items = self._db_batch_fake_items_to_real(all_items)
        all_items = sorted(all_items, key=lambda x: (x[order_by], x['id']), reverse=reverse)
        if no_more_end_key and no_more_items:
            end_key_set = None
        else:
            last_item_id = None
            if all_items:
                last_item_id = all_items[-1]['id']
            end_key_set = {'key_list': start_key_list, 'last_item_id': last_item_id}
        print('end_time:', time.time() - ct)
        return list(all_items), end_key_set

    # DB
    def _db_instruction_type(self, idx, statement, option, index_keys=None):
        def can_index(_field):
            if isinstance(index_keys, list) and _field not in index_keys:
                return False
            return True

        field, condition, value = statement
        if option == 'and':
            if condition == 'eq' and can_index(field):
                if idx == 0:
                    return 'index'
                else:
                    return 'filter'
            else:
                return 'filter'
        elif option == 'or':
            if condition == 'eq' and can_index(field):
                return 'index'
            else:
                return 'scan'
        elif option is None:
            if condition == 'eq' and can_index(field):
                return 'index'
            else:
                return 'scan'
        else:
            raise BaseException('No such option : [{}]'.format(option))

    def _db_get_fake_item(self, item, order_by):
        return IDDict({
            'id': item['item_id'],
            order_by: item[order_by],
            '_is_fake': True
        })

    def _db_batch_fake_items_to_real(self, items):
        bulk_size = 100
        item_ids = [item['id'] for item in items if '_is_fake' in item]
        items = [item for item in items if '_is_fake' not in item]
        with ThreadPoolExecutor(max_workers=32) as exc:
            for i in range(0, len(item_ids), bulk_size):
                def get_bulk(start, end):
                    items.extend(self.db_get_items(item_ids[start:end]))
                exc.submit(get_bulk, i, i + bulk_size)
        return [IDDict(item) for item in items]

    def _db_index_items(self, statement, partition, order_by, order_min, order_max, start_key, limit, reverse):
        if start_key is False:
            # 이미 탐색이 끝난 경우에 대해 탐색하지 않고 빈 리스트 반환
            return [], False
        field, condition, value = statement
        sort_min, sort_max = None, None
        if condition in ['gt', 'ge', 'ls', 'le'] and field == order_by:
            if condition in ['gt', 'ge']:
                sort_min = value
            if condition in ['ls', 'le']:
                sort_max = value
        elif condition != 'eq':
            raise BaseException('You cannot use condition : [{}] for indexing'.format(condition))
        pairs, end_key = self.db_get_item_id_and_orders(partition, field, value,
                                                        order_by, order_min, order_max, start_key, limit, reverse,
                                                        sort_min, sort_max)
        pairs = [IDDict(self._db_get_fake_item(pair, order_by)) for pair in pairs]
        if not end_key:
            # 탐색이 완전히 끝났음을 알려줌
            end_key = False
        return pairs, end_key

    def _db_scan_items(self, statement, partition, order_by, order_min, order_max, start_key, limit, reverse):
        if start_key is False:
            # 이미 탐색이 끝난 경우에 대해 탐색하지 않고 빈 리스트 반환
            return [], False
        field, condition, value = statement
        sort_min, sort_max = None, None
        if condition in ['gt', 'ge', 'ls', 'le'] and field == order_by:
            if condition in ['gt', 'ge']:
                sort_min = value
            if condition in ['ls', 'le']:
                sort_max = value
        items, end_key = self.db_get_items_in_partition(partition, order_by, order_min, order_max,
                                                        start_key, limit, reverse,
                                                        sort_min, sort_max)

        if not end_key:
            # 탐색이 완전히 끝났음을 알려줌
            end_key = False
        return items, end_key

    def _db_filter_items(self, statement, items):
        field, condition, value = statement
        items = self._db_batch_fake_items_to_real(items)
        for item in items:
            if '.' in field:
                item_value = item
                for key in field.split('.'):
                    if item_value is not None:
                        item_value = item_value.get(key, None)
            else:
                item_value = item.get(field, None)
            if condition == 'eq':
                if value == item_value:
                    yield item
            elif condition == 'neq':
                if value != item_value:
                    yield item
            elif condition == 'in':
                if item_value and isinstance(item_value, Iterable) and value in item_value:
                    yield item
            elif condition == 'nin':
                if item_value and value not in item_value:
                    yield item
            elif condition == 'gt':
                if isinstance(item_value, str):
                    if str(value) < str(item_value):
                        yield item
                else:
                    if item_value is not None and value is not None and float(value) < float(item_value):
                        yield item
            elif condition == 'ls':
                if isinstance(item_value, str):
                    if str(value) > str(item_value):
                        yield item
                else:
                    if item_value is not None and value is not None and float(value) > float(item_value):
                        yield item
            elif condition == 'ge':
                if isinstance(item_value, str):
                    if str(value) <= str(item_value):
                        yield item
                else:
                    if item_value is not None and value is not None and float(value) <= float(item_value):
                        yield item
            elif condition == 'le':
                if isinstance(item_value, str):
                    if str(value) >= str(item_value):
                        yield item
                else:
                    if item_value is not None and value is not None and float(value) >= float(item_value):
                        yield item
            else:
                raise BaseException('No such condition : [{}]'.format(condition))

    # Event scheduling
    def ev_put_schedule(self, schedule_name, cron_exp, params):
        raise NotImplementedError

    def ev_delete_schedule(self, schedule_name):
        raise NotImplementedError

    def sms_send_message(self, phone_number, message):
        raise NotImplementedError
