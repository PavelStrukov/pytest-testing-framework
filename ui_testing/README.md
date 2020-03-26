# UI testing framework

This is simple ui testing program, that uses Python, PyTest and selenium web driver to manage ui testing 
of https://www.python.org/ site.

### Prerequisites

This framework uses Chrome driver, so the Chrome web browser should be installed.
If you want to use this framework with another browser, you need to download another driver and specify it
for browser fixture in conftest.py.
See more [here](https://selenium-python.readthedocs.io/installation.html#drivers)

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

## Built With

* [PyTest](https://docs.pytest.org/en/latest/) - Test framework
* [Selenium Web Driver](https://www.selenium.dev/documentation/en/webdriver/) - Driver for web browser access
