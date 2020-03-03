import pytest
import allure
from mysql.connector import ProgrammingError

from src.student import Student
from conftest import get_manager

db_name = "TestDatabase"
table_name = "students"

drop_database = "DROP DATABASE IF EXISTS {}"
create_table = "CREATE TABLE IF NOT EXISTS {}.{} (id INT, name VARCHAR(255),login VARCHAR(255)," \
               "password VARCHAR(255), group_id INT) ENGINE=INNODB;"
insert_negative_student_data = [
    ({'id': 's', 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 2}, ProgrammingError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 1, 'group_id': 2}, TypeError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 's'}, ProgrammingError),
]
select_positive_student_data = [
    (("id", 1), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("login", "'someLogin1'"), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("name", "'SomeName'"), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("group_id", 2),
     [Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2).__dict__, ]),
    (("id", 5), [])
]
delete_data = [
    [{"id": 1, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}, ],
    [{"id": 1, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1},
     {"id": 2, "login": 'Login2', "password": 'Pass2', "name": 'wName2', "group_id": 1}],
    [{"id": 5, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}, ]
]
incorrect_update_data = [
    ['id_ = 1', 'login_name = someLogin1'],
    ['id_ = 1', 'password_ = qwerty123'],
    ['id_ = 1', 'name_ = SomeName'],
    ['id_ = 1', 'group_id_ = 3'],
]
incorrect_select_data = ['id_ = 1', 'login_name = someLogin1', 'password_ = qwerty123',
                         'name_ = SomeName', 'group_id_ = 3']
incorrect_delete_data = ['id_ = 1', 'login_name = someLogin1',
                         'name_ = SomeName', 'group_id_ = 3']


@allure.title("With allure step create connection to master")
@pytest.fixture(scope="module")
def master_manager():
    master_manager = get_manager("master")
    yield master_manager
    master_manager.send_request(drop_database.format(db_name))
    master_manager.close_connection()


