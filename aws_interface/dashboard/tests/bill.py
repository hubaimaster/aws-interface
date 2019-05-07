import time

DELAY = 2
LONG_DELAY = 4


class BillTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def do_test(self):
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('link-bill').click()
        time.sleep(LONG_DELAY)
        view_tag = self.parent.browser.find_element_by_id('view-tag').get_attribute('value')
        self.parent.assertEqual(view_tag, 'bill')
