from dashboard.tests.test_dashboard import *


class DatabaseTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _create_partition(self, partition):
        self.parent.browser.find_element_by_id('create-partition-button').click()
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('partition-name').send_keys(partition)
        self.parent.browser.find_element_by_id('add-partition-btn').click()

    def _has_partition(self, partition):
        partition_obj = self.parent.browser.find_element_by_id('partition-{}'.format(partition))
        if partition_obj:
            return True
        else:
            return False

    def do_test(self):
        PARTITION_NAME = 'test'
        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-database').click()
        time.sleep(LONG_DELAY)
        while self.parent.get_view_tag() != 'database':
            self.parent.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('database')
        time.sleep(LONG_DELAY)
        self._create_partition(PARTITION_NAME)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_partition(PARTITION_NAME))
        time.sleep(DELAY)