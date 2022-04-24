import os

import pandas as pd
import pygsheets

from src.main.domain.company import Company
from src.main.domain.person import Person
from src.main.helper.common_helper import do_login_to_linked_in, get_config, get_control_df, clear_update_control_df
from src.main.utils.constants import MASTER_SHEET_REQ_COLUMN_LIST, LINKEDIN_SPECIFIC_COLUMN_LIST, \
    MASTER_SHEET_SPECIFIC_COLUMN_LIST, NEW_STATUS, SUCCESS_STATUS, CLOSED_STATUS


def get_prof_dict():
    profile_dict = {
        'Name': '',
        'LinkedIn Profile URL': '',
        'Job Title': '',
        'Company': '',
        'Location': '',
        'About': '',
        'Educations': '',
        'Experiences': '',
        'Interests': '',
        'Accomplishments': ''
    }
    return profile_dict


def extract_degree(degree_str):
    degree = str(degree_str).lower()

    if 'ph.d' in degree or ' phd ' in degree or 'doctor of philosophy' in degree:
        return 'PhD'
    elif 'm.d ' in degree or ' md ' in degree or 'doctor of medicine' in degree:
        return 'PhD'
    # Master Degree
    elif 'm.tech' in degree or ' mtech ' in degree or 'master of technology' in degree:
        return 'M.Tech'
    elif ' m.e ' in degree or 'master of engineering' in degree:
        return 'M.E'
    elif ' m.sc ' in degree or ' msc ' in degree or 'master of science' in degree:
        return 'M.Sc'
    elif ' m.s ' in degree or ' ms ' in degree:
        return 'M.S'
    elif ' mba ' in degree or 'master of business administration' in degree:
        return 'MBA'
    elif 'executive mba' in degree:
        return 'Executive MBA'
    elif ' mbbs ' in degree or 'bachelor of medicine, bachelor of surgery' in degree:
        return 'MBBS'
    elif ' mca ' in degree or 'master of computer applications' in degree:
        return 'MCA'
    elif ' mpharm ' in degree or ' m.pharm ' in degree:
        return 'M.Pharm'
    elif ' march ' in degree or ' m.arch ' in degree or 'master of architecture' in degree:
        return 'M.Arch'
    elif 'm.phil' in degree or 'mphil' in degree or 'master of philosophy' in degree:
        return 'M.Phil'
    # Graduate
    elif ' b.tech ' in degree or ' btech ' in degree or 'bachelor of technology' in degree:
        return 'B.Tech'
    elif ' b.e ' in degree or 'bachelor of engineering' in degree:
        return 'B.E'
    elif ' b.sc ' in degree or ' bsc ' in degree or 'bachelor of science' in degree:
        return 'B.Sc'
    elif 'b.s' in degree or 'bs' in degree:
        return ' B.S '
    elif ' bpharm ' in degree or ' b.pharm ' in degree:
        return 'B.Pharm'
    elif ' barch ' in degree or ' b.arch ' in degree or 'bachelor of architecture' in degree:
        return 'B.Arch'
    elif ' bba ' in degree or 'bachelor of business administration' in degree:
        return 'BBA'
    else:
        return 'Other'


def extract_institution_type(inst_str):
    inst = str(inst_str).lower()

    if 'indian institute of technology' in inst:
        return 'IIT'
    elif 'national institute of technology' in inst:
        return 'NIT'
    elif 'indian institute of information technology' in inst:
        return 'IIIT'
    elif 'jawahar navodaya vidyalaya' in inst:
        return 'JNV'
    else:
        return 'Other'


