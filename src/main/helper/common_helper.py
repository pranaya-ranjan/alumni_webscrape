import datetime
import os

import pygsheets
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from yaml import safe_load, YAMLError

from src.main.utils.actions import login


def get_control_df():
    cfg = get_config()
    sheet_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    client = pygsheets.authorize(service_account_file=sheet_json_path)
    sheet = client.open_by_key(cfg['g_sheet']['sheet_key'])
    control_sheet_wks = sheet.worksheet_by_title(cfg['g_sheet']['control_sheet_title'])
    df = control_sheet_wks.get_as_df(has_header=True, index_column=None)
    return df


def clear_update_control_df(control_df):
    cfg = get_config()
    sheet_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    client = pygsheets.authorize(service_account_file=sheet_json_path)
    sheet = client.open_by_key(cfg['g_sheet']['sheet_key'])
    control_sheet_wks = sheet.worksheet_by_title(cfg['g_sheet']['control_sheet_title'])
    control_sheet_wks.clear()
    control_sheet_wks.set_dataframe(control_df, start=(1, 1))


def get_config():
    conf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), r'../../conf/cfg.yaml'))

    with open(conf_path, 'r') as stream:
        try:
            config = safe_load(stream)
        except YAMLError as exc:
            print(exc)
            raise YAMLError
    return config


def do_login_to_linked_in():
    cfg = get_config()
    chrome_driver_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['chrome_driver_relative_path']))

    options = Options()
    options.headless = cfg['config']['headless']
    driver = webdriver.Chrome(chrome_driver_path, options=options)
    email, password = cfg['login']['email'], cfg['login']['password']
    login(driver, email, password)
    print("Logged in to LinkedIn\n")
    return driver


def get_curr_date():
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")

