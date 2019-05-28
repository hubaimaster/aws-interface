from dashboard.tests.test_dashboard import *


class AuthTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _create_group(self, name, description):
        """
        :param name: Group name to create
        :param description: Group description to create
        :return:
        """
        self.parent.browser.find_element_by_id('create-group-modal').click()
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('group-name').send_keys(name)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('group-description').send_keys(description)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('create-group').click()

    def _has_user_group(self, name):
        has_group_name = False
        group_names = self.parent.browser.find_elements_by_name('group-name')
        for group_name in group_names:
            if group_name.text == name:
                has_group_name = True
        return has_group_name

    def _create_user(self, email, password):
        self.parent.browser.find_element_by_id('create-user-button').click()
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('input-username').send_keys(email)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('input-password').send_keys(password)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('create-user-commit').click()

    def _has_user(self, target_email):
        emails = self.parent.browser.find_elements_by_name('col-user-email')
        for email in emails:
            email = email.text
            print('email:', email)
            if target_email == email:
                return True
        return False

    def do_test(self):
        group_name = 'TEST-GROUP'
        group_desc = 'Group for testing'
        email = 'test@email.com'
        password = 'testpassword1234'

        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-auth').click()
        time.sleep(LONG_DELAY)
        while self.parent.get_view_tag() != 'auth':
            self.parent.browser.refresh()
            time.sleep(LONG_DELAY * 4)
            print('Wait...')
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('auth')
        time.sleep(LONG_DELAY)
        # USER GROUP
        self._create_group(group_name, group_desc)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_user_group(group_name))
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('remove-group-{}'.format(group_name)).click()
        time.sleep(DELAY)
        self.parent.assertFalse(self._has_user_group(group_name))
        time.sleep(LONG_DELAY)
        self._create_user(email, password)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_user(email))
        # LOGIN METHOD

