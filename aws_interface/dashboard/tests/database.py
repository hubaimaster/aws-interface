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
        print("[{}] and [{}] selected".format(partition_name, mode))

    def _write_policy_function(self, code):
        """
        Write [code] in policy_function
        :param code: code to write in policy_function
        :return:
        """
        ace_script = "editor.setValue('{}',-1);".format(code)
        self.parent.browser.execute_script(ace_script)
        print("Wrote code")

    def _save_policy_function(self):
        """
        Click save button in policy_function
        :return:
        """
        self.parent.browser.find_element_by_css_selector('button[onclick="save_policy();"]').click()
        time.sleep(DELAY)
        self.parent.browser.switch_to.alert.accept()
        print("Save button clicked")

    def _has_code_in_policy_function(self, partition_name, mode, code):
        """
        Check if [code] exists in policy function
        :param code: code to check existence
        :return:
        """
        self.parent.browser.refresh()
        time.sleep(DELAY)
        self._select_parition_and_mode_in_policy_function(partition_name, mode)
        time.sleep(LONG_DELAY)
        policy_function = self.parent.browser.find_element_by_id('code-editor')
        policy_function = policy_function.find_element_by_css_selector('div[class="ace_layer ace_text-layer"]').text.strip()
        code = code.replace('\\n', ' ')
        code = code.replace('\\t', ' ')
        function_list = [line.strip() for line in policy_function.split()]
        code_list = [line.strip() for line in code.split()]
        print(function_list)
        print(code_list)
        for i in range(len(code_list)):
            if function_list[i] != code_list[i]:
                print("There is difference")
                return False
        return True

    def _open_add_item_modal(self, partition_name):
        """
        Click partiton [partition_name] and open item+ modal
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
                print("Checked item+ modal is open")
                return True
        return False

    def _remove_readable_user(self, user_name):
        """
        Remove [user_name] from readable users group
        :param user_name: name of user group to remove
        :return:
        """
        readable_users = self.parent.browser.find_element_by_id('read-groups')
        for user in readable_users.find_elements_by_tag_name('a'):
            if user.text.strip() == user_name:
                user.click()
                print("clicked [{}]".format(user_name))
                return

    def _has_readable_user(self, user_name):
        """
        Check if [user_name] exists in readable users group
        :param user_name: naem of user group to check
        :return:
        """
        readable_users = self.parent.browser.find_element_by_id('read-groups')
        for user in readable_users.find_elements_by_tag_name('a'):
            if user.text.strip() == user_name:
                print("has user [{}]".format(user_name))
                return True
        return False

    def _add_readable_user(self, user_name):
        """
        Add [user_name] to readable users group
        :param user_name: name of user group to add
        :return:
        """
        readable_users = self.parent.browser.find_element_by_id('read-groups')
        add_button = readable_users.find_element_by_xpath('..')
        add_button.find_element_by_id('dropdownMenuButton').click()
        for item in add_button.find_elements_by_css_selector('a[class="dropdown-item"]'):
            if item.text.strip().lower() == user_name:
                print("found [{}]".format(user_name))
                item.click()
                return

    def _click_accept_item(self):
        """
        Click accept button from item+ modal
        :return:
        """
        self.parent.browser.find_element_by_id('add-item-btn').click()
        print("Accept button clicked")

    def _get_item_count(self):
        """
        Return number of items
        :return:
        """
        item_count = self.parent.browser.find_element_by_id('item_count').text
        item_count = item_count.split('/')[-1].strip()
        return int(item_count)

    def _click_item_and_check_fields(self):
        """
        Click the top locating item and check if fields exist
        :return:
        """
        item_table = self.parent.browser.find_element_by_id('item-table')
        item_table.find_element_by_name('item').click()
        time.sleep(LONG_DELAY)

    def do_test(self):
        PARTITION_NAME = 'test'
        MODE = 'update'
        CODE = "def has_permission(user, item):\\n\\treturn False"
        USER_NAME = "user"

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
        self._write_policy_function(CODE)
        time.sleep(DELAY)
        self._save_policy_function()
        time.sleep(LONG_DELAY)
        self._has_code_in_policy_function(PARTITION_NAME, MODE, CODE)
        #self.parent.assertTrue(self._has_code_in_policy_function(PARTITION_NAME, MODE, CODE))
        time.sleep(DELAY)
        self.parent.assertTrue(self._open_add_item_modal(PARTITION_NAME))
        time.sleep(DELAY)
        self._remove_readable_user(USER_NAME)
        time.sleep(DELAY)
        self.parent.assertFalse(self._has_readable_user(USER_NAME))
        time.sleep(DELAY)
        self._add_readable_user(USER_NAME)
        time.sleep(DELAY)
        self.parent.assertTrue(self._has_readable_user(USER_NAME))
        time.sleep(DELAY)
        self._click_accept_item()
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._get_item_count() == 1)
        time.sleep(DELAY)