from dashboard.tests.base import *


class AuthTestCase(DashboardTestCase):
    def _create_group(self, name, description):
        self.browser.find_element_by_id('create-group-modal').click()
        time.sleep(DELAY)
        self.browser.find_element_by_id('group-name').send_keys(name)
        self.browser.find_element_by_id('group-description').send_keys(description)
        self.browser.find_element_by_id('create-group').click()

    def _has_user_group(self, name):
        has_group_name = False
        group_names = self.browser.find_elements_by_name('group-name')
        for group_name in group_names:
            if group_name.text == name:
                has_group_name = True
        return has_group_name

    def _create_user(self, name):
        pass

    def test_auth(self):
        group_name = 'TEST-GROUP'
        group_desc = 'Group for testing'
        time.sleep(DELAY)
        start_time = time.time()
        self.browser.find_element_by_id('link-auth').click()
        time.sleep(LONG_DELAY)
        while self.get_view_tag() != 'auth':
            self.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.assert_view_tag('auth')
        time.sleep(LONG_DELAY)
        # USER GROUP
        self._create_group(group_name, group_desc)
        time.sleep(LONG_DELAY)
        self.assertTrue(self._has_user_group(group_name))
        self.browser.find_element_by_id('remove-group-{}'.format(group_name)).click()
        time.sleep(DELAY)
        self.assertFalse(self._has_user_group(group_name))
        time.sleep(LONG_DELAY)
        # LOGIN METHOD
        

