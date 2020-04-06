from ui_testing.pages.docs_page import DocsPage
from ui_testing.pages.python_main_page import PythonMainPage
import ui_testing.service as service


def test_check_python_metaclasses_history(browser):
    python_page = PythonMainPage(browser)
    python_page.go_to_site()

    title = python_page.get_page_title()
    assert title == service.get_expected_title("main_page_title")

    python_page.click_docs_link()

    docs_page = DocsPage(browser)

    title = docs_page.get_page_title()
    assert title == service.get_expected_title("documentation_page_title")

    docs_page.search_doc(service.get_required_search_text())

    docs_page.get_doc_for_metaclasses()

    title = docs_page.get_page_title()
    assert title == service.get_expected_title("doc_for_metaclasses_page_title")

    actual = docs_page.get_post_history_content()
    expected = service.get_expected_post_history()

    assert expected == actual
