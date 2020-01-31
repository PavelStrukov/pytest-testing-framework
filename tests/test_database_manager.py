import pytest

from src.Student import *
from src.database_manager import DatabaseManager


@pytest.fixture
def manager():
    manager = DatabaseManager(["root", "password"], "127.0.0.1", "TestBase")
    yield manager
    manager.close_connection()


def test_insert_request(manager):
    student = Student(id=11, name='NewestStudent', login='NewestLogin', password='NewestPass1', group_id=2)
    request = manager.generate_insert_request(student)
    result = manager.send_request(request)
    assert result is None


def test_invalid_insert_request(manager):
    with pytest.raises(ValueError):
        student_with_incorrect_data_types = Student(id='NewestStudent', name='NewestLogin', login='NewestPass1',
                                                    password=2, group_id=2)
        student_with_incorrect_number_of_data = Student(name='NewestStudent', login='NewestLogin',
                                                        password='NewestPass1',
                                                        group_id=2)
        request = manager.generate_insert_request(student_with_incorrect_data_types)
        manager.send_request(request)
        request = manager.generate_insert_request(student_with_incorrect_number_of_data)
        manager.send_request(request)


def test_one_row_select_request(manager):
    created_student = Student(id=7, name='TempStudent', login='TempStudentLogin', password='tempStudentPass1',
                              group_id=3)
    insert_request = manager.generate_insert_request(created_student)
    manager.send_request(insert_request)

    select_request = manager.generate_select_request("login='TempStudentLogin'")
    result = manager.send_request(select_request)
    received_student = Student(student_as_dict=result[0])
    assert created_student == received_student


def test_few_rows_select_request(manager):
    first_created_student = Student(id=8, name='FirstTempStudent', login='FirstTempStudentLogin',
                                    password='tempStudentPass1', group_id=15)
    first_insert_request = manager.generate_insert_request(first_created_student)
    manager.send_request(first_insert_request)

    second_created_student = Student(id=9, name='SecondTempStudent', login='SecondTempStudentLogin',
                                     password='tempStudentPass1', group_id=15)
    second_insert_request = manager.generate_insert_request(second_created_student)
    manager.send_request(second_insert_request)

    select_request = manager.generate_select_request("group_id=15")
    result = manager.send_request(select_request)

    list_of_created_students = [first_created_student, second_created_student]
    list_of_received_students = get_list_of_students(result)
    assert list_of_created_students == list_of_received_students


def test_select_not_existed_student(manager):
    not_existing_student = Student(id=13, name='NoStudent', login='NoStudentLogin',
                                   password='NoStudentPass1', group_id=15)
    not_existing_student_select_request = manager.generate_select_request("login='NoStudentLogin'")
    result = manager.send_request(not_existing_student_select_request)
    assert len(result) == 0


def test_update_request(manager):
    created_student = Student(id=10, name='TempStudent', login='TempStudentLogin', password='tempStudentPass1',
                              group_id=3)
    insert_request = manager.generate_insert_request(created_student)
    manager.send_request(insert_request)

    update_request = manager.generate_update_request("login='UpdatedLogin'", "id=10")
    manager.send_request(update_request)

    updated_student = created_student
    updated_student.login = "'UpdatedLogin'"

    find_updated_student_request = manager.generate_select_request("login='UpdatedLogin'")
    student_as_list = manager.send_request(find_updated_student_request)
    student_found = Student(student_as_dict=student_as_list[0])
    assert updated_student == student_found


def test_not_existed_student_update(manager):
    with pytest.raises(ValueError):
        update_request = manager.generate_update_request("login='UpdatedLogin'", "name=NoStudent")
        manager.send_request(update_request)


def test_delete_request(manager):
    created_student = Student(id=12, name='StudentForDelete', login='DeleteStudentLogin', password='deleteStudentPass1',
                              group_id=3)
    insert_request = manager.generate_insert_request(created_student)
    manager.send_request(insert_request)

    delete_request = manager.generate_delete_request("name='StudentForDelete'")
    manager.send_request(delete_request)

    select_all_students_request = manager.generate_select_request()
    all_students_as_list_of_dicts = manager.send_request(select_all_students_request)
    all_students = get_list_of_students(all_students_as_list_of_dicts)
    assert created_student not in all_students


def test_not_existed_student_delete(manager):
    delete_request = manager.generate_delete_request("name='NoStudent'")
    result = manager.send_request(delete_request)
    assert result is None
