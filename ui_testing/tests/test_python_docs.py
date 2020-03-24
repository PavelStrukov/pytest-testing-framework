from ui_testing.pages.python_page import PythonMainPage
import ui_testing.service as service


def test_check_python_metaclasses_history(browser):
    python_page = PythonMainPage(browser)
    python_page.go_to_site()
    python_page.click_docs_link()

    python_page.search_doc(service.get_required_search_text())

    python_page.get_doc_for_metaclasses()

    actual = python_page.get_post_history_content()
    expected = service.get_expected_post_history()

    assert expected == actual
