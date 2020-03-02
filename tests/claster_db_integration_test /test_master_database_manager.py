import pytest
import yaml
from mysql.connector import ProgrammingError

from defenitions import ROOT_DIR
from src.database_manager import DatabaseManager
from src.student import Student

db_name = "TestDatabase"
table_name = "students"


@pytest.fixture(scope="module")
def manager():
    with open(str(ROOT_DIR) + "/configs/database_replication_config.yml", "r") as yml_file:
        db_cfg = yaml.load(yml_file, Loader=yaml.FullLoader)['mysql']
        db_master_cfg = db_cfg['master']
        manager = DatabaseManager([db_master_cfg['user'], db_master_cfg['password']], db_master_cfg['host'],
                                  db_master_cfg['port'])

        yield manager
        manager.send_request("DROP DATABASE IF EXISTS {}".format(db_name))
        manager.close_connection()


def test_creation_database(manager):
    manager.send_request("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
    response = manager.send_request("SHOW DATABASES LIKE '{}'".format(db_name))[0]

    manager.set_database(db_name)
    assert db_name in response.values()


def test_creation_table(manager):
    manager.send_request("CREATE TABLE IF NOT EXISTS {}.{} ("
                         "id INT,"
                         "name VARCHAR(255),"
                         "login VARCHAR(255),"
                         "password VARCHAR(255),"
                         "group_id INT) "
                         "ENGINE=INNODB;".format(db_name, table_name))

    response = manager.send_request("SHOW TABLES IN {} LIKE '{}'".format(db_name, table_name))[0]

    assert table_name in response.values()


def test_positive_insert_statement(manager):
    student = Student(id=1, name='SomeName', login='someLogin1',
                      password='qwerty123', group_id=2)

    insert_request = manager.generate_insert_request(student)
    response = manager.send_request(insert_request)

    assert response is None

    select_request = manager.generate_select_request('id=1')
    response = manager.send_request(select_request)
    got_student = Student(student_as_dict=response[0])

    assert student == got_student


insert_negative_student_data = [
    ({'id': 's', 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 2}, ProgrammingError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 1, 'group_id': 2}, TypeError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 's'}, ProgrammingError),
]


@pytest.mark.parametrize("student_data, expected", insert_negative_student_data)
def test_negative_insert_statement(manager, student_data, expected):
    with pytest.raises(expected):
        student = Student(id=student_data['id'], name=student_data['name'], login=student_data['login'],
                          password=student_data['password'], group_id=student_data['group_id'])

        insert_request = manager.generate_insert_request(student)

        manager.send_request(insert_request)


select_positive_student_data = [
    (("id", 1), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("login", "'someLogin1'"), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("name", "'SomeName'"), Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2)),
    (("group_id", 2),
     [Student(id=1, name='SomeName', login='someLogin1', password='qwerty123', group_id=2).__dict__, ]),
    (("id", 5), [])
]


@pytest.mark.parametrize("conditions, expected", select_positive_student_data)
def test_positive_select_statement(manager, conditions, expected):
    new_student = Student(id=2, name="NewStudentName", login="NewStudentLogin",
                          password="newStudentPassword", group_id=2)
    insert_request = manager.generate_insert_request(new_student)
    manager.send_request(insert_request)

    select_request = manager.generate_select_request(conditions[0] + "=" + str(conditions[1]))

    response = manager.send_request(select_request)

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


