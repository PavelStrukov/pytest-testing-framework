from ui_testing.locators.python_locators import PythonLocators
from ui_testing.pages.base_page import BasePage


class DocsPage(BasePage):

    def search_doc(self, search_item):
        """Provides searching search_item string at the python doc page"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_SEARCH_FIELD).send_keys(search_item)
        self.find_element(PythonLocators.LOCATOR_PYTHON_SUBMIT_BUTTON).click()

    def get_doc_for_metaclasses(self):
        """Provides getting https://www.python.org/dev/peps/pep-3115/ page after successful search request"""
        self.find_element(PythonLocators.LOCATOR_PYTHON_METACLASSES_3000).click()

    def get_post_history_content(self):
        """Provides getting post history content at the https://www.python.org/dev/peps/pep-3115/ page"""
        return self.find_element(PythonLocators.LOCATOR_PYTHON_POST_HISTORY_FIELD).text
