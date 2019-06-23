from dashboard.tests.test_dashboard import *


class LogTestProcess:
    def __init__(self, parent):
        self.parent = parent

        def do_test(self):
            time.sleep(DELAY)
            start_time = time.time()
            self.parent.browser.find_element_by_id('link-log').click()
            time.sleep(LONG_DELAY)
            while True:
                try:
                    if self.parent.get_view_tag() == 'log':
                        break
                    self.parent.browser.refresh()
                    time.sleep(LONG_DELAY * 4)
                    print('Wait...')
                except StaleElementReferenceException:
                    pass
            duration = time.time() - start_time
            print('duration: {} s'.format(duration))
            print("****START TESTING LOG****")

            self.parent.assert_view_tag('LOG')
            time.sleep(LONG_DELAY)