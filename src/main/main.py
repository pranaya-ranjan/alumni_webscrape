import datetime

from src.main.helper.common_helper import get_curr_date, get_config, get_control_df, \
    clear_update_control_df
from src.main.helper.ws_helper import do_web_scrapping_for_profile_id_list, do_ws_task
from src.main.utils.constants import NEW_STATUS, SUCCESS_STATUS, LINKEDIN_SPECIFIC_COLUMN_LIST
import pandas as pd


def get_all_aan_people(aan_people_url):
    # Web Scrapping happening here
    # Returns list of PROFILE_ID
    return do_web_scrapping_for_profile_id_list(aan_people_url)


def _is_any_record_exist_gs(status_list):
    all_df = get_control_df()
    if len(all_df) == 0:
        return False

    active_df = all_df[all_df['PROFILE_ACTIVE'] == 'Y']
    req_df = active_df[active_df.WEB_SCRAP_STATUS.isin(status_list)]
    return len(req_df) > 0  # req_df.empty


def set_all_profile_disabled_gs():
    all_df = get_control_df()
    all_df['PROFILE_ACTIVE'] = "N"
    clear_update_control_df(all_df)


def insert_update_profile_gs(profiles, day):
    all_df = get_control_df()
    new_df = pd.DataFrame(profiles, columns=['NAME', 'LinkedIn Profile URL'])
    new_df['PROFILE_ACTIVE'] = "Y"
    new_df['LAST_ACTIVE_DATE'] = day
    new_df['WEB_SCRAP_STATUS'] = NEW_STATUS

    new_df['Educations'] = ''
    for linkedin_col in LINKEDIN_SPECIFIC_COLUMN_LIST:
        new_df[linkedin_col] = ''

    new_all_df = pd.concat([all_df, new_df]).drop_duplicates(['LinkedIn Profile URL'], keep='last')
    # df1 = df1.set_index('LinkedIn Profile URL')  # When Sheet is empty, PROFILE_ID does not exist
    # df2 = df2.set_index('LinkedIn Profile URL')
    # df1.update(df2)
    # df1.reset_index(inplace=True)
    clear_update_control_df(new_all_df)


def do_web_scrape_all_profile_id(aan_people_url, date):
    profile_id_from_linkedin = get_all_aan_people(aan_people_url)
    set_all_profile_disabled_gs()
    insert_update_profile_gs(profile_id_from_linkedin, date)


def get_last_ws_date():
    all_df = get_control_df()
    if len(all_df['LAST_ACTIVE_DATE']) == 0:
        return '2021-01-01'

    return max(all_df['LAST_ACTIVE_DATE'])


def do_main_task():
    exc_status_list = [NEW_STATUS, SUCCESS_STATUS]
    date = get_curr_date()
    config = get_config()
    aan_people_url = config['linkedin']['aan.people.url']

    # Fetch all active record from control sheet
    is_present = _is_any_record_exist_gs(exc_status_list)

    if is_present:
        do_ws_task()
    else:
        last_ws_date = get_last_ws_date()
        delta = datetime.date.today() - datetime.datetime.strptime(last_ws_date, "%Y-%m-%d").date()
        config_sch_diff = config['config']['ws_schedule_days_diff']
        # This will make sure, Web scrap will happen only once during this period
        if delta.days > config_sch_diff:
            do_web_scrape_all_profile_id(aan_people_url, date)
        else:
            return


# main function to run the script.
if __name__ == '__main__':
    do_main_task()
