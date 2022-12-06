from abc import ABCMeta
from concurrent.futures import ThreadPoolExecutor
import time
import json
import copy
from collections.abc import Iterable
from resource.config import MAX_N_GRAM


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

    def db_get_partitions(self):
        raise NotImplementedError

    def db_delete_partition(self, partition):
        raise NotImplementedError

    def db_delete_item(self, item_id):
        raise NotImplementedError

    def db_delete_item_batch(self, item_ids):
        raise NotImplementedError

    def db_get_item(self, item_id, projection_keys=None):
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

    def db_put_item(self, partition, item, item_id=None, creation_date=None, index_keys=None, sort_keys=None):
        """It connects with db_get_count"""
        raise NotImplementedError

    def db_update_item(self, item_id, item, index_keys=None, sort_keys=None):
        raise NotImplementedError

    def db_update_item_v2(self, item_id, item, index_keys=None, sort_keys=None):
        raise NotImplementedError

    def db_get_count(self, partition, field=None, value=None):
        raise NotImplementedError

    def db_get_item_id_and_orders(self, partition, field, value,
                                  order_by='creation_date', order_min=None, order_max=None,
                                  start_key=None, limit=100, reverse=False,
                                  sort_min=None, sort_max=None, operation='eq'):
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
        :param operation:
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
            if isinstance(instructions[0], tuple):# and instructions[0][0] == 'and':
                instructions[0] = (None, (instructions[0][1][0], instructions[0][1][1], instructions[0][1][2]))
            elif isinstance(instructions[0], dict):# and instructions[0].get('option', None) == 'and':
                instructions[0]['option'] = None
            elif isinstance(instructions[0], list):# and instructions[0][0] == 'and':
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

                        if order_min is None and order_max is None and pairs:
                            if reverse:
                                order_min = pairs[-1].get(order_by, 0)
                            else:
                                order_max = pairs[-1].get(order_by, 0)
                        if idx == 0:
                            # 0번째 inst. option 이 and 이면 무시
                            item_set = set(pairs)
                        item_set &= set(pairs)

                    elif option == 'or' or option is None:
                        pairs, _end_key_list[idx] = self._db_index_items(statement, partition, order_by, order_min,
                                                                         order_max, _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None and pairs:
                            if reverse:
                                order_min = pairs[-1].get(order_by, 0)
                            else:
                                order_max = pairs[-1].get(order_by, 0)
                        # print('order_min:', order_min, 'order_max:', order_max, 'pairs:', pairs, '_end_key_list[{}]:'.format(idx), _end_key_list[idx])
                        item_set |= set(pairs)

                elif instruction_type == 'filter':
                    if option == 'and':
                        item_set &= set(self._db_filter_items(statement, item_set))
                    elif option == 'or' or option is None:
                        raise BaseException('You cannot use option [or] on filtering')
                elif instruction_type == 'scan':
                    if option == 'and':
                        pairs, _end_key_list[idx] = self._db_scan_items(statement, partition, order_by, order_min, order_max,
                                                                        _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None and pairs:
                            if reverse:
                                order_min = pairs[-1].get(order_by, 0)
                            else:
                                order_max = pairs[-1].get(order_by, 0)
                        pairs = [IDDict(it) for it in self._db_filter_items(statement, pairs)]
                        item_set &= set(pairs)
                    elif option == 'or' or option is None:
                        pairs, _end_key_list[idx] = self._db_scan_items(statement, partition, order_by, order_min, order_max,
                                                                        _start_key_list[idx], _sub_limit, reverse)

                        if order_min is None and order_max is None and pairs:
                            if reverse:
                                order_min = pairs[-1].get(order_by, 0)
                            else:
                                order_max = pairs[-1].get(order_by, 0)
                        pairs = [IDDict(it) for it in self._db_filter_items(statement, pairs)]
                        item_set |= set(pairs)
            item_set = list(item_set)
            item_set = sorted(item_set, key=lambda x: (x.get(order_by, 0), x.get('id', 0)), reverse=reverse)
            return item_set, _end_key_list

        if start_key:
            start_key_list = start_key.get('key_list', None)
            start_item_id = start_key.get('last_item_id', None)
        else:
            start_key_list = None
            start_item_id = None

        if not limit:
            limit = 100
        sub_limit = min(limit * 1, 500)

        ct = time.time()

        all_items = []
        start_index = 0
        while True:
            # 탐색
            items, end_key_list = get_items(start_key_list, sub_limit)

            # 아이템 추가
            all_items.extend(items)

            # 첫번째 아이템 인덱스 구하기
            if start_item_id:
                for idx_item, item in enumerate(all_items):
                    item_id = item['id']
                    if item_id == start_item_id:
                        start_index = idx_item + 1
                        break

            no_more_end_key = all([(end_key is None) or (end_key is False) for end_key in end_key_list])
            if no_more_end_key:
                break
            split_count = len(all_items[start_index: start_index + limit])
            if split_count >= limit:
                break
            start_key_list = end_key_list

        all_items = list(set(all_items))
        all_items = sorted(all_items, key=lambda x: (x.get(order_by, 0), x.get('id', 0)), reverse=reverse)

        if len(all_items) > start_index + limit:
            no_more_items = False
        else:
            no_more_items = True
            start_key_list = end_key_list

        all_items = all_items[start_index: start_index + limit]
        all_items = self._db_batch_fake_items_to_real(all_items)
        all_items = sorted(all_items, key=lambda x: (x.get(order_by, 0), x.get('id', 0)), reverse=reverse)
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
        field, condition, value = statement

        def can_index(_field):
            has_key = False
            if isinstance(index_keys, list):
                for index_key in index_keys:
                    if isinstance(index_key, str) and index_key == _field and condition not in ['ins']:  # 일반 인덱싱
                        has_key = True
                    if isinstance(index_key, tuple) and index_key == (_field, condition):  # 고급 인덱싱 / 풀텍스트 등
                        has_key = True
                if not has_key:
                    return False
            elif condition in ['ins']:
                return False  # 고급 인덱싱은 인덱스 리스트에 포함되어있어야 인덱싱.
            return True

        index_operations = ['eq', 'ins']
        if option == 'and':
            if condition in index_operations and can_index(field):
                if idx == 0:
                    return 'index'
                else:
                    return 'filter'
            else:
                return 'filter'
        elif option == 'or':
            if condition in index_operations and can_index(field):
                return 'index'
            else:
                return 'scan'
        elif option is None:
            if condition in index_operations and can_index(field):
                return 'index'
            else:
                return 'scan'
        else:
            raise BaseException('No such option : [{}]'.format(option))

    def _db_get_fake_item(self, item, order_by):
        return IDDict({
            'id': item['item_id'],
            order_by: item.get(order_by, None),
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
        elif condition not in ['eq', 'ins']:
            raise BaseException('You cannot use condition : [{}] for indexing'.format(condition))
        if condition == 'ins' and isinstance(value, str):
            # ins 일 경우 ngram 토큰화
            value = value[:MAX_N_GRAM]
        pairs, end_key = self.db_get_item_id_and_orders(partition, field, value,
                                                        order_by, order_min, order_max, start_key, limit, reverse,
                                                        sort_min, sort_max, condition)
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
                if value == item_value or str(value) == str(item_value):
                    yield item
            elif condition == 'neq':
                if value != item_value and str(value) != str(item_value):
                    yield item
            elif condition == 'in':
                if item_value and isinstance(item_value, Iterable) and value in item_value:
                    yield item
            elif condition == 'ins':
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

    def function_update_memory_size(self, memory_size):
        raise NotImplementedError

    def function_delete_stand_alone_function(self, function_name):
        raise NotImplementedError

    def function_create_stand_alone_function(self, function_name, zipfile):
        """
        ExecuteStandAlone 로 실행 가능한 스탠드얼론 함수 생성.
        :param function_name:
        :param zipfile:
        :return:
        """
        raise NotImplementedError

    def function_update_stand_alone_function(self, function_name, zipfile):
        """
        ExecuteStandAlone 로 실행 가능한 스탠드얼론 함수 수정.
        :param function_name:
        :param zipfile:
        :return:
        """
        raise NotImplementedError

    def function_execute_stand_alone_function(self, function_name, request_body):
        """
        Lambda SDK 로 함수를 실행하고 응답을 반환합니다.
        :param function_name:
        :param request_body:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def fdb_item_id_to_pk_sk_pair(cls, item_id):
        """
        내부적으로 pk와 sk 조합을 item_id 로 부터 복호화합니다.
        :param item_id:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def fdb_pk_sk_to_item_id(cls, pk, sk):
        """
        pk 와 sk 를 item_id 로 암호화합니다.
        :param pk:
        :param sk:
        :return:
        """
        raise NotImplementedError

    # 새로 추가된 FastDatabase, Fully NoSQL
    def fdb_create_partition(self, partition, pk_group, pk_field, sk_group, sk_field=None,
                             post_sk_fields=None, use_random_sk_postfix=True):
        """
        Fast DB 내부에 파티션을 생성합니다. 사실 생성의 개념보다는 파티션을 선언합니다.
        파티션 삭제시에, 내부 데이터는 삭제 되지 않기 때문에 유의해야합니다.
        :param partition: order 등 파티션 이름
        :param pk_group: app, system 등 파티션 필드 앞에 구분자를 붙일 때 사용합니다. 한번 지정되면 바꿀 수 없습니다.
        같은 user_id 를 가진 엔티티여도 시스템에서 사용하느냐, 앱에서 사용하느냐에 따라 구분할 수 있습니다.
        일례로 로그 데이터 등은 system 에 보관하는것이 안전하고, 속도 측면에서도 유리합니다.
        :param pk_field: user_id 등을 pk_field 로 지정하는것이 유리합니다. 병렬 처리와 관련 있으며, 디버깅을 위해
        실제 DB의 pk 필드 (인덱스) 에는 <pk_group>#<pk_field>#<pk.value> 의 값이 들어갑니다.
        :param sk_group: sort key 앞에 붙는 그룹 구분입니다. sk = <sk_group>#<partition>#<sk_field>#<sk.value> 가 들어갑니다.
        이 값을 이용하여 같이 조인되어야 하는 값들을 효과적으로 조인할 수 있습니다. 예를 들면
        그룹 order 으로 묶이는 경우, order 으로 order_plan 이나 order 등 같이 묶여서 반환시 성능이 극대화 시킬 수 있습니다.
        :param sk_field: created_at 등.. 날짜로 구성하면 날짜별 정렬이 가능합니다.
        :param post_sk_fields: 소트키 뒤에 붙는 field 입니다. 임의로 데이터 중복 생성 방지 기능을 만드는데 유용합니다.
        :param use_random_sk_postfix: pk 와 sk 가 같으면 중복 생성이 불능하기 때문에, 랜덤 문자열을 붙여 다른 아이템으로
        생성할 수 있습니다.
        :return:
        """
        raise NotImplementedError

    def fdb_append_index(self, partition_name, pk_field, sk_field):
        """
        DB partition 에 인덱스를 추가합니다.
        TODO 일단 기본 기능 먼저 구현하고, 필요시에 인덱스 부분을 개발하도록 한다.
        :param partition_name:
        :param pk_field:
        :param sk_field:
        :return:
        """
        raise NotImplementedError

    def fdb_detach_index(self, partition_name, index_name):
        """
        DB partition 에 인덱스 제거
        :param partition_name:
        :param index_name:
        :return:
        """
        raise NotImplementedError

    def fdb_get_partitions(self, use_cache=False):
        """
        파티션 목록을 가져옵니다.
        :return:
        """
        raise NotImplementedError

    def fdb_delete_partition(self, partition):
        """
        파티션을 삭제, 내부 데이터는 별도로 삭제해야합니다.
        :param partition:
        :return:
        """
        raise NotImplementedError

    def fdb_put_items(self, partition, items):
        """
        배치 생성, 단건 생성도 이 API 를 통해 진행합니다.
        :param partition:
        :param items:
        :return:
        """
        raise NotImplementedError

    def fdb_put_item(self, partition, item):
        """
        생성
        :param partition:
        :param item:
        :return:
        """
        raise NotImplementedError

    def _fdb_put_item_low_level(self, _pk, _sk, item):
        """
        로우레벨단에서 DB Item 생성, 시스템에서 이용합니다.
        pk, sk 가 서비스단과 겹치면 곤란함.
        :param _pk:
        :param _sk:
        :param item:
        :return:
        """
        raise NotImplementedError

    def _fdb_get_item_low_level(self, _pk, _sk):
        """
        로우레벨단에서 DB Item get, 시스템에서 이용합니다.
        pk, sk 가 서비스단과 겹치면 안됨.
        :param _pk:
        :param _sk:
        :return:
        """
        raise NotImplementedError

    def fdb_get_items(self, item_ids, consistent_read=False):
        """
        item_ids 를 배치로 쿼리하여 가져옵니다.
        :param item_ids:
        :param consistent_read:
        :return:
        """
        raise NotImplementedError

    def fdb_query_items(self, pk_field, pk_value, sort_condition=None,
                        partition='', sk_field='', sk_value=' ', sk_second_value=None, filters=None,
                        start_key=None, limit=100, reverse=False, consistent_read=False, index_name=None,
                        pk_name='_pk', sk_name='_sk'):
        """
        DB 를 쿼리하고, 이는 NoSQL 최적화 되어 있습니다.
        단계별로 pk 관련 키들은 쿼리에 필수이며,
        sk 관련 키들은 단계별로 아이템 쿼리를 진행할 수 있도록 도와줍니다.
        partition 을 넘겨야, sk_value 를 입력할 수 있기 때문에,
        sk_field 를 파티션을 통해 구할 수 있습니다.
        :param pk_field:
        :param pk_value:
        :param sort_condition:
        :param partition:
        :param sk_field:
        :param sk_value:
        :param sk_second_value:
        :param filters:
        :param start_key:
        :param limit:
        :param reverse:
        :param consistent_read:
        :param index_name: 없을시 기본 파라메터로 쿼리
        :param pk_name:
        :param sk_name:
        :return:
        """
        raise NotImplementedError

    def fdb_delete_items(self, item_ids):
        """
        배치 삭제, 여러개를 한번에 삭제하고, 단건 삭제도 이 API 를 통해 진행합니다.
        :param item_ids:
        :return:
        """
        raise NotImplementedError

    def fdb_has_pk_sk_by_item(self, partition, item):
        """
        item 의 pk-sk 조합이 이미 DB에 존재하는지 확인, create 확인용으로 주로 사용
        :param partition:
        :param item:
        :return:
        """
        raise NotImplementedError

    def fdb_update_item(self, partition, item_id, item):
        """
        업데이트
        :param partition:
        :param item_id:
        :param item:
        :return:
        """
        raise NotImplementedError
