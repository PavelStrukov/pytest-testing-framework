import pytest

from ui_testing import service
from ui_testing.pages.python_page import PythonMainPage

slide_indexes = [1, 2, 3, 4, 5]


@pytest.mark.parametrize("index", slide_indexes)
def test_python_code_example_is_visible(browser, index):
    python_page = PythonMainPage(browser)
    python_page.go_to_site()

    page_title = python_page.get_page_title()
    assert page_title == service.get_expected_title("main_page_title")

    python_page.click_at_slide_index(index)

    assert python_page.check_visibility_of_slide_content(index)

    slide_content = python_page.get_slide_content(index)
    title, first_string = service.get_slide_title_and_first_string(slide_content)

    expected_data = service.get_expected_slides_data(index)

    assert title == expected_data['title'] and first_string == expected_data['first_string']
