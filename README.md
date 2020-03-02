# Database testing framework

This is simple database testing program, that uses Python, PyTest and mysql-connector-python to manage testing 
database replication functionality. Also the app provides generating allure test reports.

### Prerequisites

To use the app properly, you need to **MySQL server** be installed and running.
Also for testing replication functionality you need to provide MySQL running at **master-slave mode**.
See more [here](https://tarunlalwani.com/post/mysql-master-slave-using-docker/)

Note: to see generated allure reports you need **allure to be installed** on your computer.
    See more [here](https://docs.qameta.io/allure/#_installing_a_commandline)

### Installing

To install the app:

```
$ git clone

$ cd WorkingWithDatabase

$ python3 -m virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## Running the tests

To run all tests:
```
$ pytest
```
To run specific test:
```
$ pytest test_name.py
```

#### Allure test report

To generate allure test reports:

```
$ pytest --alluredir=/tmp/my_allure_results
```

To see test results:
```
$ allure serve /tmp/my_allure_results
```

## Built With

* [PyTest](https://docs.pytest.org/en/latest/) - Test framework
* [The MySQL Connector](https://dev.mysql.com/doc/index-connectors.html) - driver for MySQL database server connection
* [Allure Test Report](http://allure.qatools.ru/) - a framework designed to create test execution reports
