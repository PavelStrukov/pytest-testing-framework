from selenium.webdriver.common.by import By


class PythonLocators:
    """Class provides the list of xpath locators for the testing python latest version download"""

    LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION = \
        (By.XPATH, "//div[@class='small-widget download-widget']/p[contains(text(), \"Latest: \")]/a")

    LOCATOR_PYTHON_MAC_OS_DOWNLOAD_LINK = (By.XPATH, "//td[contains(text(),'Mac OS X')]/../td[1]/a")

    LOCATOR_PYTHON_MAC_OS_MD5_SUM = (By.XPATH, "//td[contains(text(),'Mac OS X')]/../td[4]")

    LOCATOR_PYTHON_DOCS_LINK = (By.XPATH, "//li[@id='documentation']/a")

    LOCATOR_PYTHON_SEARCH_FIELD = (By.ID, "id-search-field")

    LOCATOR_PYTHON_SUBMIT_BUTTON = (By.ID, "submit")

    LOCATOR_PYTHON_METACLASSES_3000 = (By.XPATH, "//a[contains(text(),'PEP 3115 -- Metaclasses in Python 3000')]")

    LOCATOR_PYTHON_POST_HISTORY_TITLE = (By.XPATH, "//th[contains(text(),'Post-History:')]")

    LOCATOR_PYTHON_POST_HISTORY_FIELD = (By.XPATH, "//th[contains(text(),'Post-History:')]/../td")

    PYTHON_INDEX_TAB = "//ol[@class='flex-control-nav flex-control-paging']//li[{index}]//a"

    PYTHON_SLIDES = "//ul[@class='slides menu']//li[{index}]"

    PYTHON_SLIDES_CONTENT = "//div[@id='dive-into-python']//ul[@class='slides menu']//li[{index}]//code"

    def get_python_index_tab_locator(self, index):
        """Method provides filling index into locator string and generates locator type element"""
        return By.XPATH, self.PYTHON_INDEX_TAB.format(index=index)

    def get_python_slides_content_locator(self, index):
        """Method provides filling index into locator string and generates locator type element"""
        return By.XPATH, self.PYTHON_SLIDES_CONTENT.format(index=index)

    def get_python_slides_locator(self, index):
        """Method provides filling index into locator string and generates locator type element"""
        return By.XPATH, self.PYTHON_SLIDES.format(index=index)
