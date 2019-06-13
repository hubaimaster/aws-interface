from dashboard.tests.test_dashboard import *


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
        if partition_obj:
            return True
        else:
            return False

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
                var sp_text = document.createTextNode('{}');
                element.appendChild( sp_text );
                """
        policy_function = self.parent.browser.find_element_by_id('code-editor')
        policy_function = policy_function.find_element_by_css_selector('div[class="ace_layer ace_text-layer"')
        for div in policy_function.find_elements_by_tag_name('div'):
            self.parent.browser.execute_script(remove_code, div)
        try:
            self.parent.browser.execute_script(add_code.format(code), policy_function)
            print(self.parent.browser.find_element_by_css_selector('div[class="ace_layer ace_text-layer"').text)
        except:
            try :
                print("error occured when writing code 111")
                print(self.parent.browser.find_element_by_css_selector('div[class="ace_content"').text)
                policy_function = self.parent.browser.find_element_by_css_selector('div[class="ace_content"')
                self.parent.browser.execute_script(add_code.format(code), policy_function)
            except:
                print("error occured when writing code 222")
                time.sleep(LONG_DELAY * 4)
        print("Wrote code")

    def _click_save_button(self):
        """
        Click save_button in policy_function
        :return:
        """
        self.parent.browser.find_element_by_css_selector('button[onclick="save_policy();"]').click()
        time.sleep(DELAY)
        self.parent.browser.switch_to.alert.accept()
        print("save clicked")

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
        return policy_function.text == code

    def _open_add_item_modal(self, partition_name):
        """
        Check the checkbox of [partition_name] and open item+ modal
        :param partition_name: name of partition that checkbox should be checked
        :return:
        """
        checkbox = self.parent.browser.find_element_by_id("partition-{}".format(partition_name))
        self.parent.browser.execute_script("arguments[0].checked = true;", checkbox)
        print(str(checkbox.is_selected()))
        time.sleep(LONG_DELAY)
        self.parent.browser.find_element_by_id("open-add-item-modal").click()
        add_item_modal = self.parent.browser.find_element_by_id('modal-add-item')
        try :
            print(type(self.parent.assertTrue(add_item_modal.get_attribute('aria-hidden'))))
            self.parent.assertTrue(add_item_modal.get_attribute('aria-hidden'))
            print("it is returned as string")
        except :
            self.parent.assertTrue(add_item_modal.get_attribute('aria-hidden')=="true")
        print("added_item")

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
        while self.parent.get_view_tag() != 'database':
            self.parent.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
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
        self._write_policy_function(CODE)
        time.sleep(LONG_DELAY)
        self._click_save_button()
        time.sleep(LONG_DELAY)
        #self.parent.assertTrue(self._has_code_in_policy_function(CODE))
        time.sleep(LONG_DELAY * 4)
        self._open_add_item_modal(PARTITION_NAME)