# Pytest testing framework

This is simple testing program, that uses Python and PyTest in common case. It consists of two directories:
* database_testing contains tests for testing database single instance and replication in master-slave mode
* ui_testing contains tests for UI testing https://www.python.org/ site

# UI testing

This is simple UI testing program, that uses Python, PyTest and selenium web driver to manage UI testing 
of https://www.python.org/ site.

### Prerequisites

This framework uses Chrome driver, so the Chrome web browser should be installed.
If you want to use this framework with another browser, you need to download another driver and specify it
for browser fixture in conftest.py.
See more [here](https://selenium-python.readthedocs.io/installation.html#drivers)

### Installing

To install the app:

```
$ git clone https://github.com/PavelStrukov/pytest-testing-framework.git

$ cd pytest-testing-framework

$ python3 -m virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

# Database testing

This is simple database testing program, that uses Python, PyTest and mysql-connector-python to manage testing 
database replication functionality. Also the app provides generating allure test reports.

### Prerequisites

To use the app properly, you need to **MySQL server** be installed and running.
Also for testing replication functionality you need to provide MySQL running at **master-slave mode**.
See more [here](https://tarunlalwani.com/post/mysql-master-slave-using-docker/)

Note: to see generated allure reports you need **allure to be installed** on your computer.
    See more [here](https://docs.qameta.io/allure/#_installing_a_commandline)

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
* [Selenium Web Driver](https://www.selenium.dev/documentation/en/webdriver/) - Driver for web browser access
* [The MySQL Connector](https://dev.mysql.com/doc/index-connectors.html) - driver for MySQL database server connection
* [Allure Test Report](http://allure.qatools.ru/) - a framework designed to create test execution reports
