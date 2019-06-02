from dashboard.tests.test_dashboard import *
import sys

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
        print("created user group {}".format(name))

    def _has_user_group(self, name):
        """
        Make sure it has a member group [name] and return Whether that group exists
        :param name: Group name to create
        :return:bool
        """
        has_group_name = False
        group_names = self.parent.browser.find_elements_by_name('group-name')
        for group_name in group_names:
            if group_name.text == name:
                has_group_name = True
        return has_group_name

    def _create_user(self, email, password):
        """
        Create user with [email] and [password] in auth
        :param email:
        :param password:
        :return:
        """
        self.parent.browser.find_element_by_id('create-user-button').click()
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('input-username').send_keys(email)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('input-password').send_keys(password)
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('create-user-commit').click()

    def _has_user(self, target_email):
        """
        Check if there exists a user with [target_email].
        Return boolean
        :param target_email:
        :return :
        """
        emails = self.parent.browser.find_elements_by_name('col-user-email')
        for email in emails:
            email = email.text
            print('email:', email)
            if target_email == email:
                return True
        return False

    def _add_authorization(self, user_group, authorization_name):
        """
        Add [authorization_name] to [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_user_group(user_group))
        auth_groups = self.parent.browser.find_element_by_css_selector("table[class='table align-items-center table-flush']")
        group = None
        for group in auth_groups.find_elements_by_css_selector("th[name='group-name']"):
            if group.text.strip() == user_group:
                break

        group = group.find_element_by_xpath('..')
        group.find_element_by_id('modify-permissions-{}'.format(user_group)).click()
        time.sleep(DELAY)
        addable_authorizations = select.Select(group.find_element_by_id('select-permissions-{}'.format(user_group)))
        addable_authorizations.select_by_value(authorization_name)
        time.sleep(DELAY)
        group.find_element_by_css_selector("button[class='form-control btn btn-success']").click()
        time.sleep(DELAY)

    def _has_authorization(self, user_group, authorization_name):
        """
        Add [authorization_name] to [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_user_group(user_group))
        auth_groups = self.parent.browser.find_element_by_css_selector("table[class='table align-items-center table-flush']")
        group = None
        for group in auth_groups.find_elements_by_css_selector("th[name='group-name']"):
            if group.text.strip() == user_group:
                break
        group = group.find_element_by_xpath('..')
        group.find_element_by_id('modify-permissions-{}'.format(user_group)).click()
        time.sleep(DELAY)
        for authorization in group.find_elements_by_tag_name('tr'):
            if authorization.text.strip() == authorization_name:
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
        self._add_authorization(group_name, 'run:cloud.auth.login')
        time.sleep(DELAY)
        self._has_authorization(group_name, 'run:cloud.auth.login')
        time.sleep(DELAY)
        """
        self.parent.browser.find_element_by_id('remove-group-{}'.format(group_name)).click()
        time.sleep(DELAY)
        self.parent.assertFalse(self._has_user_group(group_name))
        time.sleep(LONG_DELAY)
        self._create_user(email, password)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_user(email))
        # LOGIN METHOD
        """