def do_web_scrapping_for_profile_details(profile_id_url_list):
    linkedin_info_list = []
    driver = do_login_to_linked_in()

    for linkedin_profile_url in profile_id_url_list:
        profile_dict = get_prof_dict()
        prof_url = linkedin_profile_url
        person = Person(linkedin_url=prof_url, name=None, about=[], experiences=[], educations=[],
                        interests=[], accomplishments=[], company=None, job_title=None, driver=driver, scrape=True,
                        close_on_complete=False)

        profile_dict['LinkedIn Profile URL'] = str(prof_url)
        profile_dict['Job Title'] = str(person.job_title)
        profile_dict['Company'] = str(person.company)
        profile_dict['Location'] = str(person.location)

        profile_dict['About'] = ''
        if len(person.about) > 0:
            profile_dict['About'] = str(person.about)

        profile_dict['Educations'] = ''
        if len(person.educations) > 0:
            profile_dict['Educations'] = extract_degree(person.educations[0].degree)
            profile_dict['Name of Degree'] = person.educations[0].degree
            institution = person.educations[0].institution_name.split(', ')
            profile_dict['Name of the College'] = institution[0]
            if len(institution) > 1:
                profile_dict['College Location'] = institution[1]
            profile_dict['Type of College'] = extract_institution_type(institution[0])
            profile_dict['Branch'] = person.educations[0].major

        profile_dict['JNV Name'] = ''
        for education in person.educations:
            if extract_institution_type(education.institution_name) == 'JNV':
                jnv = education.institution_name.split(', ')
                if len(jnv) > 1:
                    profile_dict['JNV Name'] = jnv[1]
                break

        profile_dict['Experiences'] = ''
        if len(person.experiences) > 0:
            profile_dict['Experiences'] = str(person.experiences)

        profile_dict['Interests'] = ''
        if len(person.interests) > 0:
            profile_dict['Interests'] = str(person.interests)

        profile_dict['Accomplishments'] = ''
        if len(person.accomplishments) > 0:
            profile_dict['Accomplishments'] = str(person.accomplishments)

        linkedin_info_list.append(profile_dict)

    # pprint(linkedin_info_list)
    driver.quit()
    return linkedin_info_list


def clear_update_sheet(tuple_list, column_list, sheet_key, sheet_title):
    cfg = get_config()
    profile_df = pd.DataFrame(tuple_list, columns=column_list)
    client_secret_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    client = pygsheets.authorize(service_account_file=client_secret_json_path)
    sheet = client.open_by_key(sheet_key)
    wks = sheet.worksheet_by_title(sheet_title)
    wks.clear()
    wks.set_dataframe(profile_df, start=(1, 1))


def clear_update_sheet_gs(profile_df, sheet_key, sheet_title):
    cfg = get_config()
    client_secret_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    client = pygsheets.authorize(service_account_file=client_secret_json_path)
    sheet = client.open_by_key(sheet_key)
    wks = sheet.worksheet_by_title(sheet_title)
    wks.clear()
    wks.set_dataframe(profile_df, start=(1, 1))


def merge_master_data_and_update_sheet(web_scrapped_profile_list, columns):
    cfg = get_config()
    sheet_key = cfg['g_sheet']['sheet_key']
    sheet_title = cfg['g_sheet']['sheet_title_1']
    master_sheet_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    master_client = pygsheets.authorize(service_account_file=master_sheet_json_path)
    master_sheet = master_client.open_by_key(cfg['g_sheet']['sheet_key'])
    # (cfg['g_sheet']['master_sheet_key']) todo update
    master_wks = master_sheet.worksheet_by_title(cfg['g_sheet']['master_sheet_title_1'])
    master_values_list = master_wks.get_all_values()
    master_df = pd.DataFrame(master_values_list[1:])
    master_df.columns = master_values_list[0]
    master_sheet_req_columns = MASTER_SHEET_REQ_COLUMN_LIST

    merged_profile_list = []
    linkedin_ids = []

    # Linked In Profiles
    for profile in web_scrapped_profile_list:
        linkedin_ids.append(profile[1])
        master_data_profiles = master_df[master_df['LinkedIn Profile Link'] == profile[1]]
        if len(master_data_profiles) == 1:
            master_df_prof_data = []
            for col in master_sheet_req_columns:
                master_df_prof_data.append(master_data_profiles[col].array[0])
                # Panda Series - master_data_profiles[col]
            merged_profile = profile + tuple(master_df_prof_data)
            merged_profile_list.append(merged_profile)

        else:
            master_df_prof_data = []
            for col in master_sheet_req_columns:
                master_df_prof_data.append('')
            merged_profile = profile + tuple(master_df_prof_data)
            merged_profile_list.append(merged_profile)

    # Profile Does not exist in Linked In but in Master Sheet
    for index, row in master_df.iterrows():
        if row['LinkedIn Profile Link'] not in linkedin_ids:
            profile = (row['Full Name'], row['LinkedIn Profile Link'], '', '', '', '',
                       row['Name of Degree'] + row['Branch'], '', '', '')
            master_df_prof_data = []
            for col in master_sheet_req_columns:
                master_df_prof_data.append(row[col])

            merged_profile = profile + tuple(master_df_prof_data)
            merged_profile_list.append(merged_profile)

    clear_update_sheet(merged_profile_list, columns + master_sheet_req_columns, sheet_key, sheet_title)


