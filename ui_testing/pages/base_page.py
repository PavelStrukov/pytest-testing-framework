from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """The class provides the base model of the https://www.python.org/ Internet page"""

    def __init__(self, driver):
        """Class initialises with selenium web driver"""
        self.driver = driver
        self.base_url = "https://www.python.org/"

    def find_element(self, locator, time=10):
        """Method provides waiting for and getting element by xpath"""
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator),
                                                      message=f"Can't find element by locator {locator}")

    def get_page_title(self):
        """Method returns string with current page name"""
        return self.driver.title

    def go_to_site(self):
        """Method provides getting the main page"""
        return self.driver.get(self.base_url)
