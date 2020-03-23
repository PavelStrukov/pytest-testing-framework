import defenitions
from ui_testing.pages.python_page import PythonPage
import ui_testing.service as service


def test_is_latest_version_python(browser):
    python_page = PythonPage(browser)
    python_page.go_to_site()
    latest_version = python_page.get_latest_python_version()

    assert latest_version == service.get_expected_python_version()


def test_download_latest_python_version(browser):
    python_page = PythonPage(browser)
    python_page.click_download_latest()
    python_page.click_download_for_mac_link()

    service.download_wait(defenitions.PATH_TO_DOWNLOADS, 1)

    actual_check_sum = service.get_md5_checksum(service.get_path_to_downloaded_file())

    expected_check_sum = python_page.get_mac_os_md5_sum()

    assert actual_check_sum == expected_check_sum
