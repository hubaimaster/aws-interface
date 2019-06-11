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

    def _open_authorization(self, user_group):
        """
        Open authorization management modal of [user_group]
        :param user_group: name of user_group to manage authoirzation
        :return: selenium.webdriver.remote.webelement.WebElement
        """
        auth_groups = self.parent.browser.find_element_by_css_selector("table[class='table align-items-center table-flush']")
        group = None
        for group in auth_groups.find_elements_by_css_selector("th[name='group-name']"):
            if group.text.strip() == user_group:
                break

        group = group.find_element_by_xpath('..')
        group.find_element_by_id('modify-permissions-{}'.format(user_group)).click()
        time.sleep(DELAY)
        return group

    def _add_authorization(self, user_group, authorization_name):
        """
        Add [authorization_name] to [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_user_group(user_group))
        group = self._open_authorization(user_group)
        addable_authorizations = select.Select(group.find_element_by_id('select-permissions-{}'.format(user_group)))
        addable_authorizations.select_by_value(authorization_name)
        time.sleep(DELAY)
        group.find_element_by_css_selector("button[class='form-control btn btn-success']").click()
        print("authorization added")

    def _has_authorization(self, user_group, authorization_name):
        """
        Check if [user_group] has [authorization_name]
        :param authorization_name:
        :return: bool
        """
        self.parent.assertTrue(self._has_user_group(user_group))
        group = self._open_authorization(user_group)
        result = False
        for authorization in group.find_elements_by_tag_name('tr'):
            if authorization.text.strip() == authorization_name:
                result = True
                break
        group.find_element_by_class_name('close').click()
        # group.find_element_by_id('attach-user-group-commit').click()
        return result

    def _remove_authorization(self, user_group, authorization_name):
        """
        Remove [authorization_name] from [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_authorization(user_group, authorization_name))
        group = self._open_authorization(user_group)
        for authorization in group.find_elements_by_tag_name('tr'):
            if authorization.text.strip() == authorization_name:
                authorization.find_element_by_css_selector("a[class='btn btn-danger btn-sm text text-white']").click()
                break
        print("remove done ")

    def _select_login_method(self, select_id, value, toggle_id):
        """
        select [value] at select box with [select_id] and toggle button with [toggle_id]
        :param select_id: id of select box
        :param value: value to select
        :param toggle_id: id of toggle button
        :return:
        """
        select_box = select.Select(self.parent.browser.find_element_by_id(select_id))
        select_box.select_by_value(value)
        time.sleep(DELAY)
        toggle_button = self.parent.browser.find_element_by_id(toggle_id)
        toggle_button = toggle_button.find_element_by_xpath('..')
        toggle_button.click()
        time.sleep(DELAY)
        self.parent.browser.refresh()
        print("{} selected from {}".format(value, select_id))

    def _check_login_method(self, select_id, value, toggle_id):
        """
        Check if [value] is selected in select box with [select_id] and if switch with [toggle_id] is toggled
        :param select_id: id of select box
        :param value: value that should be selected
        :param toggle_id: id of toggle button
        :return:
        """
        select_box = select.Select(self.parent.browser.find_element_by_id(select_id))
        selected_option = select_box.first_selected_option.get_attribute("value")
        self.parent.assertTrue(selected_option == value)
        self.parent.assertFalse(self.parent.browser.find_element_by_id(toggle_id).is_selected())
        print("checked login")

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

    def _has_user_email(self, target_email):
        """
        Check if there exists a user with [target_email].
        :param target_email:
        :return : bool
        """
        emails = self.parent.browser.find_elements_by_name('col-user-email')
        for email in emails:
            email = email.text
            if email.strip() == target_email:
                return True
        return False

    def _check_user_count(self,count):
        """
        Check the number of user
        :param count: number of user
        :return: bool
        """
        user_count_box = self.parent.browser.find_element_by_class_name("card-body")
        count_on_page = int(user_count_box.find_element_by_css_selector('span').text.strip().split()[0])
        print(count_on_page)
        return self.parent.assertTrue(count_on_page == count)

    def _has_group_in_user(self, group_name):
        """
        Check if group_name is in signed_up user list
        :param group_name: name of group
        :return: bool
        """
        result = False
        user_table = self.parent.browser.find_element_by_id("user-table")
        for tr in user_table.find_elements_by_tag_name("tr")[1:]:
            groups = tr.find_elements_by_tag_name("td")[2]
            if groups.find_element_by_tag_name('a').text.strip() == group_name:
                result = True
                break
        print("checked user group in user")
        return result

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
        """
        self.parent.assertFalse(self._has_authorization(group_name, 'run:cloud.auth.login'))
        time.sleep(DELAY)
        self._add_authorization(group_name, 'run:cloud.auth.login')
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_authorization(group_name, 'run:cloud.auth.login'))
        time.sleep(DELAY)
        self.parent.assertFalse(self._has_authorization(group_name, 'run:cloud.auth.logout'))
        time.sleep(DELAY)
        self._add_authorization(group_name, 'run:cloud.auth.logout')
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_authorization(group_name, 'run:cloud.auth.logout'))
        time.sleep(DELAY)
        self._remove_authorization(group_name, 'run:cloud.auth.login')
        time.sleep(LONG_DELAY)
        self.parent.assertFalse(self._has_authorization(group_name, 'run:cloud.auth.login'))
        time.sleep(DELAY)
        self.parent.browser.find_element_by_id('remove-group-{}'.format(group_name)).click()
        time.sleep(DELAY)
        self.parent.assertFalse(self._has_user_group(group_name))
        time.sleep(LONG_DELAY)
        """
        # LOGIN METHOD
        self._select_login_method("email_default_group", group_name, "email_enabled")
        time.sleep(DELAY)
        self._check_login_method("email_default_group", group_name, "email_enabled")
        time.sleep(DELAY)
        self._select_login_method("guest_default_group", group_name, "guest_enabled")
        time.sleep(DELAY)
        self._check_login_method("guest_default_group", group_name, "guest_enabled")
        time.sleep(DELAY)
        #USER
        self._create_user(email, password)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._has_user_email(email))
        time.sleep(DELAY)
        self._check_user_count(1)
        time.sleep(DELAY)
        self._has_group_in_user(group_name)
        time.sleep(DELAY)