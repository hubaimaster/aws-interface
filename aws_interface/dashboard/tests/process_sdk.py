from dashboard.tests.base import *


class SDKTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def do_test(self):
        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-overview').click()
        time.sleep(LONG_DELAY)
        while self.parent.get_view_tag() != 'overview':
            self.parent.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('overview')
        time.sleep(LONG_DELAY)
        # USER GROUP
        self.parent.browser.find_element_by_id('download-sdk').click()
        print('download_dir:{}'.format(self.parent.download_dir))
