# !pip install google-auth

import pandas as pd
import streamlit as st
# from google.auth.transport.requests import Request
# from google.oauth2.service_account import Credentials
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread
# import os
# from git import Repo


# import mysql.connector
# from configparser import ConfigParser
# cnx: mysql.connector.connect = None

def login (userName, password):
    user_df = pd.read_csv('./user_info_2025.csv')
    user_id = user_df['ID'].tolist()
    user_password = user_df['Password'].tolist()
    
    if userName in user_id:
        index = user_id.index(userName)
        if password == user_password[index]:
            return True
    else:
        return False

# def update_log(userName):
#     user = str(userName)
    
#     log_data = {
#         'UserName': [user],
#         'Timestamp': [pd.Timestamp.now()]}

#     log_df = pd.DataFrame(log_data)

#     # Check if the log file already exists
#     try:
#         existing_log = pd.read_csv('./login_log.csv')
#         updated_log = pd.concat([existing_log, log_df], ignore_index=True)
#     except FileNotFoundError:
#         updated_log = log_df

#     st.dataframe(updated_log)


    
#     scope = ['https://spreadsheets.google.com/feeds',
#              'https://www.googleapis.com/auth/drive']
    
#     # Replace 'your-credentials.json' with your own service account credentials file.
#     credentials = ServiceAccountCredentials.from_json_keyfile_name('streamlit-project-394007-c7a8b5f570dd.json', scope)
#     client = gspread.authorize(credentials)

#     # Replace 'Your Google Sheet Name' with the name of your Google Sheet.
#     sheet_name = '19Qmd1Phxi-GUakHMk1MNAAiTSL13WVo_NXBCnE71uik'
#     sheet = client.open(sheet_name).sheet1

#     # Clear existing data (optional)
#     # sheet.clear()

#     # Append new data to the Google Sheet
#     existing_data = sheet.get_all_records()
#     df_to_append = pd.DataFrame(log_data)
#     new_data = existing_data + df_to_append.to_dict('records')
#     sheet.insert_rows(new_data)


# -------------------------------------------------------------------------------------------------------------


    # updated_log.to_csv('./login_log.csv', index=False, encoding='utf-8')

#     os.system('git add login_log.csv')   
#     os.system('git commit -m "Update login_log.csv"')
#     os.system('git push https://github.com/PATRICK-KTWIZ/batter-viewer.git main') 

    # repo = Repo('.')
    # repo.git.add('login_log.csv')
    # repo.index.commit('Update login_log.csv')
    # origin = repo.remote(name='origin', url='https://github.com/PATRICK-KTWIZ/batter-viewer.git')
    # origin.push()
