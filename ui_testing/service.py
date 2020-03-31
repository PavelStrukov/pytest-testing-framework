import glob
import hashlib
import os
import time
from pathlib import Path

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import defenitions

"""This module provides essential background work for setup ui testing"""


def clear_downloads(path_to_downloads):
    """Method provides clearing up ui_testing/downloads directory"""
    files = glob.glob(path_to_downloads + "*")

    if len(files) != 0:
        for f in files:
            os.remove(f)


def set_up_downloads_directory(path_to_downloads):
    """Method provides creating ui_testing/downloads directory if it doesn't exist"""
    Path(path_to_downloads).mkdir(parents=True, exist_ok=True)
    clear_downloads(path_to_downloads)


def set_up_chrome_driver(path_to_driver, path_to_downloads):
    """Method provides setting up chrome driver and
    configuring it to provide essential downloading functionality"""

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": path_to_downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=path_to_driver)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': path_to_downloads}}
    driver.execute("send_command", params)

    return driver


def download_wait(directory, nfiles=None):
    """
    Wait for downloads to finish.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds


def get_path_to_downloaded_file():
    """Method returns a string path to recently downloaded file"""
    file = os.listdir(defenitions.PATH_TO_DOWNLOADS)[0]
    return defenitions.PATH_TO_DOWNLOADS + file


def get_md5_checksum(file_path):
    """Method provides counting md5 check sum for downloaded file"""
    with open(file_path, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def get_data_from_yaml(required_data):
    """Method provides extracting definite data from yaml file"""
    path_to_configs = str(defenitions.ROOT_DIR) + "/ui_testing/configs/python_config.yaml"

    with open(path_to_configs, "r") as yml_file:
        data = yaml.load(yml_file, Loader=yaml.FullLoader)[required_data]
        return data


def get_expected_python_version():
    """Method provides getting required python version from config file"""
    return get_data_from_yaml('python_version')


def get_required_search_text():
    """Method provides getting text for searching from config file"""
    return get_data_from_yaml('search_text')


def get_expected_post_history():
    """Method provides getting required post history from config file"""
    return get_data_from_yaml('expected_post_history')


def get_expected_title(title_name):
    path_to_configs = str(defenitions.ROOT_DIR) + "/ui_testing/configs/python_config.yaml"

    with open(path_to_configs, "r") as yml_file:
        title = yaml.load(yml_file, Loader=yaml.FullLoader)["titles"][title_name]
        return title
