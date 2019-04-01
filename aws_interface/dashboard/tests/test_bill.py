import time
from dashboard.tests.base import DashboardTestCase

DELAY = 2
LONG_DELAY = 4


class BillTestCase(DashboardTestCase):
    def test_bill(self):
        time.sleep(DELAY)
        self.browser.find_element_by_id('link-bill').click()
        time.sleep(LONG_DELAY)
        view_tag = self.browser.find_element_by_id('view-tag').get_attribute('value')
        self.assertEqual(view_tag, 'bill')