@allure.title("With allure step check, it is possible to create database from master")
def test_creation_database(master_manager):
    master_manager.send_request("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
    response = master_manager.send_request("SHOW DATABASES LIKE '{}'".format(db_name))[0]

    master_manager.set_database(db_name)
    assert db_name in response.values()


@allure.title("With allure step check, it is possible to create table from master")
def test_creation_table(master_manager):
    master_manager.send_request(create_table.format(db_name, table_name))

    response = master_manager.send_request("SHOW TABLES IN {} LIKE '{}'".format(db_name, table_name))[0]

    assert table_name in response.values()


@allure.title("With allure step insert student from master")
def test_positive_insert_statement(master_manager):
    student = Student(id=1, name='SomeName', login='someLogin1',
                      password='qwerty123', group_id=2)

    insert_request = master_manager.generate_insert_request(student)
    response = master_manager.send_request(insert_request)

    assert response is None

    select_request = master_manager.generate_select_request('id=1')
    response = master_manager.send_request(select_request)
    got_student = Student(student_as_dict=response[0])

    assert student == got_student


@allure.title("With allure step check, it is impossible to insert "
              "incorrect student data {student_data} from master")
@pytest.mark.parametrize("student_data, expected", insert_negative_student_data)
def test_negative_insert_statement(master_manager, student_data, expected):
    with pytest.raises(expected):
        student = Student(id=student_data['id'], name=student_data['name'], login=student_data['login'],
                          password=student_data['password'], group_id=student_data['group_id'])

        insert_request = master_manager.generate_insert_request(student)

        master_manager.send_request(insert_request)


@allure.title("With allure step select students from master")
@pytest.mark.parametrize("conditions, expected", select_positive_student_data)
def test_positive_select_statement(master_manager, conditions, expected):
    new_student = Student(id=2, name="NewStudentName", login="NewStudentLogin",
                          password="newStudentPassword", group_id=2)
    insert_request = master_manager.generate_insert_request(new_student)
    master_manager.send_request(insert_request)

    select_request = master_manager.generate_select_request(conditions[0] + "=" + str(conditions[1]))

    response = master_manager.send_request(select_request)

    if len(response) > 1:
        response = response[:2]
        expected.append(new_student.__dict__)
        for student in expected:
            for key, value in student.items():
                if isinstance(value, str):
                    student[key] = eval(value)  # remove redundant quotes
    elif len(response) != 0:
        response = Student(student_as_dict=response[0])

    assert expected == response


@allure.title("With allure step update student from master")
def test_update_single_student(master_manager):
    student = {'id': 1, "login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName', "group_id": 5}

    insert_request = master_manager.generate_insert_request(Student(student_as_dict=student))
    master_manager.send_request(insert_request)

    string_data = "name = '{}', login = '{}', password = '{}', group_id = {}".format(student['name'],
                                                                                     student['login'],
                                                                                     student['password'],
                                                                                     student['group_id'])

    update_request = master_manager.generate_update_request(string_data, 'id = ' + str(student['id']))

    master_manager.send_request(update_request)

    get_updated_student_request = master_manager.generate_select_request("name = '{}'".format(student['name']))

    updated_student = master_manager.send_request(get_updated_student_request)[0]

    assert updated_student == student


@allure.title("With allure step update few students from master")
def test_update_few_students(master_manager):
    student_1 = {'id': 3, "login": 'someLogin4', "password": 'Pass4', "name": 'SomeName4', "group_id": 10}
    student_2 = {'id': 4, "login": 'someLogin5', "password": 'Pass5', "name": 'SomeName5', "group_id": 10}

    students = [student_1, student_2]

    update_data = {"login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName'}
    for student in students:
        insert_request = master_manager.generate_insert_request(Student(student_as_dict=student))
        master_manager.send_request(insert_request)

        for key in update_data.keys():
            student[key] = update_data[key]

    string_update_data = "name = '{}', login = '{}', password = '{}'".format(update_data['name'],
                                                                             update_data['login'],
                                                                             update_data['password'])

    update_request = master_manager.generate_update_request(string_update_data,
                                                            'group_id = {}'.format(student_1['group_id']))
    master_manager.send_request(update_request)

    select_request = master_manager.generate_select_request("group_id = {}".format(student_1['group_id']))

    response = master_manager.send_request(select_request)

    assert students == response


@allure.title("With allure step update not existed student from master")
def test_update_not_existed_student(master_manager):
    update_data = {"id": 5, "login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName', "group_id": 5}

    string_update_data = "name = '{}', login = '{}', password = '{}', group_id = {}".format(update_data['name'],
                                                                                            update_data['login'],
                                                                                            update_data['password'],
                                                                                            update_data['group_id'])

    update_request = master_manager.generate_update_request(string_update_data, "id = 5")

    master_manager.send_request(update_request)

    all_students = master_manager.send_request(master_manager.generate_select_request())

    assert update_data not in all_students


@allure.title("With allure step delete student from master")
@pytest.mark.parametrize("delete_student", delete_data)
def test_delete_student(master_manager, delete_student):
    for student in delete_student:
        insert_request = master_manager.generate_insert_request(Student(student_as_dict=student))
        master_manager.send_request(insert_request)

    if len(delete_student) > 1:
        student = delete_student[0]
        condition = "group_id = " + str(student["group_id"])
    else:
        student = delete_student[0]
        condition = "id = " + str(student["id"])

    delete_request = master_manager.generate_delete_request(condition)

    master_manager.send_request(delete_request)

    all_students = master_manager.send_request(master_manager.generate_select_request())

    assert delete_student not in all_students


@allure.title("With allure step delete not existed student from master")
def test_delete_not_existed_student(master_manager):
    students_before_changes = master_manager.send_request(master_manager.generate_select_request())

    not_existing_student = {"id": 5, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}

    delete_request = master_manager.generate_delete_request("id = {}".format(not_existing_student['id']))

    master_manager.send_request(delete_request)

    students_after_changes = master_manager.send_request(master_manager.generate_select_request())

    assert students_before_changes == students_after_changes


@allure.title("With allure step check, it is impossible to execute incorrect insert request from master")
def test_incorrect_insert_statement(master_manager):
    with pytest.raises(ProgrammingError):
        data = ['id_', 1, 'login_name', 'name_', 'SomeName',
                'someLogin1', 'password_', 'qwerty123', 'group_id_', 2]

        insert_request = "INSERT INTO students (id, name, login, password, group_id) VALUES ({}, {}, {}, {}, {});" \
            .format(data[0], data[2], data[4], data[6], data[8], data[1], data[3], data[5], data[7])

        master_manager.send_request(insert_request)


@allure.title("With allure step check, it is impossible to execute incorrect update request from master")
@pytest.mark.parametrize("data", incorrect_update_data)
def test_incorrect_update_statement(master_manager, data):
    with pytest.raises(ProgrammingError):
        update_request = master_manager.generate_update_request(data[1], data[0])

        master_manager.send_request(update_request)


@allure.title("With allure step check, it is impossible to execute incorrect select request from master")
@pytest.mark.parametrize("data", incorrect_select_data)
def test_incorrect_select_statement(master_manager, data):
    with pytest.raises(ProgrammingError):
        select_request = master_manager.generate_select_request(data)

        master_manager.send_request(select_request)


@allure.title("With allure step check, it is impossible to execute incorrect delete request from master")
@pytest.mark.parametrize("data", incorrect_delete_data)
def test_incorrect_delete_statement(master_manager, data):
    with pytest.raises(ProgrammingError):
        delete_request = master_manager.generate_delete_request(data)

        master_manager.send_request(delete_request)
