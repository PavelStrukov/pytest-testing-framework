from ui_testing.pages.base_page import BasePage
from ui_testing.locators.python_locators import PythonLocators


class DownloadHelper(BasePage):
    """Class provides special methods for python.org pages"""

    def get_latest_python_version(self):
        """Provides getting string that contains python latest version"""
        return self.find_element(PythonLocators.LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION).text

    def get_mac_os_md5_sum(self):
        """Provides getting string with control md5 check sum for python mac os version"""
        return self.find_element(PythonLocators.LOCATOR_PYTHON_MAC_OS_MD5_SUM).text

    def click_download_latest(self):
        """Provides finding and clicking link to python latest version download page"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION).click()

    def click_download_for_mac_link(self):
        """Provides finding and clicking button to download python .pkg file"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_MAC_OS_DOWNLOAD_LINK).click()
