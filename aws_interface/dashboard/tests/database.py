from dashboard.tests.test_dashboard import *
import sys

class DatabaseTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _create_partition(self, partition):
        """
        Create partition with name [partition]
        :param partition: name of partition
        :return:
        """
        self.parent.browser.find_element_by_id('create-partition-button').click()
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('partition-name').send_keys(partition)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('add-partition-btn').click()

    def _has_partition(self, partition):
        """
        Check if partition with name [partition] exists.
        :param partition:
        :return: bool
        """
        partition_obj = self.parent.browser.find_element_by_id('partition-{}'.format(partition))
        return partition_obj
    def _select_parition_and_mode_in_policy_function(self, partition_name, mode):
        """
        Select [parition_name] and [mode] in policy function
        :param partition_name:
        :param mode:
        :return:
        """
        partition_select_box = select.Select(self.parent.browser.find_element_by_id('policy-partition-to-apply'))
        partition_select_box.select_by_value(partition_name)
        mode_select_box = select.Select(self.parent.browser.find_element_by_id('policy-mode'))
        mode_select_box.select_by_value(mode)
        print("{} and {} selected".format(partition_name, mode))

    def _write_policy_function(self, code):
        """
        Write [code] in policy_function
        :param code: code to write in policy_function
        :return:
        """
        remove_code = """
                    var element = arguments[0];
                    element.parentNode.removeChild(element);
                    """
        add_code = """
                var element = arguments[0];
                var div = document.createElement( 'div' );
                div.innerHTML='{}';
                element.appendChild( div );
                """
        policy_function = self.parent.browser.find_element_by_id('code-editor')
        policy_function = policy_function.find_element_by_css_selector('div[class="ace_layer ace_text-layer"')
        for div in policy_function.find_elements_by_tag_name('div'):
            self.parent.browser.execute_script(remove_code, div)
        try:
            for line in code.split('\n'):
                self.parent.browser.execute_script(add_code.format(line), policy_function)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print("Code not written")
            return
        print("Wrote code")

    def _click_save_button(self):
        """
        Click save_button in policy_function
        :return:
        """
        self.parent.browser.find_element_by_css_selector('button[onclick="save_policy();"]').click()
        time.sleep(DELAY)
        self.parent.browser.switch_to.alert.accept()
        print("save button clicked")

    def _has_code_in_policy_function(self, code):
        """
        Check if [code] exists in policy function
        :param code: code to check existence
        :return:
        """
        self.parent.browser.refresh()
        policy_function = self.parent.browser.find_element_by_id('code-editor')
        policy_function = policy_function.find_element_by_css_selector('div[class="ace_layer ace_text-layer"')
        print(policy_function.text)
        written_function = [line.strip() for line in policy_function.text.split()]
        code_list = [line.strip() for line in code.split()]
        for i in range(len(code_list)):
            if written_function[i] != code_list[i]:
                return False
        return False

    def _open_add_item_modal(self, partition_name):
        """
        Click parition [partition_name] and open item + modal
        :param partition_name: name of partition that checkbox should be checked
        :return:
        """
        self.parent.browser.find_element_by_id('{}'.format(partition_name)).click()
        time.sleep(LONG_DELAY)
        self.parent.browser.find_element_by_id("open-add-item-modal").click()
        time.sleep(DELAY)
        add_item_modal = self.parent.browser.find_element_by_id('modal-add-item')
        for style in add_item_modal.get_attribute('style').split(';'):
            if style.strip() == 'display: block':
                print("add item modal open checked")
                return True
        return False

    def do_test(self):
        PARTITION_NAME = 'test'
        MODE = 'update'
        CODE = """
            def has_permission(user, item):
                return False
            """

        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-database').click()
        time.sleep(LONG_DELAY)
        while True:
            try:
                if self.parent.get_view_tag() == 'database':
                    break
                self.parent.browser.refresh()
                time.sleep(LONG_DELAY * 4)
                print('Wait...')
            except StaleElementReferenceException as e:
                print(e)
                pass
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('database')
        time.sleep(LONG_DELAY)
        self._create_partition(PARTITION_NAME)
        time.sleep(LONG_DELAY * 4)
        self.parent.assertTrue(self._has_partition(PARTITION_NAME))
        time.sleep(DELAY)
        self._select_parition_and_mode_in_policy_function(PARTITION_NAME, MODE)
        time.sleep(DELAY)
        #self._write_policy_function(CODE)
        time.sleep(LONG_DELAY)
        self._click_save_button()
        time.sleep(LONG_DELAY)
        #self.parent.assertTrue(self._has_code_in_policy_function(CODE))
        time.sleep(DELAY)
        self.parent.assertTrue(self._open_add_item_modal(PARTITION_NAME))
