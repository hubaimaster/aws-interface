from dashboard.tests.test_dashboard import *


class LogicTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _click_create_function(self):
        """
        Click create function button
        :return:
        """
        self.parent.browser.find_element_by_css_selector('a[data-target="#modal-create-function"]').click()
        print("Clicked create function button")

    def _set_function(self, function_name, function_runtime, function_desc, function_file, function_handler):
        """
        Set function with function_name, function_runtime, function_desc, function_file, function_handler
        :param function_name: name of function
        :param function_runtime: runtime of function
        :param function_desc: description of function
        :param function_file: zipfile path of function
        :param function_handler: path and method of function to execute. in a format of path.method
        :return:
        """
        self.parent.browser.find_element_by_id('function-name').send_keys(function_name)
        time.sleep(DELAY)
        select_box = select.Select(self.parent.browser.find_element_by_id('function-runtime'))
        select_box.select_by_value(function_runtime.lower())
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('function-description').send_keys(function_desc)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('function-zipfile').send_keys(function_file)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('function-handler').send_keys(function_handler)
        print("Function is set with [{}], [{}], [{}], [{}]".format(function_name, function_runtime, function_desc, function_file, function_handler))

    def _accept_and_has_function(self, function_name):
        """
        Click accept button and check if [function_name] exists in function table
        :param function_name: name of function to check
        :return: bool
        """
        self.parent.browser.find_element_by_id('create-function').click()
        print("Accept button clicked")
        time.sleep(LONG_DELAY * 2)
        return self._has_function(function_name)

    def _has_function(self, function_name):
        """
        Check if [function_name] exists in function table
        :param function_name: name of function to check
        :return: bool
        """
        function_table = self.parent.browser.find_elements_by_tag_name('table')[1]
        for tr in function_table.find_elements_by_tag_name('tr')[1:]:
            if tr.find_element_by_tag_name('th').text.strip() == function_name:
                print("[{}] exists".format(function_name))
                return True
        return False

    def _remove_function(self, function_name):
        """
        Remove function [fucntion_name] from function table
        :param function_name: name of function to remove
        :return:
        """
        function_modal = self.parent.browser.find_elements_by_tag_name('tbody')[1]
        th = None
        for th in function_modal.find_elements_by_tag_name('th'):
            if th.text.strip() == function_name:
                print("{} is found".format(th.text.strip()))
                break
        row = th.find_element_by_xpath('..')
        row.find_element_by_tag_name('form').click()
        print("Removed [{}] from function table".format(function_name))

    def _click_create_testcase(self):
        """
        Click create-testcase button and check if create-function-test modal is open
        :return: bool
        """
        self.parent.browser.find_element_by_css_selector('a[data-target="#modal-create-function-test"]').click()
        time.sleep(DELAY)
        testcase_modal = self.parent.browser.find_element_by_id('modal-create-function-test')
        for style in testcase_modal.get_attribute('style').split(';'):
            if style.strip() == 'display: block':
                print("Testcase modal is opened")
                return True
        print("Testcase modal is not opened")
        return False

    def _set_testcase(self, testcase_name, testcase_function, testcase_pageload):
        """
        Fill modal with [testcase_name], [testcase_function], [testcase_pageload] and close the modal
        :param testcase_name: name of testcase
        :param testcase_function: name of function that would be run with testcase
        :param testcase_pageload: pageload of testcase
        :return:
        """
        testcase_modal = self.parent.browser.find_element_by_id('modal-create-function-test')
        testcase_modal.find_element_by_name('test_name').send_keys(testcase_name)
        time.sleep(DELAY)
        select_box = select.Select(testcase_modal.parent.find_element_by_name('function_name'))
        select_box.select_by_value(testcase_function)
        time.sleep(DELAY)
        testcase_modal.find_element_by_id('test_input').send_keys(testcase_pageload)
        time.sleep(DELAY)
        testcase_modal.find_element_by_id('create-function-test').click()
        print("Set testcase with [{}], [{}], [{}]".format(testcase_name, testcase_function, testcase_pageload))

    def _remove_testcase(self, testcase_name):
        """
        Remove testcase [testcase_name] from testcase table.
        :param testcase_name: name of testcase to remove
        :return:
        """
        testcase_modal = self.parent.browser.find_element_by_tag_name('tbody')
        th = None
        for th in testcase_modal.find_elements_by_tag_name('th'):
            if th.text.strip() == testcase_name:
                print("{} is found".format(th.text.strip()))
                break
        row = th.find_element_by_xpath('..')
        row.find_element_by_tag_name('form').click()
        print("Removed [{}] from testcase table".format(testcase_name))

    def _has_testcase(self, testcase_name):
        testcase_table = self.parent.browser.find_element_by_tag_name('tbody')
        for th in testcase_table.find_elements_by_tag_name('th'):
            if th.text.strip() == testcase_name:
                print("[{}] exists".format(testcase_name))
                return True
        return False

    def _open_test_result(self, testcase_name):
        """
        Click run_function and open test result modal. Check if modal is open
        :param testcase_name: name of testcase to run
        :return: bool
        """
        testcase_table = self.parent.browser.find_element_by_tag_name('tbody')
        tr = None
        for tr in testcase_table.find_elements_by_tag_name('tr'):
            if tr.find_element_by_tag_name('th').text.strip() == testcase_name:
                break
        tr.find_element_by_tag_name('button').click()
        print("Clicked run function")
        self.parent.wait_overlay()
        test_result = self.parent.browser.find_element_by_id('modal-test-result')
        for style in test_result.get_attribute('style').split(';'):
            if style.strip() == 'display: block':
                print("Test result modal is open")
                return True
        return False

    # Not implemented yet
    def _get_test_result(self):
        """
        Return the text of modal-test-result
        :return: str type. text on test result modal
        """
        #print(self.parent.browser.page_source)
        test_result_modal = self.parent.browser.find_element_by_id('modal-test-result')
        test_result_modal.find_element_by_tag_name('button').click()

    def _click_test_function(self, test_function):
        """
        Click name of function to move to function info page.
        :param test_function: name of function to click
        :return:
        """
        function_table = self.parent.browser.find_elements_by_tag_name('tbody')[1]
        for th in function_table.find_elements_by_tag_name('th'):
            if th.text.strip() == test_function:
                print("[{}] is clicked".format(test_function))
                th.click()
                break

    def _get_function_url(self, test_function):
        """
        Return url of function info page.
        :param test_function:
        :return:
        """
        print("moved to url : {}".format(self.parent.browser.current_url))
        return self.parent.browser.current_url

    def _get_function_name(self):
        """
        Return function_name
        :return: value of element with id 'function-name'
        """
        return self.parent.browser.find_element_by_id('function-name').get_attribute('value')

    def _get_function_description(self):
        """
        Return function_description
        :return: value of element with id 'function-description'
        """
        return self.parent.browser.find_element_by_id('function-description').get_attribute('value')

    def _get_function_runtime(self):
        """
        Return function_runtime
        :return: value of element with id 'function-runtime'
        """
        select_box = select.Select(self.parent.browser.find_element_by_id('function-runtime'))
        return select_box.first_selected_option.get_attribute('value')

    def _get_function_handler(self):
        """
        Return function_handler
        :return: value of element with id 'function-handler'
        """
        return self.parent.browser.find_element_by_id('function-handler').get_attribute('value')

    def _edit_function_description(self, new_desc):
        """
        Edit function_description to [new_desc]
        :return:
        """
        desc_field = self.parent.browser.find_element_by_id('function-description')
        desc_field.clear()
        desc_field.send_keys(new_desc)
        time.sleep(DELAY)
        print("Edited function description to [{}]".format(new_desc))

    def _save_function_info(self):
        """
        click save button of function info, and accept button on alert
        :return:
        """
        self.parent.browser.find_element_by_css_selector('span[onclick="save_function_info();"]').click()
        time.sleep(LONG_DELAY)
        self.parent.browser.switch_to.alert.accept()
        time.sleep(DELAY)
        self.parent.browser.refresh()
        time.sleep(LONG_DELAY)
        print("Clicked save function info")

    def _clear_function_file(self):
        """
        Clear function file(test.py)
        :return:
        """
        ace_script = "editor.setValue('',-1);"
        self.parent.browser.execute_script(ace_script)
        print("Cleared function file")

    def _save_function_file(self):
        """
        Click save button on fuction file, and accept button on alert
        :return:
        """
        self.parent.browser.find_element_by_css_selector('a[onclick="save_current_file();"]').click()
        time.sleep(LONG_DELAY)
        self.parent.browser.switch_to.alert.accept()
        time.sleep(DELAY)
        self.parent.browser.refresh()
        time.sleep(LONG_DELAY)
        print("clicked save function file")

    def _get_function_file(self):
        """
        Get code on function file(test.py)/ace editor
        :return: str type. text in function file.
        """
        ace_script = "editor.getValue();"
        function_file = self.parent.browser.execute_script(ace_script)
        print(function_file)
        return function_file

    def _return_to_logic_module(self):
        """
        Click 'LOGIC' on navigation bar to move to logic module.
        :return:
        """
        self.parent.browser.find_element_by_id('link-logic').click()
        print("Returned to logic module")
        time.sleep(LONG_DELAY * 2)

    def do_test(self):
        FUNCTION_NAME = 'test-function'
        FUNCTION_RUNTIME = 'Python3.6'
        FUNCTION_DESC = 'test-description'
        FUNCTION_DESC_NEW = 'test-description-mod2'
        FUNCTION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(settings.__file__)))
        FUNCTION_FILE = 'test.zip'
        FUNCTION_FILE = os.path.join(FUNCTION_DIR, FUNCTION_FILE)
        FUNCTION_HANDLER = 'test.handler'
        FUNCTION_URL = '/logic/{}'.format(FUNCTION_NAME)
        TESTCASE_NAME = 'test-case'
        TESTCASE_FUNCTION = 'test-function'
        TESTCASE_PAGELOAD = '{"answer": 10}'

        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-logic').click()
        time.sleep(LONG_DELAY)
        while True:
            try:
                if self.parent.get_view_tag() == 'logic':
                    break
                self.parent.browser.refresh()
                time.sleep(LONG_DELAY * 4)
                print('Wait...')
            except StaleElementReferenceException:
                pass
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('logic')
        time.sleep(DELAY)
        self._click_create_function()
        time.sleep(LONG_DELAY)
        self._set_function(FUNCTION_NAME, FUNCTION_RUNTIME, FUNCTION_DESC, FUNCTION_FILE, FUNCTION_HANDLER)
        time.sleep(DELAY)
        self.parent.assertTrue(self._accept_and_has_function(FUNCTION_NAME))
        time.sleep(DELAY)
        self._click_create_testcase()
        time.sleep(DELAY)
        self._set_testcase(TESTCASE_NAME, TESTCASE_FUNCTION, TESTCASE_PAGELOAD)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertTrue(self._has_testcase(TESTCASE_NAME))
        time.sleep(DELAY)
        self._open_test_result(TESTCASE_NAME)
        time.sleep(LONG_DELAY)
        # _get_test_result is not implemented yet!
        self._get_test_result()
        #self.parent.assertTrue(self._get_test_result(TESTCASE_FUNCTION, TESTCASE_PAGELOAD)['response'])
        time.sleep(LONG_DELAY)
        self._click_test_function(FUNCTION_NAME)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._get_function_url(FUNCTION_NAME).endswith(FUNCTION_URL))
        time.sleep(DELAY)
        self.parent.assertTrue(self._get_function_name() == FUNCTION_NAME)
        time.sleep(DELAY)
        self.parent.assertTrue(self._get_function_runtime() == FUNCTION_RUNTIME.lower())
        time.sleep(DELAY)
        self.parent.assertTrue(self._get_function_description() == FUNCTION_DESC)
        time.sleep(DELAY)
        self.parent.assertTrue(self._get_function_handler() == FUNCTION_HANDLER)
        time.sleep(DELAY)
        self._edit_function_description(FUNCTION_DESC_NEW)
        time.sleep(DELAY)
        self._save_function_info()
        time.sleep(LONG_DELAY * 2)
        self.parent.assertTrue(self._get_function_description() == FUNCTION_DESC_NEW)
        time.sleep(DELAY)
        self._clear_function_file()
        time.sleep(DELAY)
        self._save_function_file()
        time.sleep(DELAY)
        self.parent.assertTrue(self._get_function_file() == None)
        time.sleep(DELAY)
        self._return_to_logic_module()
        time.sleep(LONG_DELAY * 2)
        self._open_test_result(TESTCASE_FUNCTION)
        time.sleep(DELAY)
        # _get_test_result is not implemented yet!
        self._get_test_result()
        # self.parent.assertTrue(self._get_test_result(TESTCASE_FUNCTION, TESTCASE_PAGELOAD)['error'])
        time.sleep(LONG_DELAY)
        self._remove_testcase(TESTCASE_NAME)
        time.sleep(LONG_DELAY)
        self.parent.assertFalse(self._has_testcase(TESTCASE_NAME))
        time.sleep(LONG_DELAY * 2)
        self._remove_function(FUNCTION_NAME)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertFalse(self._has_function(FUNCTION_NAME))