from selenium.webdriver.common.by import By


class PythonLocators:
    """Class provides the list of xpath locators for the testing python latest version download"""

    LOCATOR_PYTHON_DOWNLOAD_LATEST_SECTION = \
        (By.XPATH, "//div[@class='small-widget download-widget']/p[contains(text(), \"Latest: \")]/a")

    LOCATOR_PYTHON_MAC_OS_DOWNLOAD_LINK = (By.XPATH, "//td[contains(text(),'Mac OS X')]/../td[1]/a")

    LOCATOR_PYTHON_MAC_OS_MD5_SUM = (By.XPATH, "//td[contains(text(),'Mac OS X')]/../td[4]")
