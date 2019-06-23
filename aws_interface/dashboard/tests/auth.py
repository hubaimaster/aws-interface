from dashboard.tests.test_dashboard import *


class AuthTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _create_group(self, name, description):
        """
        Create group with [name] and [description]
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
        print("created user group [{}]".format(name))

    def _has_user_group(self, name):
        """
        Check if group [name] exists
        :param name: Group name to create
        :return: bool
        """
        group_names = self.parent.browser.find_elements_by_name('group-name')
        for group_name in group_names:
            if group_name.text == name:
                print("user group [{}] exists".format(name))
                return True
        print("user group [{}] does not exist".format(name))
        return False

    def _remove_user_group(self, user_group):
        """
        Remove [user_group] from user group table
        :param user_group:
        :return:
        """
        remove_button = self.parent.browser.find_element_by_id('remove-group-{}'.format(user_group))
        self.parent.browser.execute_script('arguments[0].click();', remove_button)
        print("user group [{}] is removed".format(user_group))

    def _open_authorization(self, user_group):
        """
        Open authorization management modal of [user_group]
        :param user_group: name of user_group to manage authoirzation
        :return: group: selenium.webdriver.remote.webelement.WebElement object of row with name [user_group]
        """
        auth_groups = self.parent.browser.find_element_by_css_selector("table[class='table align-items-center table-flush']")
        group = None
        for group in auth_groups.find_elements_by_css_selector("th[name='group-name']"):
            if group.text.strip() == user_group:
                break
        group = group.find_element_by_xpath('..')
        group.find_element_by_css_selector('button[id="modify-permissions-{}"]'.format(user_group)).click()
        print("Opened authorization modal")
        return group

    def _add_authorization(self, user_group, authorization_name):
        """
        Add [authorization_name] to [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_user_group(user_group))
        group = self._open_authorization(user_group)
        time.sleep(DELAY)
        addable_authorizations = select.Select(group.find_element_by_id('select-permissions-{}'.format(user_group)))
        addable_authorizations.select_by_value(authorization_name)
        time.sleep(DELAY)
        group.find_element_by_css_selector("button[class='form-control btn btn-success']").click()
        print("[{}] added to [{}]".format(authorization_name, user_group))

    def _has_authorization(self, user_group, authorization_name):
        """ Check if [user_group] has [authorization_name]
        :param user_group: name of user_group
        :param authorization_name: name of authorization
        :return:
        """
        result = False
        self.parent.assertTrue(self._has_user_group(user_group))
        group = self._open_authorization(user_group)
        time.sleep(DELAY)
        close_button = group.find_element_by_css_selector('button[data-dismiss="modal"]')
        group = group.find_element_by_tag_name('tbody')
        for authorization in group.find_elements_by_tag_name('td'):
            if authorization.text.strip() == authorization_name:
                print("[{}] has [{}]".format(user_group, authorization_name))
                result = True
                break
        close_button.click()
        return result

    def _remove_authorization(self, user_group, authorization_name):
        """
        Remove [authorization_name] from [user_group]
        :param authorization_name:
        :return:
        """
        self.parent.assertTrue(self._has_authorization(user_group, authorization_name))
        time.sleep(LONG_DELAY)
        group = self._open_authorization(user_group)
        time.sleep(DELAY)
        group = group.find_element_by_tag_name('tbody')
        group.find_element_by_css_selector("a[onclick*='{}']".format(authorization_name)).click()
        print("[{}] is removed from [{}]".format(authorization_name, user_group))

    def _select_login_method(self, select_id, value, toggle_id):
        """
        Change login method in [select_id] to [value] and toggle button with [toggle_id]
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
        print("[{}] selected from [{}]".format(value, select_id))

    def _check_login_method(self, select_id, value, toggle_id):
        """
        Check whether [value] is selected in select box with [select_id] and whether switch with [toggle_id] is toggled
        :param select_id: id of select box
        :param value: value that should be selected
        :param toggle_id: id of toggle button
        :return:
        """
        select_box = select.Select(self.parent.browser.find_element_by_id(select_id))
        selected_option = select_box.first_selected_option.get_attribute("value")
        print("checked login")
        return (selected_option == value) and (not self.parent.browser.find_element_by_id(toggle_id).is_selected())

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
        print("user with [{}], [{}] created".format(email, password))

    def _has_user_email(self, target_email):
        """
        Check if there exists a user with [target_email].
        :param target_email:
        :return : bool
        """
        self._click_load_more_users_button()
        emails = self.parent.browser.find_elements_by_name('col-user-email')
        for email in emails:
            email = email.text
            if email.strip() == target_email:
                print("[{}] exists".format(target_email))
                return True
        return False

    def _get_user_count(self):
        """
        Check the number of user
        :param count: number of user
        :return: bool
        """
        user_count_box = self.parent.browser.find_element_by_class_name("card-body")
        count_on_page = int(user_count_box.find_element_by_css_selector('span').text.strip().split()[0])
        print("number of user : {}".format(count_on_page))
        return int(count_on_page)

    def _has_group_in_user(self, group_name):
        """
        Check if group_name is in signed_up user list
        :param group_name: name of group
        :return: bool
        """
        result = False
        self._click_load_more_users_button()
        user_table = self.parent.browser.find_element_by_id("user-table")
        for tr in user_table.find_elements_by_tag_name("tr")[1:]:
            groups = tr.find_elements_by_tag_name("td")[2]
            for group in groups.find_elements_by_tag_name('a'):
                if group.text.strip() == group_name:
                    result = True
                    break
        print("group [{}] is in signed-up user".format(group_name))
        return result

    def _add_group_in_user(self, group_name):
        """
        Add [group_name] to Groups column of signed-up user
        :param group_name: name of group to add
        :return:
        """
        self._click_load_more_users_button()
        add_button = self.parent.browser.find_element_by_css_selector("a[data-target^='#modal-attach-user-group']")
        add_button.click()
        time.sleep(DELAY)
        modal = add_button.find_element_by_xpath('..')
        select_box = select.Select(modal.find_element_by_id('group-name'))
        select_box.select_by_value(group_name)
        modal.find_element_by_css_selector("button[id^='attach-user-group']").click()
        time.sleep(DELAY)
        print("added {} on GROUPS column".format(group_name))

    def _remove_group_in_user(self, group_name):
        """
        Remove [group_name] from GROUPS column of signed-up user
        :param group_name: name of group to remove
        :return:
        """
        self._click_load_more_users_button()
        groups = self.parent.browser.find_elements_by_css_selector("a[onclick^='detach_user_group']")
        for group in groups:
            if group.text.strip() == group_name:
                print("[{}] is found".format(group.text.strip()))
                group.click()
                self.parent.browser.switch_to.alert.accept()
                break
        print("removed {} from GROUPS column".format(group_name))

    def _click_checkbox_and_modify_selected_in_user(self):
        """
        Click checkbox in signed-up user table and open 'modify selected' modal
        :return:
        """
        self._click_load_more_users_button()
        radio_button = self.parent.browser.find_element_by_name('checkbox-user')
        self.parent.browser.execute_script("arguments[0].checked = true;", radio_button)
        print("checkbox is checekd : {}".format(str(self.parent.browser.find_element_by_name('checkbox-user').is_selected())))
        time.sleep(LONG_DELAY)
        user_table = self.parent.browser.find_element_by_id('create-user-button')
        user_table = user_table.find_element_by_xpath('..')
        user_table.find_element_by_id('dropdownMenuButton').click()
        user_table.find_element_by_css_selector("a[data-target='#modal-mod-user']").click()
        print("Opened modify_selected modal")

    def _click_checkbox_and_delete_selected_in_user(self):
        """
        Click checkbox in signed-up user table and open 'delete selected' modal
        :return:
        """
        self._click_load_more_users_button()
        radio_button = self.parent.browser.find_element_by_name('checkbox-user')
        self.parent.browser.execute_script("arguments[0].checked = true;", radio_button)
        print("checkbox is checekd : {}".format(str(self.parent.browser.find_element_by_name('checkbox-user').is_selected())))
        time.sleep(LONG_DELAY)
        user_table = self.parent.browser.find_element_by_id('create-user-button')
        user_table = user_table.find_element_by_xpath('..')
        user_table.find_element_by_id('dropdownMenuButton').click()
        user_table.find_element_by_css_selector("a[onclick='delete_checked_users();']").click()
        print("Deleted selected user")

    def _modify_selected(self, field_name, field_type, field_value):
        """
        Modify field name to [field_name], field type tio [field_type], field value to [field_value]
        :param field_name: modified field name
        :param field_type: modified field type
        :param field_value: modified field value
        :return:
        """
        self.parent.browser.find_element_by_name('user-field-name').send_keys(field_name)
        field_type_dropdown = select.Select(self.parent.browser.find_element_by_id('user-field-type'))
        field_type_dropdown.select_by_value(field_type)
        self.parent.browser.find_element_by_name('user-field-value').send_keys(field_value)
        self.parent.browser.find_element_by_id('mod-user-commit').click()
        print("Modified selected")

    def _has_extra(self, extra_name, extra_value):
        """
        Check if [extra_name] : [extra_value] appear in extra column
        :param extra_name: field name that should appear
        :param extra_value: field value that should appear
        :return:
        """
        self._click_load_more_users_button()
        user_table = self.parent.browser.find_element_by_id("user-table")
        for tr in user_table.find_elements_by_tag_name("tr")[1:]:
            groups = tr.find_elements_by_tag_name("td")[3]
            for extra in groups.find_elements_by_tag_name('h5'):
                if extra.text.strip() == "{} : {}".format(extra_name, extra_value):
                    print("[{}] is in extra column".format(extra.text))
                    return True
        print("[{}] [{}] is not in extra column".format(extra_name, extra_value))
        return False

    def _click_load_more_users_button(self):
        """
        If there exists 'load-more-users-btn', click it.
        :return:
        """
        time.sleep(LONG_DELAY)
        load_more = self.parent.browser.find_element_by_id('load-more-users-btn')
        if load_more.get_attribute('style').strip() != "display: none;":
            load_more.click()
            time.sleep(LONG_DELAY)

    def do_test(self):
        GROUP_NAME = 'TEST-GROUP'
        GROUP_DESC = 'Group for testing'
        TEST_EMAIL = 'test@email.com'
        TEST_PASSWORD = 'testpassword1234'
        AUTH_LOGIN = 'run:cloud.auth.login'
        AUTH_LOGOUT = 'run:cloud.auth.logout'
        FIELD_NAME = "extra_test"
        FIELD_TYPE = "S"
        FIELD_VALUE = "Test"

        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-auth').click()
        time.sleep(LONG_DELAY)
        while True:
            try:
                if self.parent.get_view_tag() == 'auth':
                    break
                self.parent.browser.refresh()
                time.sleep(LONG_DELAY * 4)
                print('Wait...')
            except StaleElementReferenceException:
                pass
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))
        print("****START TESTING AUTH****")

        self.parent.assert_view_tag('auth')
        time.sleep(LONG_DELAY)
        # USER GROUP - except remove
        # Only leave codes for logic testing
        self._create_group(GROUP_NAME, GROUP_DESC)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertTrue(self._has_user_group(GROUP_NAME))
        time.sleep(DELAY)
        """
        # Commenting code unneeded for logic testing.
        self.parent.assertFalse(self._has_authorization(GROUP_NAME, AUTH_LOGIN))
        time.sleep(LONG_DELAY * 2)
        self._add_authorization(GROUP_NAME, AUTH_LOGIN)
        time.sleep(LONG_DELAY * 3)
        self.parent.assertTrue(self._has_authorization(GROUP_NAME, AUTH_LOGIN))
        time.sleep(LONG_DELAY)
        self.parent.assertFalse(self._has_authorization(GROUP_NAME, AUTH_LOGOUT))
        time.sleep(LONG_DELAY)
        self._add_authorization(GROUP_NAME, AUTH_LOGOUT)
        time.sleep(LONG_DELAY * 3)
        self.parent.assertTrue(self._has_authorization(GROUP_NAME, AUTH_LOGOUT))
        time.sleep(LONG_DELAY * 2)
        self._remove_authorization(GROUP_NAME, AUTH_LOGIN)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertFalse(self._has_authorization(GROUP_NAME, AUTH_LOGIN))
        time.sleep(LONG_DELAY)
        # LOGIN METHOD
        self._select_login_method("email_default_group", GROUP_NAME, "email_enabled")
        time.sleep(DELAY)
        self._check_login_method("email_default_group", GROUP_NAME, "email_enabled")
        time.sleep(DELAY)
        self._select_login_method("guest_default_group", GROUP_NAME, "guest_enabled")
        time.sleep(DELAY)
        self._check_login_method("guest_default_group", GROUP_NAME, "guest_enabled")
        time.sleep(DELAY)
        self._select_login_method("email_default_group", 'user', "email_enabled")
        time.sleep(DELAY)
        self._select_login_method("guest_default_group", 'user', "guest_enabled")
        time.sleep(DELAY)"""
        # USER
        # Only leave codes for logic testing
        self._create_user(TEST_EMAIL, TEST_PASSWORD)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertTrue(self._has_user_email(TEST_EMAIL))
        time.sleep(DELAY)
        """
        # Commenting code unneeded for logic testing.
        self.parent.assertTrue(self._get_user_count() == 1)
        time.sleep(DELAY)
        self.parent.assertTrue(self._has_group_in_user("user"))
        time.sleep(DELAY)
        self._add_group_in_user(GROUP_NAME)
        time.sleep(LONG_DELAY)
        self.parent.assertTrue(self._get_user_count() == 1)
        time.sleep(DELAY)
        self.parent.assertTrue(self._has_group_in_user(GROUP_NAME))
        time.sleep(LONG_DELAY)
        self._remove_group_in_user(GROUP_NAME)
        time.sleep(LONG_DELAY)
        self.parent.assertFalse(self._has_group_in_user(GROUP_NAME))
        time.sleep(DELAY)
        self._click_checkbox_and_modify_selected_in_user()
        time.sleep(DELAY)
        self._modify_selected(FIELD_NAME, FIELD_TYPE, FIELD_VALUE)
        time.sleep(LONG_DELAY * 6)
        self.parent.assertTrue(self._has_extra(FIELD_NAME, FIELD_VALUE))
        time.sleep(DELAY)
        self._click_checkbox_and_delete_selected_in_user()
        time.sleep(LONG_DELAY * 6)
        self.parent.assertFalse(self._has_user_email(TEST_EMAIL))
        # USERGROUP - remove
        self._remove_user_group(GROUP_NAME)
        time.sleep(LONG_DELAY * 2)
        self.parent.assertFalse(self._has_user_group(GROUP_NAME))
        time.sleep(DELAY)
        """