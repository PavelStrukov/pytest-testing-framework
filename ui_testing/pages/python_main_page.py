from ui_testing.pages.base_page import BasePage
from ui_testing.locators.python_locators import PythonLocators


class PythonMainPage(BasePage):
    """Class provides special methods for python.org pages"""

    def get_latest_python_version(self):
        """Provides getting string that contains python latest version"""
        return self.find_element(PythonLocators.LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION).text

    def click_download_latest(self):
        """Provides finding and clicking link to python latest version download page"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION).click()

    def click_docs_link(self):
        """Provides finding and clicking link to https://www.python.org/doc/ page"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_DOCS_LINK).click()

    def click_at_slide_index(self, index):
        """Provides finding and clicking button with tab index on a main page"""
        python_locators = PythonLocators()
        index_tab_locator = python_locators.get_python_index_tab_locator(index)
        return self.find_element(index_tab_locator).click()

    def check_visibility_of_slide_content(self, index):
        """Provides finding and checking visibility of current index tab on a main page"""
        python_locators = PythonLocators()
        slide_locator = python_locators.get_python_slides_locator(index)
        return self.find_element(slide_locator).is_displayed()

    def get_slide_content(self, index):
        """Provides getting string with current index tab content on a main page"""
        python_locators = PythonLocators()
        content_locator = python_locators.get_python_slides_content_locator(index)
        return self.find_element(content_locator).text
