import streamlit as st
import pandas as pd
from definition import select_league, stats, season_stand, stats_viewer_pitchname, swing_viewer_pitchname, season_stand_pitchname, swing_viewer_stand_pitchname, stats_viewer_stand_pitchname 
from definition import season_pitchname, stats_viewer, swing_viewer, stats_viewer_stand, swing_viewer_stand, movement_dataframe
from map import season_movement_chart, season_pitchtrack_chart, season_pitched_fig, season_location_fig, create_pitcher_swing_map, create_pitcher_swing_map_stand, pitch_by_pitch_map
from dataframe import load_league_data
from PIL import Image
from user import login
import plotly.express as px
import plotly.graph_objects as go
from streamlit.components.v1 import html
import plotly.io as pio

# ── 리그 레이블 매핑 ──────────────────────────────────────────────────────────
LEAGUE_LABELS = {
    "KBO":   "KBO",
    "NPB":   "NPB",
    "AAA":   "AAA",
    "Minor": "KBO_Minor",
}

COOKIE_TOKEN = "my_unique_cookie_token"

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="KT WIZ PITCHING ANALYTICS"
)

if 'loggedIn' not in st.session_state:
    st.session_state.loggedIn = False

# ── 공통 CSS ─────────────────────────────────────────────────────────────────
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
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: black !important;
    }
    [data-testid="stSidebar"] button:has([data-testid="stMarkdownContainer"]) {
        color: black !important;
        font-weight: bold !important;
        font-size: 15px;
    }
    .stSelectbox option { color: black; }
    .header-container {
        padding: 1rem; margin: 0; width: 100vw;
        position: relative; left: 50%; right: 50%;
        margin-left: -47vw; margin-right: -50vw; margin-top: -2vw;
    }
    .login-container { max-width: 100px; margin: 20px auto; padding: 20px; background-color: #f0f0f0; }
    .logo-container { text-align: center; margin-bottom: 20px; }
    .stTextInput > div > div > input { border: 0px solid #ddd; padding: 10px; border-radius: 0px; margin-bottom: 0px; }
    .stButton > button { background-color: #333333; color: #c0c0c0; width: 100%; padding: 10px; border: none; border-radius: 3px; cursor: pointer; }
    .footer { text-align: center; position: fixed; bottom: 60px; width: 100%; color: #333; font-size: 15px; }
    .login-background { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #f0f0f0; background-size: cover; z-index: -1; }
    .header-text { font-size: 35px; font-weight: bold; color: #333333; margin-bottom: 0px; }
    .subheader-text { color: #c0c0c0; font-size: 18px; margin-bottom: 10px; }
    .info-text { font-size: 15px; color: #666; }
    .warning-text { color: red; font-weight: bold; margin-bottom: 12px; font-size: 16px; text-align: right; }
</style>
""", unsafe_allow_html=True)

headerSection = st.container()
mainSection   = st.container()
loginSection  = st.container()
logOutSection = st.container()

# ── 유틸 함수 ─────────────────────────────────────────────────────────────────
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
    else:
        st.session_state['loggedIn'] = False
        st.error("유효하지 않은 ID 또는 패스워드 입니다.")

# ── 로그인 페이지 ─────────────────────────────────────────────────────────────
def show_login_page():
    st.markdown("""
    <style>
        [data-testid="stVerticalBlock"] > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
        .header-container h1 { margin-top: 0 !important; padding-top: 0 !important; line-height: 1.5; }
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
        st.markdown('<div class="logo-container" style="padding-top: 100px;">', unsafe_allow_html=True)
        st.image("ktwiz_emblem.png", width=280)
        st.markdown('</div>', unsafe_allow_html=True)

    with middle2_col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="warning-text">※허가된 사용자 외 사용을 금함</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-text">케이티 위즈</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader-text">투수 분석페이지에 오신것을 환영합니다.</div>', unsafe_allow_html=True)
        st.markdown('<hr style="margin: 0px 0;">', unsafe_allow_html=True)

        with st.container():
            userName = st.text_input("아이디", placeholder="아이디", label_visibility="collapsed")
            password = st.text_input("비밀번호", placeholder="비밀번호", type="password", label_visibility="collapsed")
            st.session_state['password'] = password
            st.button("로그인", on_click=LoggedIn_Clicked, args=(userName, password))

        st.markdown('</div>', unsafe_allow_html=True)

        checkbox_col1, checkbox_col2 = st.columns([1, 3])
        with checkbox_col1:
            st.checkbox("아이디 저장", key="remember_id")
        with checkbox_col2:
            st.markdown('<div class="info-text-custom">아이디와 비밀번호를 입력하여 로그인 후 사용해 주세요.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">Copyright © 2025 kt wiz baseball club. All rights reserved.</div>
    """, unsafe_allow_html=True)


# ── 메인 페이지 ───────────────────────────────────────────────────────────────
def show_main_page():
    if not is_user_logged_in():
        show_login_page()
        return

    st.markdown("""
    <style>
        ::-webkit-scrollbar { height: 10px; background-color: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background-color: #888; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background-color: #555; }
        .stApp { background: #ffffff; height: 100vh; overflow: auto; }
    </style>
    """, unsafe_allow_html=True)

    with mainSection:
        st.title("KT WIZ :red[PITCHING ANALYTICS] PAGE[Multiple Choice]")

        # ── 사이드바 ────────────────────────────────────────────────────────────
        with st.sidebar:
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.image("ktwiz_emblem.png", width=300)
            st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)

        st.sidebar.markdown(
            '<p style="text-align:center;font-family:sans-serif;color:white;font-size:22px;font-weight:bold">[투수분석 페이지]</p>',
            unsafe_allow_html=True
        )
        st.sidebar.markdown(
            '<p style="text-align:center;font-family:sans-serif;color:#c0c0c0;font-size:16px;">본 웹페이지는 kt wiz 전략데이터팀이<br>개발 및 발행하였으며 허용되는 사용자 외<br>배포 및 사용을 엄금함</p>',
            unsafe_allow_html=True
        )

        # ── ① 리그 선택 & 데이터 로드 ────────────────────────────────────────
        league_display_list = ["-"] + list(LEAGUE_LABELS.keys())
        select_league_label = st.sidebar.selectbox(
            "리그 선택",
            league_display_list,
            key="league_select"
        )

        # 리그가 선택되지 않은 경우 안내 후 종료
        if select_league_label == "-":
            st.sidebar.info("리그를 선택하면 팀/선수 목록이 표시됩니다.")
            st.info("👈 사이드바에서 리그를 먼저 선택해 주세요.")
            return

        # 리그 변경 시 선수 목록 초기화
        if st.session_state.get("_prev_league") != select_league_label:
            st.session_state["_prev_league"]    = select_league_label
            st.session_state["selected_players"] = []

        # 데이터 로드 (캐시 활용)
        league_key = LEAGUE_LABELS[select_league_label]

        @st.cache_data(show_spinner=f"📦 {select_league_label} 데이터 로드 중...")
        def _load(lk):
            return load_league_data(lk)

        league_df = _load(league_key)

        if league_df.empty:
            st.error(f"{select_league_label} 데이터를 불러오지 못했습니다.")
            return

        # ── ② 팀 & 선수 선택 (순서 무관, 양방향 필터) ───────────────────────
        # 전체 팀 목록
        all_teams   = sorted(league_df["pitcherteam"].dropna().unique().tolist())
        all_pitchers = sorted(league_df["pitcher"].dropna().unique().tolist())

        # session_state 초기화
        if "filter_team"    not in st.session_state: st.session_state["filter_team"]    = "-"
        if "filter_pitcher" not in st.session_state: st.session_state["filter_pitcher"] = "-"

        # ── 팀 선택 ──
        # 현재 선택된 선수가 있으면 해당 선수가 속한 팀만 후보로 제공
        if st.session_state["filter_pitcher"] != "-":
            pitcher_teams = sorted(
                league_df[league_df["pitcher"] == st.session_state["filter_pitcher"]]["pitcherteam"]
                .dropna().unique().tolist()
            )
            team_options = ["-"] + pitcher_teams
        else:
            team_options = ["-"] + all_teams

        select_team = st.sidebar.selectbox(
            "팀 선택",
            team_options,
            index=team_options.index(st.session_state["filter_team"])
                  if st.session_state["filter_team"] in team_options else 0,
            key="team_selectbox"
        )
        st.session_state["filter_team"] = select_team

        # ── 선수 선택 ──
        # 현재 선택된 팀이 있으면 해당 팀 소속 선수만 후보로 제공
        if st.session_state["filter_team"] != "-":
            team_pitchers = sorted(
                league_df[league_df["pitcherteam"] == st.session_state["filter_team"]]["pitcher"]
                .dropna().unique().tolist()
            )
            pitcher_options = ["-"] + team_pitchers
        else:
            pitcher_options = ["-"] + all_pitchers

        select_pitcher = st.sidebar.selectbox(
            "선수 선택",
            pitcher_options,
            index=pitcher_options.index(st.session_state["filter_pitcher"])
                  if st.session_state["filter_pitcher"] in pitcher_options else 0,
            key="pitcher_selectbox"
        )
        st.session_state["filter_pitcher"] = select_pitcher

        # 팀/선수 선택 안내
        if select_team == "-" and select_pitcher == "-":
            st.sidebar.caption("💡 팀 또는 선수를 먼저 선택하면 상대 목록이 자동으로 좁혀집니다.")

        # ── ③ 선수 추가 / 새로고침 ──────────────────────────────────────────
        if "selected_players" not in st.session_state:
            st.session_state.selected_players = []

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("선수추가", key="add_player_btn"):
                if select_pitcher == "-":
                    st.sidebar.warning("선수를 선택해 주세요.")
                else:
                    team_val = select_team if select_team != "-" else (
                        league_df[league_df["pitcher"] == select_pitcher]["pitcherteam"]
                        .dropna().iloc[0] if not league_df[league_df["pitcher"] == select_pitcher].empty else "Unknown"
                    )
                    entry = {
                        "Team"       : team_val,
                        "Player Name": select_pitcher,
                        "League"     : select_league_label,
                    }
                    # 중복 방지
                    if entry not in st.session_state.selected_players:
                        st.session_state.selected_players.append(entry)
        with col2:
            if st.button("새로고침", key="refresh_btn"):
                st.session_state.selected_players       = []
                st.session_state["filter_team"]    = "-"
                st.session_state["filter_pitcher"] = "-"
                st.rerun()

        # 선택된 선수 목록 표시
        if st.session_state.selected_players:
            st.sidebar.markdown("---")
            st.sidebar.markdown("**선택된 선수:**")
            for p in st.session_state.selected_players:
                st.sidebar.write(f"▸ [{p['League']}] {p['Team']} / {p['Player Name']}")

        # ── ④ 실행 버튼 ──────────────────────────────────────────────────────
        if st.sidebar.button("실행"):
            if not st.session_state.selected_players:
                st.warning("선수를 추가한 후 실행해 주세요.")
                return

            # 선택된 선수들의 데이터 합치기
            concatenated_df = pd.DataFrame()
            for player_info in st.session_state.selected_players:
                lk  = LEAGUE_LABELS[player_info["League"]]
                @st.cache_data
                def _load_cached(lk):
                    return load_league_data(lk)
                df_tmp = _load_cached()
                player_df = df_tmp[df_tmp["pitcher"] == player_info["Player Name"]]
                concatenated_df = pd.concat([concatenated_df, player_df])

            if concatenated_df.empty:
                st.warning("선택된 선수의 데이터가 없습니다.")
                return

            pitcher_dataframes = {
                pitcher: group.copy()
                for pitcher, group in concatenated_df.groupby("pitcher")
            }

            # selected_player_df: 선수명 → 팀 매핑용 (기존 코드 호환)
            selected_player_df = (
                concatenated_df[["pitcher", "pitcherteam"]]
                .drop_duplicates()
                .rename(columns={"pitcher": "NAME", "pitcherteam": "TEAM"})
            )

            # ── 이하 기존 시각화 코드 (pitcher / pitcher_name 참조 방식만 수정) ──

            def get_pitcher_name(pitcher):
                """pitcher 컬럼값 그대로 이름으로 사용"""
                return str(pitcher)

# ─────────────────────────────────────────────────────────────────────────────
# 시즌별 주요현황
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌별 :red[주요현황]]')
            st.subheader(':gray[기록 & 투구]')

            season_stats_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                season_stats_df = stats(pitcher_df)
                stats_viewer_df = stats_viewer(season_stats_df)

                stats_f_row_df          = stats_viewer_df.iloc[:1].copy()
                game_year               = stats_f_row_df.index.values[0]
                stats_f_row_df["선수명"] = pitcher_name
                stats_f_row_df.set_index("선수명", inplace=True)
                stats_f_row_df.insert(0, "연도", game_year)
                season_stats_concat_df  = pd.concat([season_stats_concat_df, stats_f_row_df])

            s1 = dict(selector='th', props=[('text-align', 'center')])
            s2 = dict(selector='td', props=[('text-align', 'center')])
            st.dataframe(season_stats_concat_df.style.set_table_styles([s1, s2]), width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                season_stats_df = stats(pitcher_df)
                stats_viewer_df = (
                    stats_viewer(season_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(stats_viewer_df, width=1500)

# ─────────────────────────────────────────────────────────────────────────────
            st.subheader(':gray[투구 경향성]')

            season_swing_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                season_stats_df = stats(pitcher_df)
                swing_viewer_df = swing_viewer(season_stats_df)

                swing_f_row_df          = swing_viewer_df.iloc[:1].copy()
                game_year               = swing_f_row_df.index.values[0]
                swing_f_row_df["선수명"] = pitcher_name
                swing_f_row_df.set_index("선수명", inplace=True)
                swing_f_row_df.insert(0, "연도", game_year)
                season_swing_concat_df  = pd.concat([season_swing_concat_df, swing_f_row_df])

            st.dataframe(season_swing_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                season_stats_df = stats(pitcher_df)
                swing_viewer_df = (
                    swing_viewer(season_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(swing_viewer_df, width=1500)

            with st.expander("LSA(Launch Speed Angle) 이란?"):
                st.write("LSA(Launch Speed Angle)은 Baseball Savant의 타구표에서 활용되는 지표로 6단계로 타구의 질을 구분하고 있음 (*괄호의 %는 안타확률)")
                st.write("LSA 1: Weak(10.4%) / LSA 2: Topped(22.3%) / LSA 3: Under(7.7%) / LSA 4: Flare & Burner(70.8%) / LSA 5: Solid Contact(46.3%) / LSA 6: Barrel(70.5%)")
                st.markdown("""<style>[data-testid=stExpander] [data-testid=stImage]{text-align:left;display:block;margin-left:10;margin-right:auto;width:50%;}</style>""", unsafe_allow_html=True)
                st.image("approach.jpg")

            with st.expander("타격 어프로치 구분"):
                st.write("타격 어프로치는 타자들의 타격성향을 나타내기 위해 작성된 내용으로 리그의 평균적인 존에 대한 스윙시도, 존 외부에 대한 스윙시도를 기준으로 4가지의 성향을 구분하고 있음")
                st.markdown("""<style>[data-testid=stExpander] [data-testid=stImage]{text-align:left;display:block;margin-left:10;margin-right:auto;width:80%;}</style>""", unsafe_allow_html=True)
                st.image("plate_discipline.png")

            st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# 구종유형별 현황
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[구종유형별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            pkind_stats_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = season_pitchname(pitcher_df)
                pkind_stats_df = pkind_stats_df.set_index("game_year")
                sv_df = (
                    stats_viewer_pitchname(pkind_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year      = sv_df.iloc[0]["연도"]
                row_df         = sv_df[sv_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                pkind_stats_concat_df = pd.concat([pkind_stats_concat_df, row_df])

            st.dataframe(pkind_stats_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = (
                    season_pitchname(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sv_df = stats_viewer_pitchname(pkind_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sv_df, width=1600)

            st.subheader(':gray[투구경향성]')

            throws_swing_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = season_pitchname(pitcher_df)
                throws_stats_df = throws_stats_df.set_index("game_year")
                sw_df = (
                    swing_viewer_pitchname(throws_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year       = sw_df.iloc[0]["연도"]
                row_df          = sw_df[sw_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                throws_swing_concat_df = pd.concat([throws_swing_concat_df, row_df])

            st.dataframe(throws_swing_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = (
                    season_pitchname(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sw_df = swing_viewer_pitchname(throws_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sw_df, width=1600)

            st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# 타자유형별 현황
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[타자유형별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = season_stand(pitcher_df)
                throws_stats_df = throws_stats_df.set_index("game_year")
                sv_df = (
                    stats_viewer_stand(throws_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year       = sv_df.iloc[0]["연도"]
                row_df          = sv_df[sv_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, row_df])

            st.dataframe(throws_stats_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = (
                    season_stand(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sv_df = stats_viewer_stand(throws_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sv_df, width=1600)

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = season_stand(pitcher_df)
                pkind_stats_df = pkind_stats_df.set_index("game_year")
                sw_df = (
                    swing_viewer_stand(pkind_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year      = sw_df.iloc[0]["연도"]
                row_df         = sw_df[sw_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, row_df])

            st.dataframe(pkind_swing_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = (
                    season_stand(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sw_df = swing_viewer_stand(pkind_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sw_df, width=1600)

            st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# 타자유형 & 구종별 현황
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[타자유형 & 구종별] 현황]')
            st.subheader(':gray[기록 & 투구]')

            throws_stats_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = season_stand_pitchname(pitcher_df)
                throws_stats_df = throws_stats_df.set_index("game_year")
                sv_df = (
                    stats_viewer_stand_pitchname(throws_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year       = sv_df.iloc[0]["연도"]
                row_df          = sv_df[sv_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                throws_stats_concat_df = pd.concat([throws_stats_concat_df, row_df])

            st.dataframe(throws_stats_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                throws_stats_df = (
                    season_stand_pitchname(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sv_df = stats_viewer_stand_pitchname(throws_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sv_df, width=1600)

            st.subheader(':gray[투구경향성]')

            pkind_swing_concat_df = pd.DataFrame()
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = season_stand_pitchname(pitcher_df)
                pkind_stats_df = pkind_stats_df.set_index("game_year")
                sw_df = (
                    swing_viewer_stand_pitchname(pkind_stats_df)
                    .reset_index()
                    .astype({"game_year": "str"})
                    .rename(columns={"game_year": "연도"})
                )
                game_year      = sw_df.iloc[0]["연도"]
                row_df         = sw_df[sw_df["연도"] == game_year].copy()
                row_df["선수명"] = pitcher_name
                row_df.set_index("선수명", inplace=True)
                pkind_swing_concat_df = pd.concat([pkind_swing_concat_df, row_df])

            st.dataframe(pkind_swing_concat_df, width=1600)

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name   = get_pitcher_name(pitcher)
                pkind_stats_df = (
                    season_stand_pitchname(pitcher_df)
                    .rename(columns={"game_year": "연도"})
                    .set_index("연도")
                )
                sw_df = swing_viewer_stand_pitchname(pkind_stats_df)
                with st.expander(f"연도별 상세기록:  {pitcher_name}"):
                    st.dataframe(sw_df, width=1600)

            st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# 무브먼트 차트 ~ 이하 기존 시각화 코드 (pitcher_name 참조만 변경)
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[무브먼트 차트] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name = get_pitcher_name(pitcher)
                game_year    = pitcher_df["game_year"].max()
                cur_df       = pitcher_df[pitcher_df["game_year"] == game_year]

                st.subheader(f"{pitcher_name}, {game_year}")
                col1, col2 = st.columns([3.8, 6.2])
                with col1:
                    st.plotly_chart(season_movement_chart(cur_df), layout="wide", key=f"mv_{pitcher}")
                with col2:
                    st.markdown("<div style='height: 320px;'></div>", unsafe_allow_html=True)
                    st.dataframe(movement_dataframe(cur_df), hide_index=True, width=950)

                st.markdown("""<div style="text-align:right;font-size:0.9em;">
                    <span style="font-weight:bold;">색상 범례:</span>
                    빨강: 포심 / 핑크: 투심 / 보라: 커터 / 녹색: 슬라이더 / 오랜지: 커브 / 골드: 스위퍼 / 파랑: 체인지업 / 갈색: 포크
                </div>""", unsafe_allow_html=True)

                years          = sorted(pitcher_df["game_year"].unique(), reverse=True)
                previous_years = [y for y in years if y != game_year]
                if previous_years:
                    with st.expander(f"연도별 현황: {pitcher_name}"):
                        for year in previous_years:
                            st.subheader(f"{pitcher_name}, {year}")
                            yr_df = pitcher_df[pitcher_df["game_year"] == year]
                            col1, col2 = st.columns([3.8, 6.2])
                            with col1:
                                st.plotly_chart(season_movement_chart(yr_df), layout="wide", key=f"mv_{pitcher}_{year}")
                            with col2:
                                st.markdown("<div style='height: 330px;'></div>", unsafe_allow_html=True)
                                st.dataframe(movement_dataframe(yr_df), hide_index=True, width=1100)

# ─────────────────────────────────────────────────────────────────────────────
# 피치 트랙
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[피치 트랙(Pitch Track)] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                available_years = sorted(pitcher_df["game_year"].unique(), reverse=True)

                if len(available_years) >= 2:
                    st.subheader(f"{pitcher_name}, {available_years[0]}-{available_years[1]}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{available_years[0]}**")
                        st.plotly_chart(season_pitchtrack_chart(pitcher_df[pitcher_df["game_year"] == available_years[0]]),
                                        layout="wide", key=f"pt_{pitcher}_latest")
                    with col2:
                        st.write(f"**{available_years[1]}**")
                        st.plotly_chart(season_pitchtrack_chart(pitcher_df[pitcher_df["game_year"] == available_years[1]]),
                                        layout="wide", key=f"pt_{pitcher}_prev")
                else:
                    year = available_years[0]
                    st.subheader(f"{pitcher_name}, {year}")
                    col1, _ = st.columns(2)
                    with col1:
                        st.write(f"**{year}**")
                        st.plotly_chart(season_pitchtrack_chart(pitcher_df[pitcher_df["game_year"] == year]),
                                        layout="wide", key=f"pt_{pitcher}_latest")

                st.markdown("""<div style="text-align:right;font-size:0.9em;">
                    <span style="font-weight:bold;">색상 범례:</span>
                    빨강: 포심 / 핑크: 투심 / 보라: 커터 / 녹색: 슬라이더 / 오랜지: 커브 / 골드: 스위퍼 / 파랑: 체인지업 / 갈색: 포크
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 로케이션 / 구종별 로케이션 / 스윙맵 / 투구표 — 기존 로직 동일, pitcher_name만 교체
# ─────────────────────────────────────────────────────────────────────────────
            DESIRED_PITCH_ORDER = ['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Sweeper','Curveball','Changeup','Split-Finger']

            def _render_location_html(df_year, pitcher, year, height=650):
                available = df_year["pitch_name"].unique().tolist()
                ordered   = [p for p in DESIRED_PITCH_ORDER if p in available]
                pitch_figs = {p: season_location_fig(df_year[df_year["pitch_name"] == p], p) for p in ordered}
                total_w    = len(ordered) * 300
                html_parts = []
                for pname, fig in pitch_figs.items():
                    fh = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                    html_parts.append(f'<div style="display:inline-block;width:270px;height:600px;margin-right:0px;"><div style="text-align:center;font-weight:bold;margin-bottom:5px;">{pname}</div>{fh}</div>')
                label = '<div style="display:inline-block;width:50px;height:900px;vertical-align:top;padding-top:200px;"><div style="transform:rotate(-90deg);transform-origin:center;font-weight:bold;margin-bottom:80px;">우타자</div><div style="transform:rotate(-90deg);transform-origin:center;font-weight:bold;margin-top:230px;">좌타자</div></div>'
                complete = f'<div style="width:100%;height:750px;border:none;border-radius:5px;padding:10px;margin-bottom:20px;background-color:white;"><div style="width:100%;height:100%;overflow-x:scroll;overflow-y:hidden;-webkit-overflow-scrolling:touch;"><div style="width:{total_w+50}px;height:800px;">{label}{"".join(html_parts)}</div></div></div>'
                html(complete, height=height)

            st.title('[시즌 :red[로케이션(Location)] 현황]')
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                available_years = sorted(pitcher_df["game_year"].unique(), reverse=True)

                def _loc_cols(years_to_show):
                    col_cfg = [1] + [3] * len(years_to_show) + [3] * (3 - len(years_to_show))
                    cols    = st.columns(col_cfg[:4])
                    cols[0].markdown("""<div style="height:950px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;padding:290px 0;"><div style="transform:rotate(-90deg);font-weight:bold;">우타자</div><div style="transform:rotate(-90deg);font-weight:bold;">좌타자</div></div>""", unsafe_allow_html=True)
                    for i, yr in enumerate(years_to_show[:3]):
                        with cols[i+1]:
                            st.markdown(f"<h3 style='text-align:center;'>{yr}</h3>", unsafe_allow_html=True)
                            st.plotly_chart(season_pitched_fig(pitcher_df[pitcher_df["game_year"] == yr]),
                                            use_container_width=True, key=f"loc_{pitcher}_{yr}")
                    for j in range(len(years_to_show), 3):
                        cols[j+1].write("**데이터 없음**")

                years_show = available_years[:3]
                st.subheader(f"{pitcher_name}, {years_show[0]}" + (f"-{years_show[-1]}" if len(years_show) > 1 else ""))
                _loc_cols(years_show)

            st.title('[시즌 :red[구종별 로케이션(Location)] 현황]')
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                available_years = sorted(pitcher_df["game_year"].unique(), reverse=True)
                current_year    = available_years[0]
                cur_df          = pitcher_df[pitcher_df["game_year"] == current_year]

                st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                if not cur_df.empty:
                    _render_location_html(cur_df, pitcher, current_year)
                if len(available_years) > 1:
                    with st.expander(f"연도별 현황: {pitcher_name}"):
                        for yr in available_years[1:]:
                            st.subheader(f"{yr}년 시즌")
                            yr_df = pitcher_df[pitcher_df["game_year"] == yr]
                            if not yr_df.empty:
                                _render_location_html(yr_df, pitcher, yr)
                            if yr != available_years[-1]:
                                st.markdown("---")
                st.markdown("---")

            st.title('[시즌 :red[타자유형별 스윙맵(Swing Map)] 현황]')
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                available_years = sorted(pitcher_df["game_year"].unique(), reverse=True)
                current_year    = available_years[0]
                cur_df          = pitcher_df[pitcher_df["game_year"] == current_year]

                st.subheader(f"{pitcher_name} - {current_year} 시즌 타자유형별 로케이션")
                if not cur_df.empty:
                    create_pitcher_swing_map_stand(cur_df, pitcher_name, current_year)
                st.markdown("""<div style="text-align:left;font-size:0.9em;"><span style="font-weight:bold;">기호 범례:</span> 파란색: 콜 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃</div>""", unsafe_allow_html=True)
                st.markdown("""<div style="text-align:left;font-size:0.9em;"><span style="font-weight:bold;">색상 범례:</span> 원: 포심 / 역삼각형: 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼</div>""", unsafe_allow_html=True)
                if len(available_years) > 1:
                    with st.expander(f"연도별 현황: {pitcher_name}"):
                        for yr in available_years[1:]:
                            st.subheader(f"{yr}년 시즌")
                            yr_df = pitcher_df[pitcher_df["game_year"] == yr]
                            if not yr_df.empty:
                                create_pitcher_swing_map_stand(yr_df, pitcher_name, yr)
                            if yr != available_years[-1]:
                                st.markdown("---")
                st.markdown("---")

            st.title('[시즌 :red[구종별 스윙맵(Swing Map)] 현황]')
            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name    = get_pitcher_name(pitcher)
                available_years = sorted(pitcher_df["game_year"].unique(), reverse=True)
                current_year    = available_years[0]
                cur_df          = pitcher_df[pitcher_df["game_year"] == current_year]

                st.subheader(f"{pitcher_name} - {current_year} 시즌 구종별 로케이션")
                if not cur_df.empty:
                    ordered = [p for p in DESIRED_PITCH_ORDER if p in cur_df["pitch_name"].unique()]
                    create_pitcher_swing_map(cur_df, pitcher_name, current_year, ordered)
                st.markdown("""<div style="text-align:left;font-size:0.9em;"><span style="font-weight:bold;">기호 범례:</span> 파란색: 콜 스트라이크 / 노란색: 스윙 스트라이크 / 회색: 볼 / 분홍색: 파울 / 빨간색: 안타 / 갈색: 아웃</div>""", unsafe_allow_html=True)
                st.markdown("""<div style="text-align:left;font-size:0.9em;"><span style="font-weight:bold;">색상 범례:</span> 원: 포심 / 역삼각형: 투심 / 삼각형-우측아래: 커터 / 삼각형-우측: 슬라이더 / 삼각형-위: 커브 / 다이아몬드: 체인지업 / 사각형: 스플리터 / 십자가: 스위퍼</div>""", unsafe_allow_html=True)
                if len(available_years) > 1:
                    with st.expander(f"연도별 현황: {pitcher_name}"):
                        for yr in available_years[1:]:
                            st.subheader(f"{yr}년 시즌")
                            yr_df = pitcher_df[pitcher_df["game_year"] == yr]
                            if not yr_df.empty:
                                ordered = [p for p in DESIRED_PITCH_ORDER if p in yr_df["pitch_name"].unique()]
                                create_pitcher_swing_map(yr_df, pitcher_name, yr, ordered)
                            if yr != available_years[-1]:
                                st.markdown("---")
                st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 최근 5경기 투구표
# ─────────────────────────────────────────────────────────────────────────────
            st.title('[시즌 :red[최근 5경기 투구표] 현황]')

            for pitcher, pitcher_df in pitcher_dataframes.items():
                pitcher_name = get_pitcher_name(pitcher)
                if "game_date" not in pitcher_df.columns:
                    st.error(f"{pitcher_name}의 데이터에 game_date 컬럼이 없습니다.")
                    continue

                pitcher_df["game_date"] = pd.to_datetime(pitcher_df["game_date"], errors="coerce")
                recent_dates = sorted(pitcher_df["game_date"].dropna().unique(), reverse=True)[:5]

                if not len(recent_dates):
                    st.write(f"{pitcher_name}의 경기 데이터가 없습니다.")
                    continue

                st.subheader(f"{pitcher_name} - 최근 경기 구종별 로케이션")

                def _render_pbp(game_df, key_suffix):
                    inning_figs = pitch_by_pitch_map(game_df)
                    for inning, fig in inning_figs.items():
                        st.write(f"#### {inning}회")
                        batter_count = len(game_df[game_df["inning"] == inning].batname.unique())
                        total_w      = batter_count * 300
                        fig_html     = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})
                        complete     = f'<div style="width:100%;height:600px;border:none;border-radius:5px;padding:10px;margin-bottom:20px;background-color:white;"><div style="width:100%;height:100%;overflow-x:scroll;overflow-y:hidden;-webkit-overflow-scrolling:touch;"><div style="width:{total_w}px;height:550px;">{fig_html}</div><div style="text-align:center;margin-top:5px;color:#555;font-size:0.8em;">← 좌우로 스크롤하여 더 보기 →</div></div></div>'
                        html(complete, height=520)

                # 최신 경기
                latest_df  = pitcher_df[pitcher_df["game_date"] == recent_dates[0]]
                opponent   = latest_df["batterteam"].iloc[0] if "batterteam" in latest_df.columns else "상대팀 정보 없음"
                date_str   = str(recent_dates[0]).split("T")[0]
                st.write(f"### 최신 경기 (날짜: {date_str})")
                st.write(f"상대팀: {opponent}")
                _render_pbp(latest_df, f"{pitcher}_latest")

                # 이전 경기
                for gd in recent_dates[1:]:
                    gdf      = pitcher_df[pitcher_df["game_date"] == gd]
                    opp      = gdf["batterteam"].iloc[0] if "batterteam" in gdf.columns else "상대팀 정보 없음"
                    date_str = str(gd).split("T")[0]
                    with st.expander(f"경기 날짜: {date_str} (상대팀: {opp})"):
                        _render_pbp(gdf, f"{pitcher}_{date_str}")

                st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 엔트리포인트
# ─────────────────────────────────────────────────────────────────────────────
# with headerSection:
#     user_id = get_user_id()
#     if user_id is None:
#         st.session_state['loggedIn'] = False
#         show_login_page()
#     else:
#         st.session_state['loggedIn'] = True
#         show_main_page()

# 수정된 코드
with headerSection:
    if is_user_logged_in():
        show_logout_page()
        show_main_page()
    else:
        show_login_page()