def merge_master_data_and_update_sheet_gs(ws_profile_df):
    cfg = get_config()
    sheet_key = cfg['g_sheet']['sheet_key']
    sheet_master_linkedin = cfg['g_sheet']['sheet_title_1']
    sheet_linkedin = cfg['g_sheet']['sheet_title_2']

    clear_update_sheet_gs(ws_profile_df, sheet_key, sheet_linkedin)

    master_sheet_json_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), cfg['paths']['client_secret_json_relative_path']))
    master_client = pygsheets.authorize(service_account_file=master_sheet_json_path)
    master_sheet = master_client.open_by_key(cfg['g_sheet']['master_sheet_key'])
    master_worksheet = master_sheet.worksheet_by_title(cfg['g_sheet']['master_sheet_title_1'])
    master_df = master_worksheet.get_as_df(has_header=True, index_column=None)
    master_columns = ["Full Name", "LinkedIn Profile Link"] + MASTER_SHEET_REQ_COLUMN_LIST
    req_master_df = master_df[master_columns]
    req_master_df.rename(columns={"Full Name": 'NAME'}, inplace=True)
    req_master_df.rename(columns={"Type of Degree": 'Educations'}, inplace=True)
    req_master_df.rename(columns={"LinkedIn Profile Link": 'LinkedIn Profile URL'}, inplace=True)

    # Making two dataframes Dame by columns
    for linkedin_col in LINKEDIN_SPECIFIC_COLUMN_LIST:
        req_master_df[linkedin_col] = ''

    for linkedin_col in MASTER_SHEET_SPECIFIC_COLUMN_LIST:
        ws_profile_df[linkedin_col] = ''

    # Adding a new column user id based on existing columns value
    req_master_df['userId'] = req_master_df.apply(userid_conditions, axis=1)
    ws_profile_df['userId'] = ws_profile_df.apply(userid_conditions, axis=1)

    # Remove if userId is null or empty
    req_master_df = req_master_df.query("userId != ''")
    ws_profile_df = ws_profile_df.query("userId != ''")

    req_master_df['userId'] = req_master_df['userId'].map(str)
    ws_profile_df['userId'] = ws_profile_df['userId'].map(str)

    req_master_df['userId'] = req_master_df['userId'].str.replace(r'https://www.linkedin.com/', '') \
        .str.replace(r'/', '_').str.replace(r' ', '_')
    ws_profile_df['userId'] = ws_profile_df['userId'].str.replace(r'https://www.linkedin.com/', '') \
        .str.replace(r'/', '_')

    if len(ws_profile_df) > 0 and len(req_master_df) > 0:
        ws_profile_df = ws_profile_df.set_index('userId')
        req_master_df = req_master_df.set_index('userId')
        req_master_df.update(ws_profile_df)

        new_all_df = pd.concat([req_master_df, ws_profile_df])

        req_master_df.reset_index(inplace=True)
        ws_profile_df.reset_index(inplace=True)
        new_all_df.reset_index(inplace=True)

        new_all_df.drop_duplicates(['userId'], keep='first')
        clear_update_sheet_gs(new_all_df, sheet_key, sheet_master_linkedin)
    elif len(ws_profile_df) > 0:
        clear_update_sheet_gs(req_master_df, sheet_key, sheet_master_linkedin)
    elif len(req_master_df) > 0:
        clear_update_sheet_gs(ws_profile_df, sheet_key, sheet_master_linkedin)


def userid_conditions(df):
    if (not pd.isna(df['Email Address'])) and df['Email Address'] not in ['', '#REF!']:
        return df['Email Address']
    elif (not pd.isna(df['Phone_Number_Own'])) and df['Phone_Number_Own'] not in ['', '#REF!']:
        return df['Phone_Number_Own']
    elif (not pd.isna(df['LinkedIn Profile URL'])) and df['LinkedIn Profile URL'] not in ['', '#REF!']:
        return df['LinkedIn Profile URL']
    elif (not pd.isna(df['Date of Birth'])) and df['Date of Birth'] not in ['', '#REF!']:
        return df['NAME'] + '_' + df['Date of Birth']
    else:
        return df['NAME']


