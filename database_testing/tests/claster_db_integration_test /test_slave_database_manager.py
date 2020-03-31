import time

import allure
import pytest
from mysql.connector import DatabaseError

from database_testing.src.student import Student
from conftest import get_manager

db_name = "TestDatabase"
table_name = "students"
error_message = "The MySQL server is running with the --read-only option so it cannot execute this statement"
drop_db = "DROP DATABASE IF EXISTS {}"
create_table = "CREATE TABLE IF NOT EXISTS {}.{} (id INT, name VARCHAR(255),login VARCHAR(255)," \
               "password VARCHAR(255), group_id INT) ENGINE=INNODB;"
insert_student_data = [
    ({'id': 1, 'name': 'SomeName', 'login': 'someLogin1', 'password': 'qwerty123', 'group_id': 2}, DatabaseError),
    ({'id': 's', 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 2}, DatabaseError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 1, 'group_id': 2}, TypeError),
    ({'id': 1, 'login': 'someLogin1', 'password': 'qwerty123', 'name': 'SomeName', 'group_id': 's'}, DatabaseError),
]
select_student_data = [
    ("id = 1", {'id': 1, 'name': 'SomeName', 'login': 'someLogin1', 'password': 'qwerty123', 'group_id': 2}),
    ("login = 'someLogin2'", {'id': 2, 'name': 'SomeName2', 'login': 'someLogin2',
                              'password': 'qwerty123', 'group_id': 3}),
    ("name = 'SomeName3'", {'id': 3, 'name': 'SomeName3', 'login': 'someLogin3',
                            'password': 'qwerty123', 'group_id': 4}),
    ("group_id = 2", {'id': 1, 'name': 'SomeName', 'login': 'someLogin1', 'password': 'qwerty123', 'group_id': 2}),
    ("id = 5", {'id': 1, 'name': 'SomeName', 'login': 'someLogin1', 'password': 'qwerty123', 'group_id': 2})
]
update_student_data = [
    ("id = 1", {'id': 1, 'login': 'someNewLogin1', 'password': 'NewPass1', 'name': 'SomeNewName', 'group_id': 5}),
    ("group_id = 10",
     {'id': 1, 'login': 'someNewLogin1', 'password': 'NewPass1', 'name': 'SomeNewName', 'group_id': 10}),
    ("group_id = 5", {'id': 1, 'login': 'someNewLogin1', 'password': 'NewPass1', 'name': 'SomeNewName', 'group_id': 5})
]
delete_student_data = [
    "id = 1", "group_id = 1", "id = 5"
]
update_master_slave_data = [
    ("id = 100", "login = 'someNewLogin100'"),
    ("id = 100", "password = 'NewPass100'"),
    ("id = 100", "name = 'SomeNewName100'"),
    ("id = 100", "group_id = 3"),
]
delete_master_slave_data = [
    "id = 100", "login = 'someNewLogin100'", "name = 'SomeNewName100'", "group_id = 3"
]


@allure.title("With allure step create connection to master")
@pytest.fixture(scope="module")
def master_manager():
    """creating master manager"""
    master_manager = get_manager("master")
    yield master_manager
    master_manager.send_request(drop_db.format(db_name))
    master_manager.close_connection()


@allure.title("With allure step create connection to slave")
@pytest.fixture(scope="module")
def slave_manager():
    """creating slave manager"""
    slave_manager = get_manager("slave")
    yield slave_manager
    slave_manager.close_connection()


