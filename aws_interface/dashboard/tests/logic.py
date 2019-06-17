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
        time.sleep(DELAY)
        self.parent.browser.find_elements_by_id('create-function')[1].click()
        print("Function is set with [{}], [{}], [{}], [{}]".format(function_name, function_runtime, function_desc, function_file, function_handler))

    def _click_and_check_function(self, function_name):
        """
        Check if [function_name] exists in function table
        :param function_name: name of function to check
        :return: bool
        """
        self.parent.browser.find_element_by_id('create-function').click()
        time.sleep(LONG_DELAY * 2)
        function_table = self.parent.browser.find_elements_by_tag_name('table')[1]
        for tr in function_table.find_elements_by_tag_name('tr')[1:]:
            if tr.find_element_by_tag_name('th').text.strip() == function_name:
                print("[{}] exists".format(function_name))
                return True
        return False


    def do_test(self):
        FUNCTION_NAME = 'test-function'
        FUNCTION_RUNTIME = 'Python3.6'
        FUNCTION_DESC = 'test-description'
        FUNCTION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(settings.__file__)))
        FUNCTION_FILE = 'test.zip'
        FUNCTION_FILE = os.path.join(FUNCTION_DIR, FUNCTION_FILE)
        FUNCTION_HANDLER = 'test.handler'

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
        time.sleep(LONG_DELAY)
        self._click_create_function()
        time.sleep(LONG_DELAY)
        self._set_function(FUNCTION_NAME, FUNCTION_RUNTIME, FUNCTION_DESC, FUNCTION_DIR, FUNCTION_HANDLER)
        time.sleep(DELAY)
