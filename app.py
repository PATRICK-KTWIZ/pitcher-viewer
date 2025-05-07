import streamlit as st
import pandas as pd
from definition import select_league, stats, season_stand, stats_viewer_pitchname, swing_viewer_pitchname, season_stand_pitchname, swing_viewer_stand_pitchname, stats_viewer_stand_pitchname 
from definition import season_pitchname, stats_viewer, swing_viewer, stats_viewer_stand, swing_viewer_stand, movement_dataframe
from map import season_movement_chart, season_pitchtrack_chart, season_pitched_fig, season_location_fig, create_pitcher_swing_map, create_pitcher_swing_map_stand, pitch_by_pitch_map
import time
from dataframe import dataframe
from PIL import Image
from user import login
import plotly.express as px
import plotly.graph_objects as go
from streamlit.components.v1 import html
import plotly.io as pio

# Set a unique token for the cookie
COOKIE_TOKEN = "my_unique_cookie_token"

# 페이지 설정
st.set_page_config(
    layout="wide",
    # initial_sidebar_state="collapsed",
    page_title="KT WIZ PITCHING ANALYTICS"
)

if 'loggedIn' not in st.session_state:
    st.session_state.loggedIn = False

# 로그인 페이지와 메인 페이지를 위한 CSS 스타일 분리
st.markdown("""
<style>
    
    /* 전체 페이지 스타일 */
    .stApp {
        background: linear-gradient(135deg, #e70012 50%, #f0f0f0 50%);
        background-attachment: fixed;
        height: 95vh; /* 뷰포트 높이의 80%로 설정 - 원하는 대로 조정 가능 */
        max-height: 1000px; /* 최대 높이 설정 */
        overflow: auto;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #e70012 !important;
        color: #ffffff !important;
    }
    
    /* 사이드바 버튼 스타일 */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #cccccc !important;
        color: black !important;
        width: 100%;
        border-radius: 7px;  /* 모서리 둥글기 */
        padding: 0.5rem 1rem;  /* 패딩 */
    }

    /* 사이드바 selectbox 라벨 색상 변경 (옅은 회색) */
    [data-testid="stSidebar"] .css-81oif8,
    [data-testid="stSidebar"] .css-1inwz65,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox > div > label {
        color: #ababab !important;
    }

    /* 사이드바 selectbox 내부 텍스트 색상 변경 */
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: black !important;
    }
    
    /* 사이드바 markdowncontainer 내부 텍스트 색상 변경 */
    [data-testid="stSidebar"] button:has([data-testid="stMarkdownContainer"]) {
        color: black !important; 
        font-weight: bold !important;
        font-size: 15px;
    }

    /* 드롭다운 메뉴 텍스트 색상 */
    .stSelectbox option {
        color: black;
    }
  
    /* 헤더 스타일 */
    .header-container {
        padding: 1rem;
        margin: 0;
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -47vw;
        margin-right: -50vw;
        margin-top: -2vw;
    }
    
    /* 로그인 컨테이너 스타일 */
    .login-container {
        max-width: 100px;
        margin: 20px auto;
        padding: 20px;
        background-color: #f0f0f0;
    }
    
    /* 로고 컨테이너 */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* 로그인 폼 스타일 */
    .stTextInput > div > div > input {
        border: 0px solid #ddd;
        padding: 10px;
        border-radius: 0px;
        margin-bottom: 0px;
    }

    /* 메인 버튼 스타일 */
    .stButton > button {
        background-color: #333333;
        color: #c0c0c0;
        width: 100%;
        padding: 10px;
        border: none;
        border-radius: 3px;
        cursor: pointer;
    }


    /* 푸터 스타일 */
    .footer {
        text-align: center;
        position: fixed;
        bottom: 60px;
        width: 100%;
        color: #333;
        font-size: 15px;
    }
    /* 로그인 페이지 배경 */
    .login-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: #f0f0f0;
        background-size: cover;
        z-index: -1;
    }
    /* 헤더 텍스트 스타일 */
    .header-text {
        font-size: 35px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 0px;
    }
    /* 서브헤더 텍스트 스타일 */
    .subheader-text {
        color: #c0c0c0;
        font-size: 18px;
        margin-bottom: 10px;
    }
    
    /* 안내 텍스트 스타일 */
    .info-text {
        font-size: 15px;
        color: #666;
    }
        
    /* 경고 텍스트 스타일 */
    .warning-text {
        color: red;
        font-weight: bold;
        margin-bottom: 12px;
        font-size: 16px;
        text-align: right;
    }

</style>
""", unsafe_allow_html=True)


headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()

# Define a function to get the user's ID from the session cookie
def get_user_id():
    return st.session_state.get(COOKIE_TOKEN)

