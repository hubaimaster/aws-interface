from dashboard.tests.base import *
from os import listdir
from os.path import isfile, join


class SDKTestCase(DashboardTestCase):
    def find_zip(self):
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    def test_sdk(self):
        time.sleep(DELAY)
        start_time = time.time()
        self.browser.find_element_by_id('link-overview').click()
        time.sleep(LONG_DELAY)
        while self.get_view_tag() != 'overview':
            self.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.assert_view_tag('overview')
        time.sleep(LONG_DELAY)
        # USER GROUP
        self.browser.find_element_by_id('download-sdk').click()
        print('download_dir:{}'.format(self.download_dir))