@allure.title("With allure step create database from master and check, it is visible from slave")
def test_visibility_of_created_database(master_manager, slave_manager):
    master_manager.send_request("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
    time.sleep(0.05)
    response = slave_manager.send_request("SHOW DATABASES LIKE '{}'".format(db_name))[0]

    master_manager.set_database(db_name)
    slave_manager.set_database(db_name)

    assert db_name in response.values()


@allure.title("With allure step create table from master and check, it is visible from slave")
def test_visibility_of_created_table(master_manager, slave_manager):
    master_manager.send_request(create_table.format(db_name, table_name))

    time.sleep(0.01)

    response = slave_manager.send_request("SHOW TABLES IN {} LIKE '{}'".format(db_name, table_name))

    response = response[0]

    assert table_name in response.values()


@allure.title("With allure step check it is impossible to create database from slave")
def test_creation_db_from_slave(slave_manager):
    with pytest.raises(DatabaseError):
        slave_manager.send_request("CREATE DATABASE IF NOT EXISTS {}".format(db_name))


@allure.title("With allure step check it is impossible to create table from slave")
def test_creation_table_from_slave(slave_manager):
    with pytest.raises(DatabaseError):
        slave_manager.send_request(create_table.format(db_name, table_name))


@allure.title("With allure step check it is impossible to delete table from slave")
def test_deletion_table_from_slave(slave_manager):
    with pytest.raises(DatabaseError):
        slave_manager.send_request("DROP TABLE {}".format(table_name))


@allure.title("With allure step check it is impossible to delete database from slave")
def test_deletion_db_from_slave(slave_manager):
    with pytest.raises(DatabaseError):
        slave_manager.send_request(drop_db.format(db_name))


@allure.title("With allure step check it is impossible to insert student {student_data} from slave")
@pytest.mark.parametrize("student_data, expected", insert_student_data)
def test_insert_statement(slave_manager, student_data, expected):
    with pytest.raises(expected):
        student = Student(id=student_data['id'], name=student_data['name'], login=student_data['login'],
                          password=student_data['password'], group_id=student_data['group_id'])

        insert_request = slave_manager.generate_insert_request(student)

        slave_manager.send_request(insert_request)


@allure.title("With allure step select students with {conditions} from slave")
@pytest.mark.parametrize("conditions, expected", select_student_data)
def test_select_statement(master_manager, slave_manager, conditions, expected):
    insert_student = master_manager.generate_insert_request(Student(student_as_dict=expected))
    master_manager.send_request(insert_student)

    time.sleep(0.02)

    select_student = slave_manager.generate_select_request(conditions)
    response = slave_manager.send_request(select_student)

    if len(response) == 1:
        actual = response[0]
    elif len(response) > 1:
        actual = response
        expected = [expected] * 2
    else:
        actual = response
        expected = []

    assert expected == actual


@allure.title("With allure step check it is impossible to set student with {conditions} "
              "values {student_data} from slave")
@pytest.mark.parametrize("conditions, student_data", update_student_data)
def test_update_statement(master_manager, slave_manager, conditions, student_data):
    insert_student = master_manager.generate_insert_request(Student(student_as_dict=student_data))
    master_manager.send_request(insert_student)

    with pytest.raises(DatabaseError):
        update_student = slave_manager.generate_update_request(str(student_data), conditions)
        slave_manager.send_request(update_student)


@allure.title("With allure step check it is impossible to delete student with {conditions} from slave")
@pytest.mark.parametrize("conditions", delete_student_data)
def test_delete_student(slave_manager, conditions):
    with pytest.raises(DatabaseError):
        delete_student = slave_manager.generate_delete_request(conditions)
        slave_manager.send_request(delete_student)


@allure.title("With allure step check that student inserted from master is visible from slave")
def test_insert_from_master_is_visible_in_slave_request(master_manager, slave_manager):
    student_data = {"id": 100, "login": 'someLogin100', "password": 'qwerty123', "name": 'SomeName100', "group_id": 20}
    student = Student(student_as_dict=student_data)
    master_manager.send_request(master_manager.generate_insert_request(student))

    time.sleep(0.03)

    select_student = slave_manager.generate_select_request("id = 100")
    student = slave_manager.send_request(select_student)[0]

    assert student_data == student


@allure.title("With allure step check that assigned values {update_data} from master "
              "to student with {conditions} is visible from slave")
@pytest.mark.parametrize("conditions, update_data", update_master_slave_data)
def test_update_from_master_is_visible_in_slave_request(master_manager, slave_manager, conditions, update_data):
    update_request = master_manager.generate_update_request(update_data, conditions)
    master_manager.send_request(update_request)

    time.sleep(0.02)

    select_student = slave_manager.generate_select_request(conditions)
    updated_student = slave_manager.send_request(select_student)[0]

    update_data = update_data.split()
    expected = update_data[2].replace("'", "")

    assert str(updated_student[update_data[0]]) == expected


@allure.title("With allure step check when master try to update not existed student, nothing happens")
def test_update_from_master_without_changes_is_visible_in_slave(master_manager, slave_manager):
    update_data = ("id = 500", "login = 'someNewLogin100', password = 'NewPass100', "
                               "name = 'SomeNewName100', group_id = 3")
    table_before_changes = slave_manager.send_request(slave_manager.generate_select_request())

    update_request = master_manager.generate_update_request(update_data[1], update_data[0])
    master_manager.send_request(update_request)

    time.sleep(0.02)

    table_after_changes = slave_manager.send_request(slave_manager.generate_select_request())

    assert table_before_changes == table_after_changes


@allure.title("With allure step check that few students updated from master are visible from slave")
def test_update_few_students_from_master_is_visible_in_slave(master_manager, slave_manager):
    update_name = "SomeNewName100"
    student_1 = {"id": 20, "login": 'someLogin20', "password": 'qwerty20', "name": 'SomeName20', "group_id": 20}
    student_2 = {"id": 21, "login": 'someLogin21', "password": 'qwerty21', "name": 'SomeName21', "group_id": 20}

    students = [student_1, student_2]

    for student in students:
        insert_student = master_manager.generate_insert_request(Student(student_as_dict=student))
        master_manager.send_request(insert_student)
        student['name'] = "SomeNewName100"

    update_student = master_manager.generate_update_request("name = '{}'".format(update_name),
                                                            "group_id = {}".format(student_1['group_id']))
    master_manager.send_request(update_student)

    time.sleep(0.02)

    select_students = slave_manager.generate_select_request("group_id = {}".format(student_1['group_id']))

    response = slave_manager.send_request(select_students)

    assert students == response


@allure.title("With allure step check that student with {conditions} "
              "deleted from master isn't visible from slave")
@pytest.mark.parametrize("conditions", delete_master_slave_data)
def test_delete_from_master_is_visible_in_slave(master_manager, slave_manager, conditions):
    insert_request = master_manager.generate_insert_request(Student(id=100, name='SomeNewName100',
                                                                    login='someNewLogin100', password='qwerty123',
                                                                    group_id=3))
    master_manager.send_request(insert_request)

    delete_request = master_manager.generate_delete_request(conditions)
    master_manager.send_request(delete_request)

    time.sleep(0.02)

    select_student = slave_manager.generate_select_request(conditions)
    response = slave_manager.send_request(select_student)

    assert response == []


@allure.title("With allure step check when master try to delete not existed student, nothing happens")
def test_delete_from_master_without_changes_is_visible_in_slave(master_manager, slave_manager):
    table_before_changes = slave_manager.send_request(slave_manager.generate_select_request())

    delete_request = master_manager.generate_delete_request("id = 200")
    master_manager.send_request(delete_request)

    time.sleep(0.02)

    table_after_changes = slave_manager.send_request(slave_manager.generate_select_request())

    assert table_before_changes == table_after_changes


@allure.title("With allure step check that few students updated from master are visible from slave")
def test_delete_few_students_from_master_is_visible_in_slave(master_manager, slave_manager):
    all_students_before_changes = slave_manager.send_request(slave_manager.generate_select_request())

    delete_students = master_manager.generate_delete_request("group_id = 20")
    master_manager.send_request(delete_students)

    time.sleep(0.02)

    all_students_after_changes = slave_manager.send_request(slave_manager.generate_select_request())

    students_without_definite_students = [student for student in all_students_before_changes if
                                          student['group_id'] != 20]

    assert students_without_definite_students == all_students_after_changes