# Define a function to set the user's ID in the session cookie
def set_user_id(user_id):
    st.session_state[COOKIE_TOKEN] = user_id

# Define a function to check if the user is logged in
def is_user_logged_in():
    return st.session_state.get('loggedIn', False)

def find_id(player_dataset, select_player):
    find_player = player_dataset[player_dataset['NAME'] == select_player]
    id = find_player.iloc[0]['TM_ID']
    return id

def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
  
def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button("Log Out", key="logout", on_click=LoggedOut_Clicked)

def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        set_user_id(userName)  # Set the user ID in the session cookie
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("유효하지 않은 ID 또는 패스워드 입니다.")

def show_login_page():


    st.markdown("""
    <style>
        /* 특정 컨테이너에 스타일 적용 */
        [data-testid="stVerticalBlock"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* 컨테이너 내부 제목 스타일 */
        .header-container h1 {
            margin-top: 0 !important;
            padding-top: 0 !important;
            line-height: 1.5;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
                <div class="header-container">
                    <h1 class="header-text">
                        <span style='color: #c0c0c0;'>KT WIZ</span> 
                        <span style='color: #333333;'>PITCHING ANALYTICS</span> 
                        <span style='color: #c0c0c0;'>PAGE[Multiple Choice]</span>
                    </h1>
                </div>
                """, unsafe_allow_html=True)

    # Main layout with two columns
    left_col, middle1_col, middle2_col, right_col = st.columns([0.7, 4, 5, 0.7])

    with middle1_col:
        # Logo area
        st.markdown("""
        <div class="logo-container" style="padding-top: 100px;">
        """, unsafe_allow_html=True)
        st.image("ktwiz_emblem.png", width=300)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with middle2_col:
        # Login form container
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="warning-text">※허가된 사용자 외 사용을 금함</div>', unsafe_allow_html=True)

        # Header text
        st.markdown('<div class="header-text">케이티 위즈</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader-text">투수 분석페이지에 오신것을 환영합니다.</div>', unsafe_allow_html=True)
        
        # Horizontal line
        st.markdown('<hr style="margin: 0px 0;">', unsafe_allow_html=True)

        form_col = st.container()
        with form_col:
            userName = st.text_input("", placeholder="아이디", label_visibility="collapsed")
            password = st.text_input("", placeholder="비밀번호", type="password", label_visibility="collapsed")
            st.session_state['password'] = password

            st.markdown("""
            <style>
                [data-testid="element-container"] [data-testid="stButton"][key="login_btn"] button {
                    background-color: #333333 !important;
                    color: #c0c0c0 !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            login_button = st.button("로그인", on_click=LoggedIn_Clicked, args=(userName, password))
        
        st.markdown('</div>', unsafe_allow_html=True)

        # 체크박스와 안내 텍스트를 같은 행에 배치
        checkbox_col1, checkbox_col2 = st.columns([1, 3])
        with checkbox_col1:
            remember_id = st.checkbox("아이디 저장", key="remember_id")
        with checkbox_col2:
            st.markdown('<div class="info-text-custom">아이디와 비밀번호를 입력하여 로그인 후 사용해 주세요.</div>', unsafe_allow_html=True)
    
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the login container div
        st.markdown('</div>', unsafe_allow_html=True)

        
   # Footer
    st.markdown("""
    <div class="footer">
        Copyright © 2025 kt wiz baseball club. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

    # 로그인 페이지 클래스 닫기
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_page():
    # Check if the user is logged in
    
    if not is_user_logged_in():
        show_login_page()
        return

    # 메인 페이지 클래스 추가
    st.markdown('<div class="main-page">', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        .stApp {
        background: #ffffff;
        height: 100vh; /* 뷰포트 높이의 80%로 설정 - 원하는 대로 조정 가능 */
        overflow: auto;
    }

    </style>
    """, unsafe_allow_html=True)

    with mainSection:
        
        st.title("KT WIZ :red[PITCHING ANALYTICS] PAGE[Multiple Choice]")

        with st.sidebar:
    
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.image("ktwiz_emblem.png", width=300)
    
            st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)

        id_dataset = pd.read_csv('./player_id_info_2025.csv')
        id_dataset = id_dataset[['team','NAME','POS','TM_ID']]
        id_dataset = id_dataset[id_dataset['POS'] == 'P']

        #------------------------------------------------------------------------------

        sidebar_text = '<p style="text-align: center; font-family:sans-serif; color:white; font-size: 22px;font-weight:bold">[투수분석 페이지]</p>'
        st.sidebar.markdown(sidebar_text, unsafe_allow_html=True)

        sidebar_text = '<p style="text-align: center; font-family:sans-serif; color: #c0c0c0; font-size: 16px;">본 웹페이지는 kt wiz 전략데이터팀이<br> 개발 및 발행하였으며 허용되는 사용자 외 <br>배포 및 사용을 엄금함</p>'
        st.sidebar.markdown(sidebar_text, unsafe_allow_html=True)

        #-------------------------------------------------------------------------

        teams = id_dataset['team'].tolist() 
        teams_list = id_dataset['team'].unique().tolist()
        select_team = st.sidebar.selectbox('팀명 선택', teams_list)
        player_dataset = id_dataset[id_dataset['team'] == select_team]

        player_list = player_dataset['NAME'].unique().tolist()
        select_player = st.sidebar.selectbox('선수 선택', player_list)

        player_id = find_id(player_dataset, select_player)
        
        option = st.sidebar.selectbox('리그 선택', ("-", "KBO(1군)", "KBO(2군)", "AAA","KBA(아마)"))


        # Create a session_state variable to store selected player information
        if 'selected_players' not in st.session_state:
            st.session_state.selected_players = []

        if st.sidebar.button('선수추가'):
            st.session_state.selected_players.append({'Team': select_team, 'Player Name': select_player, 'League': option, 'ID' : player_id})

        selected_player_df = pd.DataFrame()
        # Display the selected player names
        if st.session_state.selected_players:
            st.subheader('Selected Players:')
            for player_info in st.session_state.selected_players:
                st.write(f"Team: {player_info['Team']}, Player Name: {player_info['Player Name']}, League: {player_info['League']}, ID: {player_info['ID']}")

                select_player_df = id_dataset[ (id_dataset['team'] == player_info['Team']) & (id_dataset['TM_ID'] == player_info['ID']) ]
                selected_player_df = pd.concat([selected_player_df, select_player_df])


        if st.sidebar.button('실행'):
            
            concatenated_df = pd.DataFrame()
            # final_results = pd.DataFrame()

            for player_info in st.session_state.selected_players:

                league = select_league(player_info['League'])
                id = player_info['ID']
                # player_name = player_info['Player Name']

                player_df = dataframe(league, id, st.session_state['password'])

                concatenated_df = pd.concat([concatenated_df, player_df])
            
            pitcher_dataframes = {}
            
            for pitcher, group in concatenated_df.groupby('pitcher'):
                pitcher_dataframes[pitcher] = group.copy()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
            
            st.title('[시즌별 :red[주요현황]]')
            st.subheader(':gray[기록 & 투구]')

            season_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                season_stats_df = stats(pitcher_raw_df)
                stats_viewer_df = stats_viewer(season_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.index.values[0]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)

                stats_f_row_df.insert(0,'연도',game_year)
                
                season_stats_concat_df = pd.concat([season_stats_concat_df, stats_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            s1 = dict(selector='th', props=[('text-align', 'center')])
            s2 = dict(selector='td', props=[('text-align', 'center')])  

            styled_df = season_stats_concat_df.style.set_table_styles([s1, s2])

            st.dataframe(styled_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                season_stats_df = stats(pitcher_raw_df)
                stats_viewer_df = stats_viewer(season_stats_df)

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})
                stats_viewer_df = stats_viewer_df.set_index('연도')

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1500)

#-------------------------------------------------------------------------------------------------------

            st.subheader(':gray[투구 경향성]')

            season_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                season_stats_df = stats(pitcher_raw_df)
                swing_viewer_df = swing_viewer(season_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.index.values[0]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)

                swing_f_row_df.insert(0,'연도',game_year)
                
                season_swing_concat_df = pd.concat([season_swing_concat_df, swing_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(season_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                season_stats_df = stats(pitcher_raw_df)
                swing_viewer_df = swing_viewer(season_stats_df)

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})
                swing_viewer_df = swing_viewer_df.set_index('연도')

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1500)

            
            with st.expander("LSA(Launch Speed Angle) 이란?"):
                st.write("LSA(Launch Speed Angle)은 Baseball Savant의 타구표에서 활용되는 지표로 6단계로 타구의 질을 구분하고 있음 (*괄호의 %는 안타확률)")
                st.write("LSA 1: Weak(10.4%) / LSA 2: Topped(22.3%) / LSA 3: Under(7.7%) / LSA 4: Flare & Burner(70.8%) / LSA 5: Solid Contact(46.3%) / LSA 6: Barrel(70.5%)")
                st.markdown("""<style>[data-testid=stExpander] [data-testid=stImage]{text-align: left;display: block;margin-left: 10; margin-right: auto; width: 50%;}</style>""", unsafe_allow_html=True)
                st.image("approach.jpg")

            with st.expander("타격 어프로치 구분"):
                st.write("타격 어프로치는 타자들의 타격성향을 나타내기 위해 작성된 내용으로 리그의 평균적인 존에 대한 스윙시도, 존 외부에 대한 스윙시도를 기준으로 4가지의 성향을 구분하고 있음")
                st.markdown("""<style>[data-testid=stExpander] [data-testid=stImage]{text-align: left;display: block;margin-left: 10; margin-right: auto; width: 80%;}</style>""", unsafe_allow_html=True)
                st.image("plate_discipline.png")


            st.divider()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[구종유형별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            pkind_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_pitchname(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)

                # stats_f_row_df.insert(0,'연도',game_year)
                
                pkind_stats_concat_df = pd.concat([pkind_stats_concat_df, stats_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(pkind_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')                
                pkind_stats_df = stats_viewer_pitchname(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1600)


# # -------------------------------------------------------------------------------------------------------

            st.subheader(':gray[투구경향성]')

            throws_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_pitchname(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)

                # swing_f_row_df.insert(0,'연도',game_year)
                
                throws_swing_concat_df = pd.concat([throws_swing_concat_df, swing_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(throws_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                swing_viewer_df = swing_viewer_pitchname(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# # -------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_stand(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_stand(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)

                # stats_f_row_df.insert(0,'연도',game_year)
                
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, stats_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(throws_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_stand(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                stats_viewer_df = stats_viewer_stand(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1600)

# # -------------------------------------------------------------------------------------------------------

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_stand(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_stand(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)

                # swing_f_row_df.insert(0,'연도',game_year)
                
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, swing_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(pkind_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_stand(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')
                pkind_stats_df = swing_viewer_stand(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# # -------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형 & 구종별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_stand_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_stand_pitchname(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)

                # stats_f_row_df.insert(0,'연도',game_year)
                
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, stats_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(throws_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                throws_stats_df = season_stand_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                stats_viewer_df = stats_viewer_stand_pitchname(throws_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1600)

# # -------------------------------------------------------------------------------------------------------

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_stand_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_stand_pitchname(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)

                # swing_f_row_df.insert(0,'연도',game_year)
                
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, swing_f_row_df])

            pd.set_option('display.max_colwidth', 100)

            st.dataframe(pkind_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                pkind_stats_df = season_stand_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')
                pkind_stats_df = swing_viewer_stand_pitchname(pkind_stats_df)

                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']                

                with st.expander(f"상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


            st.title('[시즌 :red[무브먼트 차트] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                movement_chart_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                movement_chart_df = movement_chart_raw_df

                game_year = movement_chart_df['game_year'].max()
                movement_chart_df = movement_chart_df[movement_chart_df['game_year'] == game_year]
            
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']

                st.subheader(f"{pitcher_name}, {game_year}")

                col1, col2 = st.columns([3.8,6.2])

                with col1: 
                    season_movement_fig = season_movement_chart(movement_chart_df)
                    st.plotly_chart(season_movement_fig, layout="wide", key=f"season_pitched_{pitcher}")

                with col2:
                    st.markdown("<div style='height: 320px;'></div>", unsafe_allow_html=True)
                    season_movement_dataframe = movement_dataframe(movement_chart_df)
                    st.dataframe(season_movement_dataframe, hide_index=True, width=950)

                st.markdown(""" <div style="text-align: right; font-size: 0.9em;">
                    <span style="font-weight: bold;">색상 범례:</span> 
                    붉은색: 포심 / 핑크: 투심 / 보라: 커터 / 파랑 : 슬라이더 / 오랜지: 커브 / 노랑: 스위퍼 / 녹색: 체인지업 / 갈색: 포크 
                </div>
                """, 
                unsafe_allow_html=True)
                
                # 모든 연도 가져오기
                years = sorted(movement_chart_raw_df['game_year'].unique(), reverse=True)
                
                # 최신 연도를 제외한 이전 연도들만 필터링
                previous_years = [year for year in years if year != game_year]
                
                # 이전 연도가 있을 경우에만 expander 표시
                if previous_years:
                    with st.expander(f"연도별: {pitcher_name}"):
                        # 최신 연도를 제외한 각 연도별로 그래프 표시
                        for year_idx, year in enumerate(previous_years):
                            st.subheader(f"{pitcher_name}, {year}")

                            year_df = movement_chart_raw_df[movement_chart_raw_df['game_year'] == year]

                            col1, col2 = st.columns([3.8,6.2])

                            with col1: 
                                season_movement_fig = season_movement_chart(year_df)
                                st.plotly_chart(season_movement_fig, layout="wide", key=f"season_pitched_{pitcher}_{year}")

                            with col2:
                                st.markdown("<div style='height: 330px;'></div>", unsafe_allow_html=True)
                                season_movement_dataframe = movement_dataframe(year_df)
                                st.dataframe(season_movement_dataframe, hide_index=True, width=1100)

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[피치 트랙(Pitch Track)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitchtrack_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                # 사용 가능한 모든 시즌 확인
                available_years = sorted(pitchtrack_raw_df['game_year'].unique(), reverse=True)
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # 최근 2개 시즌 표시
                if len(available_years) >= 2:
                    years_display = f"{available_years[0]}-{available_years[1]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    
                    col1, col2 = st.columns(2)
                    
                    # 가장 최근 연도 (col1)
                    with col1:
                        st.write(f"**{available_years[0]}**")
                        latest_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]
                        latest_year_fig = season_pitchtrack_chart(latest_year_df)
                        st.plotly_chart(latest_year_fig, layout="wide", key=f"season_pitched_{pitcher}_latest")
                    
                    # 그 다음 연도 (col2)
                    with col2:
                        st.write(f"**{available_years[1]}**")
                        previous_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]
                        previous_year_fig = season_pitchtrack_chart(previous_year_df)
                        st.plotly_chart(previous_year_fig, layout="wide", key=f"season_pitched_{pitcher}_previous")
                
                # 최근 1개 시즌만 있는 경우
                else:
                    year = available_years[0]
                    st.subheader(f"{pitcher_name}, {year}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**{year}**")
                        year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == year]
                        year_fig = season_pitchtrack_chart(year_df)
                        st.plotly_chart(year_fig, layout="wide", key=f"season_pitched_{pitcher}")
                
                st.markdown(""" <div style="text-align: right; font-size: 0.9em;">
                                <span style="font-weight: bold;">색상 범례:</span> 
                                붉은색: 포심 / 핑크: 투심 / 보라: 커터 / 파랑 : 슬라이더 / 오랜지: 커브 / 노랑: 스위퍼 / 녹색: 체인지업 / 갈색: 포크 
                            </div>
                            """, 
                            unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[로케이션(Location)] 현황]')

            # 그래프 설명을 위한 HTML 마크업 준비
            explanation_html = """
            <div style="display: flex; justify-content: space-between; margin-top: -15px; margin-bottom: 15px;">
                <div style="text-align: center; width: 50%;">
                    <p style="font-weight: bold; margin-bottom: 0;">우타자</p>
                </div>
                <div style="text-align: center; width: 50%;">
                    <p style="font-weight: bold; margin-bottom: 0;">좌타자</p>
                </div>
            </div>
            """

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitchtrack_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                # 사용 가능한 모든 시즌 확인
                available_years = sorted(pitchtrack_raw_df['game_year'].unique(), reverse=True)
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # 최근 3개 시즌 표시
                if len(available_years) >= 3:
                    years_display = f"{available_years[0]}-{available_years[2]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    
                    col1, col2, col3, col4 = st.columns([1,3,3,3])
                    
                    with col1:
                        st.markdown("""
                        <div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # 2025 (col1)
                    with col2:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[0]}</h3>", unsafe_allow_html=True)
                        latest_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]
                        latest_year_fig = season_pitched_fig(latest_year_df)
                        st.plotly_chart(latest_year_fig, use_container_width=True, key=f"season_location_{pitcher}_latest")
        
                    
                    # 2024 (col2)
                    with col3:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[1]}</h3>", unsafe_allow_html=True)
                        previous_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]
                        previous_year_fig = season_pitched_fig(previous_year_df)
                        st.plotly_chart(previous_year_fig, use_container_width=True, key=f"season_location_{pitcher}_previous")
                        
                    # 2023 (col3)
                    with col4:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[2]}</h3>", unsafe_allow_html=True)
                        third_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[2]]
                        third_year_fig = season_pitched_fig(third_year_df)
                        st.plotly_chart(third_year_fig, use_container_width=True, key=f"season_location_{pitcher}_third")
                
                # 최근 2개 시즌만 있는 경우
                elif len(available_years) == 2:
                    years_display = f"{available_years[0]}-{available_years[1]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    
                    col1, col2, col3, col4 = st.columns([0.3,3.2,3.2,3.2])
                    
                    with col1:
                        st.markdown("""
                        <div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # 첫 번째 연도 (col1)
                    with col2:
                        st.write(f"**{available_years[0]}**")
                        latest_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]
                        latest_year_fig = season_pitched_fig(latest_year_df)
                        st.plotly_chart(latest_year_fig, use_container_width=True, key=f"season_location_{pitcher}_latest")
                    
                    # 두 번째 연도 (col2)
                    with col3:
                        st.write(f"**{available_years[1]}**")
                        previous_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]
                        previous_year_fig = season_pitched_fig(previous_year_df)
                        st.plotly_chart(previous_year_fig, use_container_width=True, key=f"season_location_{pitcher}_previous")
                        
                    # 세 번째 열은 비워둠
                    with col4:
                        st.write("**데이터 없음**")
                
                # 최근 1개 시즌만 있는 경우
                elif len(available_years) == 1:
                    year = available_years[0]
                    st.subheader(f"{pitcher_name}, {year}")
                    
                    col1, col2, col3, col4 = st.columns([1,3,3,3])
                    
                    with col1:
                        st.markdown("""
                        <div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.write(f"**{year}**")
                        year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == year]
                        year_fig = season_pitched_fig(year_df)
                        st.plotly_chart(year_fig, use_container_width=True, key=f"season_location_{pitcher}")
                        
                    # 두 번째, 세 번째 열은 비워둠
                    with col3:
                        st.write("**데이터 없음**")
                    with col4:
                        st.write("**데이터 없음**")
                
# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------


            st.title('[시즌 :red[구종별 로케이션(Location)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                location_chart_df = pitcher_df
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # 사용 가능한 모든 시즌 확인
                years = sorted(location_chart_df['game_year'].unique(), reverse=True)
                
                if len(years) > 0:
                    # 최근 연도 데이터
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                    
                    current_year_df = location_chart_df[location_chart_df['game_year'] == current_year]
                    
                    if not current_year_df.empty:
                        # 구종 정보 가져오기
                        available_pitches = current_year_df['pitch_name'].unique().tolist()
                        
                        # 원하는 순서의 구종 목록
                        desired_order = ['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Curveball', 'Changeup', 'Split-Finger', 'Sweeper']
                        
                        # 실제 데이터에 있는 구종만 필터링하여 순서 지정
                        ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                        
                        # 좌측 라벨 열과 구종별 열 생성
                        cols = st.columns([1] + [3] * len(ordered_pitches))
                        
                        # 좌측 라벨 열
                        with cols[0]:
                            st.markdown("""
                            <div style="height: 600px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 150px 0;">
                                <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                                <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                            </div>
                            """, unsafe_allow_html=True)


                        # 각 구종별 차트 표시
                        for idx, pitch_name in enumerate(ordered_pitches):
                            with cols[idx + 1]:
                                # # 구종 이름을 상단에 표시
                                # st.markdown(f"<h4 style='text-align: center;'>{pitch_name}</h4>", unsafe_allow_html=True)
                                
                                # 해당 구종의 데이터만 필터링
                                pitch_df = current_year_df[current_year_df['pitch_name'] == pitch_name]
                                
                                # 구종별 로케이션 차트 생성
                                pitch_fig = season_location_fig(pitch_df, pitch_name)
                                st.plotly_chart(pitch_fig, use_container_width=True, key=f"pitch_{pitcher}_{current_year}_{idx}")
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")
                    
                    # 이전 연도 데이터를 expander에 표시
                    if len(years) > 1:
                        with st.expander((f"연도별: {pitcher_name}")):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                
                                year_df = location_chart_df[location_chart_df['game_year'] == year]
                                
                                if not year_df.empty:
                                    # 구종 정보 가져오기
                                    available_pitches = year_df['pitch_name'].unique().tolist()
                                    
                                    # 원하는 순서의 구종 목록
                                    desired_order = ['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Curveball', 'Changeup', 'Split-Finger', 'Sweeper']
                                    
                                    # 실제 데이터에 있는 구종만 필터링하여 순서 지정
                                    ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                                    
                                    # 좌측 라벨 열과 구종별 열 생성
                                    year_cols = st.columns([1] + [3] * len(ordered_pitches))
                                    
                                    # 좌측 라벨 열
                                    with year_cols[0]:
                                        st.markdown("""
                                        <div style="height: 700px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 200px 0;">
                                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # 각 구종별 차트 표시
                                    for idx, pitch_name in enumerate(ordered_pitches):
                                        with year_cols[idx + 1]:
                                            
                                            # 해당 구종의 데이터만 필터링
                                            pitch_df = year_df[year_df['pitch_name'] == pitch_name]

                                          
                                            # 구종별 로케이션 차트 생성
                                            pitch_fig = season_location_fig(pitch_df, pitch_name)


                                            st.plotly_chart(pitch_fig, use_container_width=True, config={'displayModeBar': False,  # 도구바 숨기기
                                                                                                         'staticPlot': False,      # 상호작용 유지
                                                            },key=f"pitch_{pitcher}_{year}_{idx}")
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                
                                # 연도 간 구분선 추가 (마지막 연도 제외)
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")

                    # 투수 간 구분선 추가
                    st.markdown("---")


# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형별 스윙맵(Swing Map)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                swing_map_stnad_df = pitcher_df
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # 사용 가능한 모든 시즌 확인
                years = sorted(swing_map_stnad_df['game_year'].unique(), reverse=True)
                
                if len(years) > 0:
                    # 최근 연도 데이터
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 타자유형별 로케이션")
                    
                    current_year_df = swing_map_stnad_df[swing_map_stnad_df['game_year'] == current_year]
                    
                    if not current_year_df.empty:
                        
                        # 각 투수의 스윙맵 생성
                        create_pitcher_swing_map_stand(current_year_df, pitcher_name, current_year)
                        
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")

                    st.markdown("""
                        <div style="text-align: left; font-size: 0.9em;">
                        <span style="font-weight: bold;">기호 범례:</span> 
                        파란색: 콜드 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("""
                        <div style="text-align: left; font-size: 0.9em;">
                        <span style="font-weight: bold;">색상 범례:</span> 
                        원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 이전 연도 데이터를 expander에 표시
                    if len(years) > 1:
                        with st.expander(f"연도별: {pitcher_name}"):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                
                                year_df = swing_map_stnad_df[swing_map_stnad_df['game_year'] == year]
                                
                                if not year_df.empty:

                                    # 각 투수의 스윙맵 생성
                                    create_pitcher_swing_map_stand(year_df, pitcher_name, year)
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                
                                # 연도 간 구분선 추가 (마지막 연도 제외)
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")

                    # 투수 간 구분선 추가
                    st.markdown("---")

# # -------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[구종별 스윙맵(Swing Map)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                swing_map_df = pitcher_df
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # 사용 가능한 모든 시즌 확인
                years = sorted(swing_map_df['game_year'].unique(), reverse=True)
                
                if len(years) > 0:
                    # 최근 연도 데이터
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                    
                    current_year_df = swing_map_df[swing_map_df['game_year'] == current_year]
                    
                    if not current_year_df.empty:
                        # 구종 정보 가져오기
                        available_pitches = current_year_df['pitch_name'].unique().tolist()
                        
                        # 원하는 순서의 구종 목록
                        desired_order = ['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Curveball', 'Changeup', 'Split-Finger', 'Sweeper']
                        
                        # 실제 데이터에 있는 구종만 필터링하여 순서 지정
                        ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                        
                        # 각 투수의 스윙맵 생성
                        create_pitcher_swing_map(current_year_df, pitcher_name, current_year, ordered_pitches)
                        
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")

                    st.markdown("""
                        <div style="text-align: left; font-size: 0.9em;">
                        <span style="font-weight: bold;">기호 범례:</span> 
                        파란색: 콜드 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("""
                        <div style="text-align: left; font-size: 0.9em;">
                        <span style="font-weight: bold;">색상 범례:</span> 
                        원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 이전 연도 데이터를 expander에 표시
                    if len(years) > 1:
                        with st.expander(f"연도별: {pitcher_name}"):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                
                                year_df = swing_map_df[swing_map_df['game_year'] == year]
                                
                                if not year_df.empty:
                                    # 구종 정보 가져오기
                                    available_pitches = year_df['pitch_name'].unique().tolist()
                                    
                                    # 원하는 순서의 구종 목록에서 실제 데이터에 있는 구종만 필터링
                                    ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                                    
                                    # 각 투수의 스윙맵 생성
                                    create_pitcher_swing_map(year_df, pitcher_name, year, ordered_pitches)
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                
                                # 연도 간 구분선 추가 (마지막 연도 제외)
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")

                    # 투수 간 구분선 추가
                    st.markdown("---")



# # -------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[최근 5경기 투구표] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitch_by_pitch_map_df = pitcher_df
                
                # 투수 정보 가져오기
                pitcher_str = str(pitcher)
                pitcher_finder = selected_player_df[selected_player_df['TM_ID'] == pitcher_str]
                pitcher_name = pitcher_finder.iloc[0]['NAME']
                
                # game_date 컬럼을 사용하여 최근 5경기 가져오기
                if 'game_date' in pitch_by_pitch_map_df.columns:
                    # 날짜 데이터 변환
                    pitch_by_pitch_map_df['game_date'] = pd.to_datetime(pitch_by_pitch_map_df['game_date'], errors='coerce')
                    # 날짜별로 정렬하여 최근 5개 날짜 선택
                    recent_dates = sorted(pitch_by_pitch_map_df['game_date'].dropna().unique(), reverse=True)[:5]
                    
                    if len(recent_dates) > 0:
                        st.subheader(f"{pitcher_name} - 최근 경기 구종별 로케이션")
                        
                        # 최근 경기 데이터
                        latest_date = recent_dates[0]
                        latest_game_df = pitch_by_pitch_map_df[pitch_by_pitch_map_df['game_date'] == latest_date]
                        
                        if not latest_game_df.empty:
                            # 최신 경기 정보 표시
                            opponent = latest_game_df['batterteam'].iloc[0] if 'batterteam' in latest_game_df.columns else "상대팀 정보 없음"
                            # numpy.datetime64를 문자열로 변환
                            date_str = str(latest_date).split('T')[0]  # 'T' 이후의 시간 부분을 제거
                            st.write(f"### 최신 경기 (날짜: {date_str})")
                            st.write(f"상대팀: {opponent}")
                            st.markdown("""
                                <div style="text-align: left; font-size: 0.9em;">
                                <span style="font-weight: bold;">기호 범례:</span> 
                                파란색: 콜드 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown("""
                                <div style="text-align: left; font-size: 0.9em;">
                                <span style="font-weight: bold;">색상 범례:</span> 
                                원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # 이닝별 그래프 생성 및 표시
                            inning_figures = pitch_by_pitch_map(latest_game_df)
                            
                            # 여기서 수정: 각 이닝별 그래프를 HTML 컴포넌트로 표시
                            for inning, fig in inning_figures.items():
                                st.write(f"#### {inning}회")
                                
                                # 타자 수에 따라 전체 너비 계산
                                batter_count = len(latest_game_df[latest_game_df['inning'] == inning].batname.unique())
                                total_width = batter_count * 300  # 기본 너비 사용 (타자당 300px)
                                
                                # 그래프 HTML 생성
                                fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                                
                                # 전체 HTML 구성 (빈 박스 + 그래프)
                                complete_html = f"""
                                <div style="width: 100%; 
                                            height: 600px; 
                                            border: none; 
                                            border-radius: 5px; 
                                            padding: 10px; 
                                            margin-bottom: 20px;
                                            background-color: white;">
                                    <div style="width: 100%; height: 100%; overflow-x: auto; overflow-y: hidden;">
                                        <div style="width: {total_width}px; height: 550px;">
                                            {fig_html}
                                        </div>
                                    </div>
                                </div>
                                """
                                
                                # HTML 컴포넌트로 렌더링
                                html(complete_html, height=520)  # 약간의 여유 공간 추가
                        else:
                            st.write(f"{pitcher_name}의 최근 경기 데이터가 없습니다.")
                        
                        # 이전 경기 데이터를 expander에 표시
                        if len(recent_dates) > 1:
                            for game_date in recent_dates[1:]:
                                game_df = pitch_by_pitch_map_df[pitch_by_pitch_map_df['game_date'] == game_date]
                                
                                if not game_df.empty:
                                    # 경기 정보 가져오기
                                    opponent = game_df['batterteam'].iloc[0] if 'batterteam' in game_df.columns else "상대팀 정보 없음"
                                    # numpy.datetime64를 문자열로 변환
                                    date_str = str(game_date).split('T')[0]  # 'T' 이후의 시간 부분을 제거
                                    
                                    with st.expander(f"경기 날짜: {date_str} (상대팀: {opponent})"):
                                        # 이닝별 그래프 생성 및 표시
                                        inning_figures = pitch_by_pitch_map(game_df)
                                        
                                        # 여기도 수정: expander 내의 그래프도 HTML 컴포넌트로 표시
                                        for inning, fig in inning_figures.items():
                                            st.write(f"#### {inning}회")
                                            
                                            # 타자 수에 따라 전체 너비 계산
                                            batter_count = len(game_df[game_df['inning'] == inning].batname.unique())
                                            total_width = batter_count * 300  # 기본 너비 사용
                                            
                                            # 그래프 HTML 생성
                                            fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                                            
                                            # 전체 HTML 구성 (빈 박스 + 그래프)
                                            complete_html = f"""
                                            <div style="width: 100%; 
                                                        height: 600px; 
                                                        border: 1px none; 
                                                        border-radius: 5px; 
                                                        padding: 10px; 
                                                        margin-bottom: 20px;
                                                        background-color: white;">
                                                <div style="width: 100%; height: 100%; overflow-x: auto; overflow-y: hidden;">
                                                    <div style="width: {total_width}px; height: 550px;">
                                                        {fig_html}
                                                    </div>
                                                </div>
                                            </div>
                                            """
                                            
                                            # HTML 컴포넌트로 렌더링
                                            html(complete_html, height=520)
                                else:
                                    # numpy.datetime64를 문자열로 변환
                                    date_str = str(game_date).split('T')[0]
                                    with st.expander(f"경기 날짜: {date_str}"):
                                        st.write(f"{pitcher_name}의 해당 경기 데이터가 없습니다.")
                        else:
                            st.write(f"{pitcher_name}의 이전 경기 데이터가 없습니다.")
                        
                        # 투수 간 구분선 추가
                        st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 경기 데이터가 없습니다.")
                else:
                    st.error(f"{pitcher_name}의 데이터에 game_date 컬럼이 없습니다.")
                            








with headerSection:
    # Get the user's ID from the session cookie
    user_id = get_user_id()

    if user_id is None:
        st.session_state['loggedIn'] = False
        show_login_page()
    else:
        st.session_state['loggedIn'] = True
        show_main_page()
