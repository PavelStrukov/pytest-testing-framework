from ui_testing.locators.python_locators import PythonLocators
from ui_testing.pages.base_page import BasePage


class LatestPythonDownloadPage(BasePage):

    def click_download_for_mac_link(self):
        """Provides finding and clicking button to download python .pkg file"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_MAC_OS_DOWNLOAD_LINK).click()

    def get_mac_os_md5_sum(self):
        """Provides getting string with control md5 check sum for python mac os version"""
        return self.find_element(PythonLocators.LOCATOR_PYTHON_MAC_OS_MD5_SUM).text