def test_update_single_student(manager):
    student = {'id': 1, "login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName', "group_id": 5}

    insert_request = manager.generate_insert_request(Student(student_as_dict=student))
    manager.send_request(insert_request)

    string_data = "name = '{}', login = '{}', password = '{}', group_id = {}".format(student['name'],
                                                                                     student['login'],
                                                                                     student['password'],
                                                                                     student['group_id'])

    update_request = manager.generate_update_request(string_data, 'id = ' + str(student['id']))

    manager.send_request(update_request)

    get_updated_student_request = manager.generate_select_request("name = '{}'".format(student['name']))

    updated_student = manager.send_request(get_updated_student_request)[0]

    assert updated_student == student


def test_update_few_students(manager):
    student_1 = {'id': 3, "login": 'someLogin4', "password": 'Pass4', "name": 'SomeName4', "group_id": 10}
    student_2 = {'id': 4, "login": 'someLogin5', "password": 'Pass5', "name": 'SomeName5', "group_id": 10}

    students = [student_1, student_2]

    update_data = {"login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName'}
    for student in students:
        insert_request = manager.generate_insert_request(Student(student_as_dict=student))
        manager.send_request(insert_request)

        for key in update_data.keys():
            student[key] = update_data[key]

    string_update_data = "name = '{}', login = '{}', password = '{}'".format(update_data['name'],
                                                                             update_data['login'],
                                                                             update_data['password'])

    update_request = manager.generate_update_request(string_update_data, 'group_id = {}'.format(student_1['group_id']))
    manager.send_request(update_request)

    select_request = manager.generate_select_request("group_id = {}".format(student_1['group_id']))

    response = manager.send_request(select_request)

    assert students == response


def test_update_not_existed_student(manager):
    update_data = {"id": 5, "login": 'someNewLogin1', "password": 'NewPass1', "name": 'SomeNewName', "group_id": 5}

    string_update_data = "name = '{}', login = '{}', password = '{}', group_id = {}".format(update_data['name'],
                                                                                            update_data['login'],
                                                                                            update_data['password'],
                                                                                            update_data['group_id'])

    update_request = manager.generate_update_request(string_update_data, "id = 5")

    manager.send_request(update_request)

    all_students = manager.send_request(manager.generate_select_request())

    assert update_data not in all_students


delete_data = [
    [{"id": 1, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}, ],
    [{"id": 1, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1},
     {"id": 2, "login": 'Login2', "password": 'Pass2', "name": 'wName2', "group_id": 1}],
    [{"id": 5, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}, ]
]


@pytest.mark.parametrize("delete_student", delete_data)
def test_delete_student(manager, delete_student):
    for student in delete_student:
        insert_request = manager.generate_insert_request(Student(student_as_dict=student))
        manager.send_request(insert_request)

    if len(delete_student) > 1:
        student = delete_student[0]
        condition = "group_id = " + str(student["group_id"])
    else:
        student = delete_student[0]
        condition = "id = " + str(student["id"])

    delete_request = manager.generate_delete_request(condition)

    manager.send_request(delete_request)

    all_students = manager.send_request(manager.generate_select_request())

    assert delete_student not in all_students


def test_delete_not_existed_student(manager):
    students_before_changes = manager.send_request(manager.generate_select_request())

    not_existing_student = {"id": 5, "login": 'Login1', "password": 'Pass1', "name": 'wName', "group_id": 1}

    delete_request = manager.generate_delete_request("id = {}".format(not_existing_student['id']))

    manager.send_request(delete_request)

    students_after_changes = manager.send_request(manager.generate_select_request())

    assert students_before_changes == students_after_changes


def test_incorrect_insert_statement(manager):
    with pytest.raises(ProgrammingError):
        data = ['id_', 1, 'login_name', 'name_', 'SomeName',
                'someLogin1', 'password_', 'qwerty123', 'group_id_', 2]

        insert_request = "INSERT INTO students (id, name, login, password, group_id) VALUES ({}, {}, {}, {}, {});" \
            .format(data[0], data[2], data[4], data[6], data[8], data[1], data[3], data[5], data[7])

        manager.send_request(insert_request)


incorrect_update_data = [
    ['id_ = 1', 'login_name = someLogin1'],
    ['id_ = 1', 'password_ = qwerty123'],
    ['id_ = 1', 'name_ = SomeName'],
    ['id_ = 1', 'group_id_ = 3'],
]


@pytest.mark.parametrize("data", incorrect_update_data)
def test_incorrect_update_statement(manager, data):
    with pytest.raises(ProgrammingError):
        update_request = manager.generate_update_request(data[1], data[0])

        manager.send_request(update_request)


incorrect_select_data = ['id_ = 1', 'login_name = someLogin1', 'password_ = qwerty123',
                         'name_ = SomeName', 'group_id_ = 3']


@pytest.mark.parametrize("data", incorrect_select_data)
def test_incorrect_select_statement(manager, data):
    with pytest.raises(ProgrammingError):
        select_request = manager.generate_select_request(data)

        manager.send_request(select_request)


incorrect_delete_data = ['id_ = 1', 'login_name = someLogin1',
                         'name_ = SomeName', 'group_id_ = 3']


@pytest.mark.parametrize("data", incorrect_delete_data)
def test_incorrect_delete_statement(manager, data):
    with pytest.raises(ProgrammingError):
        delete_request = manager.generate_delete_request(data)

        manager.send_request(delete_request)
