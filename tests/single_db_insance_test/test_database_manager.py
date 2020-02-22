import pytest
import yaml
from mysql.connector import ProgrammingError

from src.student import *
from src.database_manager import DatabaseManager
from defenitions import ROOT_DIR


@pytest.fixture(scope="module")
def manager():
    with open(str(ROOT_DIR) + "/configs/databaseconfig.yml", "r") as yml_file:
        dbcfg = yaml.load(yml_file, Loader=yaml.FullLoader)['mysql']
        manager = DatabaseManager([dbcfg['user'], dbcfg['password']], dbcfg['host'], dbcfg['port'], dbcfg['db'])

        manager.send_request("CREATE TABLE IF NOT EXISTS students ("
                             "id INT,"
                             "name VARCHAR(255),"
                             "login VARCHAR(255),"
                             "password VARCHAR(255),"
                             "group_id INT) "
                             "ENGINE=INNODB;")

        yield manager
    manager.send_request("DROP DATABASE IF EXISTS testdb")
    manager.close_connection()


def test_insert_request(manager):
    student = Student(id=11, name='NewestStudent', login='NewestLogin',
                      password='NewestPass1', group_id=2)
    request = manager.generate_insert_request(student)
    result = manager.send_request(request)
    assert result is None


test_add_invalid_student_data = [
    ({"id": "NewestStudent", "name": "NewestLogin", "login": "NewestPass1", "password": 2, "group_id": 2}, TypeError),
    ({"name": "NewestStudent", "login": "NewestLogin", "password": "NewestPass1", "group_id": 2}, KeyError),
]


@pytest.mark.parametrize("new_student, expected", test_add_invalid_student_data)
def test_invalid_insert_request(manager, new_student, expected):
    with pytest.raises(expected):
        student = Student(id=new_student['id'], name=new_student['name'],
                          login=new_student['login'], password=new_student['password'],
                          group_id=new_student['group_id'])
        request = manager.generate_insert_request(student)
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
    created_students = [Student(id=8, name='FirstTempStudent', login='FirstTempStudentLogin',
                                password='tempStudentPass1', group_id=15),
                        Student(id=9, name='SecondTempStudent', login='SecondTempStudentLogin',
                                password='tempStudentPass1', group_id=15)]

    for student in created_students:
        insert_request = manager.generate_insert_request(student)
        manager.send_request(insert_request)

    select_request = manager.generate_select_request("group_id={}".format(created_students[0].group_id))
    result = manager.send_request(select_request)

    received_students = get_list_of_students(result)
    assert created_students == received_students


def test_select_not_existed_student(manager):
    not_existing_student = Student(id=13, name='NoStudent', login='NoStudentLogin',
                                   password='NoStudentPass1', group_id=15)
    not_existing_student_select_request = \
        manager.generate_select_request("login={}".format(not_existing_student.login))

    result = manager.send_request(not_existing_student_select_request)
    assert len(result) == 0


def test_update_request(manager):
    created_student = Student(id=10, name='TempStudent', login='TempStudentLogin', password='tempStudentPass1',
                              group_id=3)
    insert_request = manager.generate_insert_request(created_student)
    manager.send_request(insert_request)

    update_request = manager.generate_update_request("login='UpdatedLogin'", "id={}".format(created_student.id))
    manager.send_request(update_request)

    created_student.login = "'UpdatedLogin'"

    find_updated_student_request = manager.generate_select_request("login={}".format(created_student.login))
    student_as_list = manager.send_request(find_updated_student_request)
    student_found = Student(student_as_dict=student_as_list[0])
    assert created_student == student_found


def test_not_existed_student_update(manager):
    with pytest.raises(ProgrammingError):
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
