from dashboard.tests.test_dashboard import *


class StorageTestProcess:
    def __init__(self, parent):
        self.parent = parent

    def _click_load_more_files_button(self):
        """
        If there exists 'load-more-files-btn', click it.
        :return:
        """
        load_more = self.parent.browser.find_element_by_id('load-more-files-btn')
        if not load_more.get_attribute('style') == "display: none;":
            load_more.click()
            time.sleep(LONG_DELAY)

    def _click_file_upload_button(self):
        """
        Click 'file upload' button
        :return:
        """
        self.parent.browser.find_element_by_css_selector('a[data-target="#modal-upload-file"]').click()
        time.sleep(DELAY)
        file_upload_modal = self.parent.browser.find_element_by_id('modal-upload-file')
        styles = [style.strip() for style in file_upload_modal.get_attribute('style').split(';')]
        self.parent.assertTrue('display: block' in styles)
        print("Clicked file_upload button")

    def _attach_file_on_file_upload_modal(self, textfile):
        """
        Create text file with name [textfile] and attach it on file upload modal
        :param textfile: name of textfile to attach
        :return:
        """
        with open(textfile, 'w') as file:
            file.write("This is a test sample file")
        file_select = self.parent.browser.find_element_by_id('file-bin')
        self.file_dir = os.path.join(BASE_DIR, textfile)
        file_select.send_keys(self.file_dir)
        print("Added [{}]".format(textfile))

    def _click_accept_in_file_upload_modal(self):
        """
        Click accept in file upload modal
        :return:
        """
        self.parent.browser.find_element_by_id('upload-file').click()
        print("Uploaded file")


    def _has_file(self, textfile):
        """
        Check if textfile exists in file table
        :param textfile: name of textfile to check
        :return:
        """
        self._click_load_more_files_button()
        file_table = self.parent.browser.find_element_by_id('file-table')
        for tr in file_table.find_elements_by_tag_name('tr')[1:]:
            if tr.find_elements_by_tag_name('td')[1].text.strip() == textfile:
                print("[{}] exists".format(textfile))
                return True
        print("[{}] does not exist".format(textfile))
        return False

    def _download_and_compare_file(self, textfile):
        """
        Download [textfile] from file-table(on server) and compare it with original [textfile](in local)
        :param textfile: name of text file
        :return:
        """
        file_table = self.parent.browser.find_element_by_id('file-table')
        for tr in file_table.find_elements_by_tag_name('tr')[1:]:
            if tr.find_elements_by_tag_name('td')[1].text.strip() == textfile:
                file_link = tr.find_element_by_tag_name('a').get_attribute('href')
                self.parent.browser.get(file_link)
                print("Download link : {}".format(file_link))
                print("Downloaded [{}] at {}".format(textfile, self.parent.download_dir))
                break
        time.sleep(LONG_DELAY * 2)
        with open(os.path.join(self.parent.download_dir, textfile), 'r') as downloaded_file:
            with open(self.file_dir, 'r') as original_file:
                print("opened file")
                return original_file.read() == downloaded_file.read()

    def _remove_file(self, textfile):
        """
        Remove [textfile] from file table
        :param textfile: name of file to remove
        :return:
        """
        self._click_load_more_files_button()
        file_table = self.parent.browser.find_element_by_id('file-table')
        for tr in file_table.find_elements_by_tag_name('tr')[1:]:
            if tr.find_elements_by_tag_name('td')[1].text.strip() == textfile:
                tr.find_element_by_tag_name('button').click()
                print("Removed [{}]".format(textfile))
                return

    def do_test(self):
        TEXTFILE = 'sample.txt'
        os.path.dirname(os.path.dirname(os.path.abspath(settings.__file__)))

        time.sleep(DELAY)
        start_time = time.time()
        self.parent.browser.find_element_by_id('link-storage').click()
        time.sleep(LONG_DELAY)
        while True:
            try:
                if self.parent.get_view_tag() == 'storage':
                    break
                self.parent.browser.refresh()
                time.sleep(LONG_DELAY * 4)
                print('Wait...')
            except StaleElementReferenceException:
                pass
        duration = time.time() - start_time
        print('duration: {} s'.format(duration))

        self.parent.assert_view_tag('storage')
        time.sleep(LONG_DELAY)
        self._click_file_upload_button()
        time.sleep(DELAY)
        self._attach_file_on_file_upload_modal(TEXTFILE)
        time.sleep(LONG_DELAY)
        self._click_accept_in_file_upload_modal()
        time.sleep(LONG_DELAY * 2)
        self.parent.assertTrue(self._has_file(TEXTFILE))
        time.sleep(DELAY)
        self.parent.assertTrue(self._download_and_compare_file(TEXTFILE))
        time.sleep(DELAY)
        self._remove_file(TEXTFILE)
        time.sleep(LONG_DELAY * 6)
        self.parent.assertFalse(self._has_file(TEXTFILE))