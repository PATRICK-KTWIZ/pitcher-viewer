import streamlit as st
import pandas as pd
from definition import stats, season_stand, stats_viewer_pitchname, swing_viewer_pitchname, season_stand_pitchname, swing_viewer_stand_pitchname, stats_viewer_stand_pitchname
from definition import season_pitchname, stats_viewer, swing_viewer, stats_viewer_stand, swing_viewer_stand, movement_dataframe
from map import season_movement_chart, season_pitchtrack_chart, season_pitched_fig, season_location_fig, create_pitcher_swing_map, create_pitcher_swing_map_stand, pitch_by_pitch_map
import time
# ✅ dataframe → load_league_data, get_player_df 로 교체
from dataframe import load_league_data, get_player_df
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
    page_title="KT WIZ PITCHING ANALYTICS"
)

if 'loggedIn' not in st.session_state:
    st.session_state.loggedIn = False

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #e70012 50%, #f0f0f0 50%);
        background-attachment: fixed;
        height: 95vh;
        max-height: 1000px;
        overflow: auto;
    }
    [data-testid="stSidebar"] {
        background-color: #e70012 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #cccccc !important;
        color: black !important;
        width: 100%;
        border-radius: 7px;
        padding: 0.5rem 1rem;
        height: 2rem;
        font-size: 16px;
        margin-bottom: 0px;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .css-81oif8,
    [data-testid="stSidebar"] .css-1inwz65,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox > div > label {
        color: #ababab !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: black !important;
    }
    [data-testid="stSidebar"] button:has([data-testid="stMarkdownContainer"]) {
        color: black !important; 
        font-weight: bold !important;
        font-size: 15px;
    }
    .stSelectbox option {
        color: black;
    }
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
    .login-container {
        max-width: 100px;
        margin: 20px auto;
        padding: 20px;
        background-color: #f0f0f0;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .stTextInput > div > div > input {
        border: 0px solid #ddd;
        padding: 10px;
        border-radius: 0px;
        margin-bottom: 0px;
    }
    .stButton > button {
        background-color: #333333;
        color: #c0c0c0;
        width: 100%;
        padding: 10px;
        border: none;
        border-radius: 3px;
        cursor: pointer;
    }
    .footer {
        text-align: center;
        position: fixed;
        bottom: 60px;
        width: 100%;
        color: #333;
        font-size: 15px;
    }
    .login-background {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: #f0f0f0;
        background-size: cover;
        z-index: -1;
    }
    .header-text {
        font-size: 35px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 0px;
    }
    .subheader-text {
        color: #c0c0c0;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .info-text {
        font-size: 15px;
        color: #666;
    }
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

def get_user_id():
    return st.session_state.get(COOKIE_TOKEN)

def set_user_id(user_id):
    st.session_state[COOKIE_TOKEN] = user_id

def is_user_logged_in():
    return st.session_state.get('loggedIn', False)

def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False

def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button("Log Out", key="logout", on_click=LoggedOut_Clicked)

def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        set_user_id(userName)
        st.session_state['loggedIn'] = True
        st.session_state['password'] = password
    else:
        st.session_state['loggedIn'] = False
        st.error("유효하지 않은 ID 또는 패스워드 입니다.")

def reset_selections():
    st.session_state.selected_players = []

def show_login_page():
    st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
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

    left_col, middle1_col, middle2_col, right_col = st.columns([0.7, 4, 5, 0.7])

    with middle1_col:
        st.markdown("""
        <div class="logo-container" style="padding-top: 100px;">
        """, unsafe_allow_html=True)
        st.image("ktwiz_emblem.png", width=280)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with middle2_col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="warning-text">※허가된 사용자 외 사용을 금함</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-text">케이티 위즈</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader-text">투수 분석페이지에 오신것을 환영합니다.</div>', unsafe_allow_html=True)
        st.markdown('<hr style="margin: 0px 0;">', unsafe_allow_html=True)

        form_col = st.container()
        with form_col:
            # ✅ label에 빈 문자열 대신 실제 텍스트 + label_visibility="collapsed"
            userName = st.text_input("아이디", placeholder="아이디", label_visibility="collapsed")
            password = st.text_input("비밀번호", placeholder="비밀번호", type="password", label_visibility="collapsed")
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

        checkbox_col1, checkbox_col2 = st.columns([1, 3])
        with checkbox_col1:
            remember_id = st.checkbox("아이디 저장", key="remember_id")
        with checkbox_col2:
            st.markdown('<div class="info-text-custom">아이디와 비밀번호를 입력하여 로그인 후 사용해 주세요.</div>', unsafe_allow_html=True)
    
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        Copyright © 2025 kt wiz baseball club. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def show_main_page():
    
    if not is_user_logged_in():
        show_login_page()
        return

    st.markdown('<div class="main-page">', unsafe_allow_html=True)

    st.markdown("""
    <style>
        ::-webkit-scrollbar { height: 10px; background-color: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background-color: #888; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background-color: #555; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        .stApp {
        background: #ffffff;
        height: 100vh;
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

        # ✅ ── 변경 시작 ──────────────────────────────────────
        # 기존: player_id_info_2025.csv 로드 + find_id()
        # 변경: 리그 선택 → load_league_data() → 팀/선수 목록 동적 생성

        sidebar_text = '<p style="text-align: center; font-family:sans-serif; color:white; font-size: 22px;font-weight:bold">[투수분석 페이지]</p>'
        st.sidebar.markdown(sidebar_text, unsafe_allow_html=True)

        sidebar_text = '<p style="text-align: center; font-family:sans-serif; color: #c0c0c0; font-size: 16px;">본 웹페이지는 kt wiz 전략데이터팀이<br> 개발 및 발행하였으며 허용되는 사용자 외 <br>배포 및 사용을 엄금함</p>'
        st.sidebar.markdown(sidebar_text, unsafe_allow_html=True)

        # 1) 리그 먼저 선택
        option = st.sidebar.selectbox('리그 선택', ("-", "KBO(1군)", "KBO(2군)", "AAA(마이너)", "KBA(아마)"))
       
        # 리그 "-" 선택 시 로드 안 함
        if option != "-":
            try:
                league_df = load_league_data(option)
            except Exception as e:
                st.sidebar.error(f"데이터 로드 실패: {e}")
                league_df = pd.DataFrame()
        
            if not league_df.empty:
                latest_year = league_df['game_year'].max()
                teams_list = sorted(
                    league_df[league_df['game_year'] == latest_year]['pitcherteam']
                    .dropna().unique().tolist()
                )
                select_team = st.sidebar.selectbox('팀명 선택', teams_list)
        
                team_df = league_df[
                    (league_df['game_year'] == latest_year) &
                    (league_df['pitcherteam'] == select_team)
                ]
                player_list = sorted(team_df['pitname'].dropna().unique().tolist())
                select_player = st.sidebar.selectbox('선수 선택', player_list)
            else:
                select_team = None
                select_player = None
        else:
            league_df = pd.DataFrame()
            select_team = None
            select_player = None
            st.sidebar.info("리그를 선택해 주세요.")

        # ✅ ── 변경 끝 ────────────────────────────────────────

        # 선수 추가 / 새로고침 버튼
        if 'selected_players' not in st.session_state:
            st.session_state.selected_players = []

        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button('선수추가', key="add_player_btn"):
                if select_player and option != "-":
                    # ✅ ID 없이 pitname 기준으로만 저장
                    st.session_state.selected_players.append({
                        'Team': select_team,
                        'Player Name': select_player,
                        'League': option,
                    })
     
        with col2:
            if st.button('새로고침', key="refresh_btn"):
                st.session_state.selected_players = []

        selected_player_df = pd.DataFrame()

        if st.session_state.selected_players:
            st.subheader('Selected Players:')
            for player_info in st.session_state.selected_players:
                st.write(f"Team: {player_info['Team']}, Player Name: {player_info['Player Name']}, League: {player_info['League']}")

        if st.sidebar.button('실행'):
            concatenated_df = pd.DataFrame()
        
            for player_info in st.session_state.selected_players:
                try:
                    p_league_df = load_league_data(player_info['League'])
                    player_df   = get_player_df(p_league_df, player_info['Player Name'])
                    concatenated_df = pd.concat([concatenated_df, player_df])
                except Exception as e:
                    st.error(f"[{player_info['Player Name']}] 데이터 로드 실패: {e}")
        
            if concatenated_df.empty:
                st.warning("데이터가 없습니다. 선수를 추가하고 실행해 주세요.")
                st.stop()
        
            # ✅ pitname 기준 groupby
            pitcher_dataframes = {}
            for pitcher_name, group in concatenated_df.groupby('pitname'):
                pitcher_dataframes[pitcher_name] = group.copy()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------
            
            st.title('[시즌별 :red[주요현황]]')
            st.subheader(':gray[기록 & 투구]')

            season_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df

                season_stats_df = stats(pitcher_raw_df)
                stats_viewer_df = stats_viewer(season_stats_df)

                # ✅ pitcher = pitname(문자열)이므로 직접 사용
                pitcher_name = pitcher

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
                pitcher_name = pitcher  # ✅

                season_stats_df = stats(pitcher_raw_df)
                stats_viewer_df = stats_viewer(season_stats_df)

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})
                stats_viewer_df = stats_viewer_df.set_index('연도')

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1500)

#-------------------------------------------------------------------------------------------------------

            st.subheader(':gray[투구 경향성]')

            season_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                season_stats_df = stats(pitcher_raw_df)
                swing_viewer_df = swing_viewer(season_stats_df)

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.index.values[0]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)
                swing_f_row_df.insert(0,'연도',game_year)
                
                season_swing_concat_df = pd.concat([season_swing_concat_df, swing_f_row_df])

            st.dataframe(season_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                season_stats_df = stats(pitcher_raw_df)
                swing_viewer_df = swing_viewer(season_stats_df)

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})
                swing_viewer_df = swing_viewer_df.set_index('연도')

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
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
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_pitchname(pkind_stats_df)

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)
                
                pkind_stats_concat_df = pd.concat([pkind_stats_concat_df, stats_f_row_df])

            st.dataframe(pkind_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')                
                pkind_stats_df = stats_viewer_pitchname(pkind_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(pkind_stats_df, width=1600)

            st.subheader(':gray[투구경향성]')

            throws_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_pitchname(throws_stats_df)

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)
                
                throws_swing_concat_df = pd.concat([throws_swing_concat_df, swing_f_row_df])

            st.dataframe(throws_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                swing_viewer_df = swing_viewer_pitchname(throws_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_stand(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_stand(throws_stats_df)

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)
                
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, stats_f_row_df])

            st.dataframe(throws_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_stand(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                stats_viewer_df = stats_viewer_stand(throws_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1600)

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_stand(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_stand(pkind_stats_df)

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)
                
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, swing_f_row_df])

            st.dataframe(pkind_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_stand(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')
                swing_viewer_df = swing_viewer_stand(pkind_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형 & 구종별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_stand_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.set_index('game_year')
                stats_viewer_df = stats_viewer_stand_pitchname(throws_stats_df)

                stats_viewer_df = stats_viewer_df.reset_index()
                stats_viewer_df = stats_viewer_df.astype({'game_year':'str'})
                stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'연도'})

                stats_f_row_df = stats_viewer_df.iloc[:1]
                game_year = stats_f_row_df.iloc[0]['연도']
                stats_f_row_df = stats_viewer_df[stats_viewer_df['연도'] == game_year]

                stats_f_row_df['선수명'] = pitcher_name
                stats_f_row_df.set_index('선수명', inplace=True)
                
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, stats_f_row_df])

            st.dataframe(throws_stats_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                throws_stats_df = season_stand_pitchname(pitcher_raw_df)
                throws_stats_df = throws_stats_df.rename(columns={'game_year':'연도'})
                throws_stats_df = throws_stats_df.set_index('연도')
                stats_viewer_df = stats_viewer_stand_pitchname(throws_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1600)

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_stand_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.set_index('game_year')
                swing_viewer_df = swing_viewer_stand_pitchname(pkind_stats_df)

                swing_viewer_df = swing_viewer_df.reset_index()
                swing_viewer_df = swing_viewer_df.astype({'game_year':'str'})
                swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'연도'})

                swing_f_row_df = swing_viewer_df.iloc[:1]
                game_year = swing_f_row_df.iloc[0]['연도']
                swing_f_row_df = swing_viewer_df[swing_viewer_df['연도'] == game_year]

                swing_f_row_df['선수명'] = pitcher_name
                swing_f_row_df.set_index('선수명', inplace=True)
                
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, swing_f_row_df])

            st.dataframe(pkind_swing_concat_df, width=1600)
            
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅

                pkind_stats_df = season_stand_pitchname(pitcher_raw_df)
                pkind_stats_df = pkind_stats_df.rename(columns={'game_year':'연도'})
                pkind_stats_df = pkind_stats_df.set_index('연도')
                swing_viewer_df = swing_viewer_stand_pitchname(pkind_stats_df)

                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1600)

            st.divider()

# -------------------------------------------------------------------------------------------------------
# (무브먼트 ~ 최근5경기 이하 코드는 pitcher_name = pitcher 로만 변경, 나머지 100% 원본 유지)
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[무브먼트 차트] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                movement_chart_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                movement_chart_df = movement_chart_raw_df
                game_year = movement_chart_df['game_year'].max()
                movement_chart_df = movement_chart_df[movement_chart_df['game_year'] == game_year]
                pitcher_name = pitcher  # ✅

                st.subheader(f"{pitcher_name}, {game_year}")
                col1, col2 = st.columns([3.8,6.2])
                with col1: 
                    season_movement_fig = season_movement_chart(movement_chart_df)
                    st.plotly_chart(season_movement_fig, layout="wide", key=f"season_pitched_{pitcher}")
                with col2:
                    st.markdown("<div style='height: 320px;'></div>", unsafe_allow_html=True)
                    season_movement_dataframe = movement_dataframe(movement_chart_df)
                    st.dataframe(season_movement_dataframe, hide_index=True, width=950)

                st.markdown("""<div style="text-align: right; font-size: 0.9em;">
                    <span style="font-weight: bold;">색상 범례:</span> 
                    빨강: 포심 / 핑크: 투심 / 보라: 커터 / 녹색 : 슬라이더 / 오랜지: 커브 / 골드: 스위퍼 / 파랑: 체인지업 / 갈색: 포크 
                </div>""", unsafe_allow_html=True)
                
                years = sorted(movement_chart_raw_df['game_year'].unique(), reverse=True)
                previous_years = [year for year in years if year != game_year]
                
                if previous_years:
                    with st.expander(f"연도별 현황: {pitcher_name}"):
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

            st.title('[시즌 :red[피치 트랙(Pitch Track)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitchtrack_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                available_years = sorted(pitchtrack_raw_df['game_year'].unique(), reverse=True)
                pitcher_name = pitcher  # ✅
                
                if len(available_years) >= 2:
                    years_display = f"{available_years[0]}-{available_years[1]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{available_years[0]}**")
                        latest_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]
                        st.plotly_chart(season_pitchtrack_chart(latest_year_df), layout="wide", key=f"season_pitched_{pitcher}_latest")
                    with col2:
                        st.write(f"**{available_years[1]}**")
                        previous_year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]
                        st.plotly_chart(season_pitchtrack_chart(previous_year_df), layout="wide", key=f"season_pitched_{pitcher}_previous")
                else:
                    year = available_years[0]
                    st.subheader(f"{pitcher_name}, {year}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{year}**")
                        year_df = pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == year]
                        st.plotly_chart(season_pitchtrack_chart(year_df), layout="wide", key=f"season_pitched_{pitcher}_latest")

                st.markdown("""<div style="text-align: right; font-size: 0.9em;">
                    <span style="font-weight: bold;">색상 범례:</span> 
                    빨강: 포심 / 핑크: 투심 / 보라: 커터 / 녹색 : 슬라이더 / 오랜지: 커브 / 골드: 스위퍼 / 파랑: 체인지업 / 갈색: 포크 
                </div>""", unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------------
# 로케이션 ~ 최근5경기: pitcher_name = pitcher 로만 변경, 나머지 원본 100% 유지
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[로케이션(Location)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitchtrack_raw_df = globals()[f"df_{pitcher}"] = pitcher_df
                available_years = sorted(pitchtrack_raw_df['game_year'].unique(), reverse=True)
                pitcher_name = pitcher  # ✅
                
                if len(available_years) >= 3:
                    years_display = f"{available_years[0]}-{available_years[2]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    col1, col2, col3, col4 = st.columns([1,3,3,3])
                    with col1:
                        st.markdown("""<div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[0]}</h3>", unsafe_allow_html=True)
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]), use_container_width=True, key=f"season_location_{pitcher}_latest")
                    with col3:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[1]}</h3>", unsafe_allow_html=True)
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]), use_container_width=True, key=f"season_location_{pitcher}_previous")
                    with col4:
                        st.markdown(f"<h3 style='text-align: center;'>{available_years[2]}</h3>", unsafe_allow_html=True)
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[2]]), use_container_width=True, key=f"season_location_{pitcher}_third")
                elif len(available_years) == 2:
                    years_display = f"{available_years[0]}-{available_years[1]}"
                    st.subheader(f"{pitcher_name}, {years_display}")
                    col1, col2, col3, col4 = st.columns([0.3,3.2,3.2,3.2])
                    with col1:
                        st.markdown("""<div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.write(f"**{available_years[0]}**")
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[0]]), use_container_width=True, key=f"season_location_{pitcher}_latest")
                    with col3:
                        st.write(f"**{available_years[1]}**")
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == available_years[1]]), use_container_width=True, key=f"season_location_{pitcher}_previous")
                    with col4:
                        st.write("**데이터 없음**")
                else:
                    year = available_years[0]
                    st.subheader(f"{pitcher_name}, {year}")
                    col1, col2, col3, col4 = st.columns([1,3,3,3])
                    with col1:
                        st.markdown("""<div style="height: 950px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 290px 0;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold;">좌타자</div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        st.write(f"**{year}**")
                        st.plotly_chart(season_pitched_fig(pitchtrack_raw_df[pitchtrack_raw_df['game_year'] == year]), use_container_width=True, key=f"season_location_{pitcher}")
                    with col3:
                        st.write("**데이터 없음**")
                    with col4:
                        st.write("**데이터 없음**")

# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[구종별 로케이션(Location)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                location_chart_df = globals()[f"df_{pitcher}"] = pitcher_df
                pitcher_name = pitcher  # ✅
                years = sorted(location_chart_df['game_year'].unique(), reverse=True)
                
                if len(years) > 0:
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                    current_year_df = location_chart_df[location_chart_df['game_year'] == current_year]
                    
                    if not current_year_df.empty:
                        available_pitches = current_year_df['pitch_name'].unique().tolist()
                        desired_order = ['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Sweeper', 'Curveball', 'Changeup', 'Split-Finger']
                        ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                        pitch_count = len(ordered_pitches)
                        total_width = pitch_count * 300
                        pitch_figures = {}
                        for pitch_name in ordered_pitches:
                            pitch_df = current_year_df[current_year_df['pitch_name'] == pitch_name]
                            pitch_figures[pitch_name] = season_location_fig(pitch_df, pitch_name)
                        html_components = []
                        for pitch_name, fig in pitch_figures.items():
                            fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                            html_components.append(f"""<div style="display: inline-block; width: 270px; height: 600px; margin-right: 0px;">
                                <div style="text-align: center; font-weight: bold; margin-bottom: 5px;">{pitch_name}</div>
                                {fig_html}</div>""")
                        label_html = """<div style="display: inline-block; width: 50px; height: 900px; vertical-align: top; padding-top: 200px;">
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold; margin-bottom: 80px;">우타자</div>
                            <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold; margin-top: 230px;">좌타자</div></div>"""
                        complete_html = f"""<div style="width: 100%; height: 750px; border: none; border-radius: 5px; padding: 10px; margin-bottom: 20px; background-color: white;">
                            <div style="width: 100%; height: 100%; overflow-x: scroll; overflow-y: hidden; -webkit-overflow-scrolling: touch;">
                                <div style="width: {total_width + 50}px; height: 800px;">{label_html}{''.join(html_components)}</div></div></div>"""
                        html(complete_html, height=650)
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")
                    
                    if len(years) > 1:
                        with st.expander((f"연도별 현황: {pitcher_name}")):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                year_df = location_chart_df[location_chart_df['game_year'] == year]
                                if not year_df.empty:
                                    available_pitches = year_df['pitch_name'].unique().tolist()
                                    ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                                    pitch_count = len(ordered_pitches)
                                    total_width = pitch_count * 300
                                    pitch_figures = {}
                                    for pitch_name in ordered_pitches:
                                        pitch_df = year_df[year_df['pitch_name'] == pitch_name]
                                        pitch_figures[pitch_name] = season_location_fig(pitch_df, pitch_name)
                                    html_components = []
                                    for pitch_name, fig in pitch_figures.items():
                                        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                                        html_components.append(f"""<div style="display: inline-block; width: 270px; height: 600px; margin-right: 0px;">
                                            <div style="text-align: center; font-weight: bold; margin-bottom: 5px;">{pitch_name}</div>
                                            {fig_html}</div>""")
                                    label_html = """<div style="display: inline-block; width: 50px; height: 700px; vertical-align: top; padding-top: 200px;">
                                        <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold; margin-bottom: 80px;">우타자</div>
                                        <div style="transform: rotate(-90deg); transform-origin: center; font-weight: bold; margin-top: 230px;">좌타자</div></div>"""
                                    complete_html = f"""<div style="width: 100%; height: 750px; border: none; border-radius: 5px; padding: 5px; margin-bottom: 10px; background-color: white;">
                                        <div style="width: 100%; height: 100%; overflow-x: scroll; overflow-y: hidden; -webkit-overflow-scrolling: touch;">
                                            <div style="width: {total_width + 40}px; height: 600px;">{label_html}{''.join(html_components)}</div></div></div>"""
                                    html(complete_html, height=650)
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")
                    st.markdown("---")

# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[타자유형별 스윙맵(Swing Map)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                swing_map_stnad_df = pitcher_df
                pitcher_name = pitcher  # ✅
                years = sorted(swing_map_stnad_df['game_year'].unique(), reverse=True)
                
                if len(years) > 0:
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 타자유형별 로케이션")
                    current_year_df = swing_map_stnad_df[swing_map_stnad_df['game_year'] == current_year]
                    if not current_year_df.empty:
                        create_pitcher_swing_map_stand(current_year_df, pitcher_name, current_year)
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")

                    st.markdown("""<div style="text-align: left; font-size: 0.9em;"><span style="font-weight: bold;">기호 범례:</span> 
                        파란색: 콜 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃</div>""", unsafe_allow_html=True)
                    st.markdown("""<div style="text-align: left; font-size: 0.9em;"><span style="font-weight: bold;">색상 범례:</span> 
                        원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼</div>""", unsafe_allow_html=True)
                    
                    if len(years) > 1:
                        with st.expander(f"연도별 현황황: {pitcher_name}"):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                year_df = swing_map_stnad_df[swing_map_stnad_df['game_year'] == year]
                                if not year_df.empty:
                                    create_pitcher_swing_map_stand(year_df, pitcher_name, year)
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")
                    st.markdown("---")

# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[구종별 스윙맵(Swing Map)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                swing_map_df = pitcher_df
                pitcher_name = pitcher  # ✅
                years = sorted(swing_map_df['game_year'].unique(), reverse=True)
                desired_order = ['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Sweeper', 'Curveball', 'Changeup', 'Split-Finger']
                
                if len(years) > 0:
                    current_year = years[0]
                    st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                    current_year_df = swing_map_df[swing_map_df['game_year'] == current_year]
                    if not current_year_df.empty:
                        available_pitches = current_year_df['pitch_name'].unique().tolist()
                        ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                        create_pitcher_swing_map(current_year_df, pitcher_name, current_year, ordered_pitches)
                    else:
                        st.write(f"{pitcher_name}의 {current_year}년 구종 데이터가 없습니다.")

                    st.markdown("""<div style="text-align: left; font-size: 0.9em;"><span style="font-weight: bold;">기호 범례:</span>
                        파란색: 콜 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃</div>""", unsafe_allow_html=True)
                        
                    st.markdown("""<div style="text-align: left; font-size: 0.9em;"><span style="font-weight: bold;">색상 범례:</span> 
                        원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼</div>""", unsafe_allow_html=True)
                    
                    if len(years) > 1:
                        with st.expander(f"연도별 현황황: {pitcher_name}"):
                            for year in years[1:]:
                                st.subheader(f"{year}년 시즌")
                                year_df = swing_map_df[swing_map_df['game_year'] == year]
                                if not year_df.empty:
                                    available_pitches = year_df['pitch_name'].unique().tolist()
                                    ordered_pitches = [pitch for pitch in desired_order if pitch in available_pitches]
                                    create_pitcher_swing_map(year_df, pitcher_name, year, ordered_pitches)
                                else:
                                    st.write(f"{pitcher_name}의 {year}년 구종 데이터가 없습니다.")
                                if year != years[-1]:
                                    st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 이전 시즌 데이터가 없습니다.")
                    st.markdown("---")

# -------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------

            st.title('[시즌 :red[최근 5경기 투구표] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitch_by_pitch_map_df = pitcher_df
                pitcher_name = pitcher  # ✅
                
                if 'game_date' in pitch_by_pitch_map_df.columns:
                    pitch_by_pitch_map_df['game_date'] = pd.to_datetime(pitch_by_pitch_map_df['game_date'], errors='coerce')
                    recent_dates = sorted(pitch_by_pitch_map_df['game_date'].dropna().unique(), reverse=True)[:5]
                    
                    if len(recent_dates) > 0:
                        st.subheader(f"{pitcher_name} - 최근 경기 구종별 로케이션")
                        
                        latest_date = recent_dates[0]
                        latest_game_df = pitch_by_pitch_map_df[pitch_by_pitch_map_df['game_date'] == latest_date]
                        
                        if not latest_game_df.empty:
                            opponent = latest_game_df['batterteam'].iloc[0] if 'batterteam' in latest_game_df.columns else "상대팀 정보 없음"
                            date_str = str(latest_date).split('T')[0]
                            st.write(f"### 최신 경기 (날짜: {date_str})")
                            st.write(f"상대팀: {opponent}")
                            st.markdown("""<div style="text-align: left; font-size: 0.9em;">
                                <span style="font-weight: bold;">기호 범례:</span> 
                                파란색: 콜 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃</div>""", unsafe_allow_html=True)
                            st.markdown("""<div style="text-align: left; font-size: 0.9em;">
                                <span style="font-weight: bold;">색상 범례:</span> 
                                원: 포심 / 삼각형-아래(역삼각형): 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼</div>""", unsafe_allow_html=True)
                            
                            inning_figures = pitch_by_pitch_map(latest_game_df)
                            
                            for inning, fig in inning_figures.items():
                                st.write(f"#### {inning}회")
                                batter_count = len(latest_game_df[latest_game_df['inning'] == inning].batname.unique())
                                total_width = batter_count * 300
                                fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                                complete_html = f"""
                                <div style="width: 100%; height: 600px; border: none; border-radius: 5px; padding: 10px; margin-bottom: 20px; background-color: white;">
                                    <div style="width: 100%; height: 100%; overflow-x: scroll; overflow-y: hidden; -webkit-overflow-scrolling: touch;">
                                        <div style="width: {total_width}px; height: 550px;">
                                            {fig_html}
                                        </div>
                                        <div style="text-align: center; margin-top: 5px; color: #555; font-size: 0.8em;">
                                            ← 좌우로 스크롤하여 더 보기 →
                                        </div>
                                    </div>
                                </div>
                                """
                                html(complete_html, height=520)
                        else:
                            st.write(f"{pitcher_name}의 최근 경기 데이터가 없습니다.")
                        
                        if len(recent_dates) > 1:
                            for game_date in recent_dates[1:]:
                                game_df = pitch_by_pitch_map_df[pitch_by_pitch_map_df['game_date'] == game_date]
                                if not game_df.empty:
                                    opponent = game_df['batterteam'].iloc[0] if 'batterteam' in game_df.columns else "상대팀 정보 없음"
                                    date_str = str(game_date).split('T')[0]
                                    with st.expander(f"경기 날짜: {date_str} (상대팀: {opponent})"):
                                        inning_figures = pitch_by_pitch_map(game_df)
                                        for inning, fig in inning_figures.items():
                                            st.write(f"#### {inning}회")
                                            batter_count = len(game_df[game_df['inning'] == inning].batname.unique())
                                            total_width = batter_count * 300
                                            fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                                            complete_html = f"""
                                            <div style="width: 100%; height: 600px; border: none; border-radius: 5px; padding: 10px; margin-bottom: 20px; background-color: white;">
                                                <div style="width: 100%; height: 100%; overflow-x: scroll; overflow-y: hidden; -webkit-overflow-scrolling: touch;">
                                                    <div style="width: {total_width}px; height: 550px;">
                                                        {fig_html}
                                                    </div>
                                                    <div style="text-align: center; margin-top: 5px; color: #555; font-size: 0.8em;">
                                                        ← 좌우로 스크롤하여 더 보기 →
                                                    </div>
                                                </div>
                                            </div>
                                            """
                                            html(complete_html, height=450)
                                else:
                                    date_str = str(game_date).split('T')[0]
                                    with st.expander(f"경기 날짜: {date_str}"):
                                        st.write(f"{pitcher_name}의 해당 경기 데이터가 없습니다.")
                        else:
                            st.write(f"{pitcher_name}의 이전 경기 데이터가 없습니다.")
                        
                        st.markdown("---")
                    else:
                        st.write(f"{pitcher_name}의 경기 데이터가 없습니다.")
                else:
                    st.error(f"{pitcher_name}의 데이터에 game_date 컬럼이 없습니다.")


# ════════════════════════════════════════════════════════════
# 진입점 (원본 100% 유지)
# ════════════════════════════════════════════════════════════
with headerSection:
    user_id = get_user_id()

    if user_id is None:
        st.session_state['loggedIn'] = False
        show_login_page()
    else:
        st.session_state['loggedIn'] = True
        show_main_page()











                    