def do_web_scrapping_for_profile_id_list(aan_people_url):
    # Web Scrapping happening here
    # Returns list of PROFILE_ID

    driver = do_login_to_linked_in()
    # "https://www.linkedin.com/school/avanti-alumni-network/people/?viewAsMember=true"
    company = Company(aan_people_url, driver=driver, scrape=True, close_on_complete=False)
    driver.quit()
    print(company)

    names_and_urls = []
    unretrieved_count = 0
    unretrieved_reasons = []
    for idx, employee in enumerate(company.employees):
        try:
            names_and_urls.append((employee.name, employee.linkedin_url))
            print((employee.name, employee.linkedin_url))
        except Exception as e:
            unretrieved_count += 1
            unretrieved_reasons.append(str(e))
            unretrieved_reasons = list(set(unretrieved_reasons))

    print("Profiles Retrieved -", len(names_and_urls))
    print("Profiles Un-retrieved :", unretrieved_count)
    print("Reasons for failure of profile retrievals -", unretrieved_reasons)
    print()
    print('*' * 20, "RETRIEVED ALUMNI NAMES AND URLS", '*' * 20)
    names_and_urls_df_list = [[name, url] for name, url in names_and_urls]

    return names_and_urls_df_list


def get_new_profiles_to_web_scrape_gs(num_of_prof):
    all_df = get_control_df()
    status = NEW_STATUS
    req_df = all_df.query('WEB_SCRAP_STATUS == @status & PROFILE_ACTIVE == "Y"').head(num_of_prof)
    return list(req_df['LinkedIn Profile URL'])


def web_scrape_and_update_gs(profile_id_url_list):
    all_df = get_control_df()
    profile_info_list = do_web_scrapping_for_profile_details(profile_id_url_list)
    profile_info_df = pd.DataFrame(profile_info_list)
    profile_info_df['WEB_SCRAP_STATUS'] = SUCCESS_STATUS

    if len(all_df) > 0:
        all_df = all_df.set_index('LinkedIn Profile URL')  # When Sheet is empty, PROFILE_ID does not exist
        profile_info_df = profile_info_df.set_index('LinkedIn Profile URL')
        all_df.update(profile_info_df)
        all_df.reset_index(inplace=True)
        clear_update_control_df(all_df)
    else:
        clear_update_control_df(profile_info_df)


def get_all_web_scrapped_profiles_to_update_gs():
    all_df = get_control_df()
    req_df = all_df.query('WEB_SCRAP_STATUS == @SUCCESS_STATUS & PROFILE_ACTIVE == "Y"')
    req_df = req_df.drop(['PROFILE_ACTIVE', 'LAST_ACTIVE_DATE', 'WEB_SCRAP_STATUS'], axis=1)
    return req_df


def complete_profiles_gs(web_scrapped_profile):
    ctrl_df = get_control_df()
    web_scrapped_profile['WEB_SCRAP_STATUS'] = CLOSED_STATUS
    status_dict = pd.Series(web_scrapped_profile['WEB_SCRAP_STATUS'].values,
                            index=web_scrapped_profile['LinkedIn Profile URL']).to_dict()
    ctrl_df.loc[ctrl_df['LinkedIn Profile URL'].isin(status_dict.keys()), 'WEB_SCRAP_STATUS'] = \
        ctrl_df.loc[ctrl_df['LinkedIn Profile URL'].isin(status_dict.keys()), 'LinkedIn Profile URL'].map(status_dict)
    clear_update_control_df(ctrl_df)


def update_sync_date_for_audit():
    pass


def do_ws_task():
    # Select n number profile with  PROFILE_ACTIVE=Y and WEB_SCRAPE_STATUS= NEW
    cfg = get_config()
    num_of_prof = cfg['linkedin']['num.of.profiles']
    profile_id_list = get_new_profiles_to_web_scrape_gs(num_of_prof)

    if len(profile_id_list) > 0:
        web_scrape_and_update_gs(profile_id_list)
    else:
        web_scrapped_profile_details = get_all_web_scrapped_profiles_to_update_gs()

        if len(web_scrapped_profile_details) > 0:
            merge_master_data_and_update_sheet_gs(web_scrapped_profile_details)
            complete_profiles_gs(web_scrapped_profile_details)
        else:
            # not required, For Future use
            update_sync_date_for_audit()