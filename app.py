import streamlit as st
import pandas as pd
from definition import (
    stats, season_stand, stats_viewer_pitchname, swing_viewer_pitchname,
    season_stand_pitchname, swing_viewer_stand_pitchname,
    stats_viewer_stand_pitchname, season_pitchname,
    stats_viewer, swing_viewer, stats_viewer_stand,
    swing_viewer_stand, movement_dataframe, LEAGUE_OPTIONS,
)
from dataframe import load_league_data, get_team_list, get_pitcher_list, get_player_df
from map import (
    season_movement_chart, season_pitchtrack_chart, season_pitched_fig,
    season_location_fig, create_pitcher_swing_map,
    create_pitcher_swing_map_stand, pitch_by_pitch_map,
)
from user import login
import plotly.express as px
import plotly.graph_objects as go

# ════════════════════════════════════════════════════════════
# 페이지 설정
# ════════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="KT WIZ PITCHING ANALYTICS",
)

COOKIE_TOKEN = "my_unique_cookie_token"

if "loggedIn" not in st.session_state:
    st.session_state.loggedIn = False

# ════════════════════════════════════════════════════════════
# 반응형 + 공통 CSS
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── 반응형 브레이크포인트 ─────────────────────────────── */
@media (max-width: 1024px) {
    .header-text    { font-size: 24px !important; }
    .subheader-text { font-size: 15px !important; }
    [data-testid="stSidebar"] { min-width: 220px !important; max-width: 240px !important; }
    .block-container { padding: 0.5rem 1rem !important; }
}
@media (max-width: 767px) {
    .header-text    { font-size: 18px !important; }
    .subheader-text { font-size: 13px !important; }
    [data-testid="stSidebar"] { min-width: 100% !important; max-width: 100% !important; }
    .block-container { padding: 0.3rem 0.5rem !important; }
    .js-plotly-plot  { width: 100% !important; }
}

/* ── 전체 배경 ─────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #e70012 50%, #f0f0f0 50%);
    background-attachment: fixed;
}

/* ── 사이드바 ──────────────────────────────────────────── */
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
    font-weight: 500;
}
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

/* ── 헤더 ──────────────────────────────────────────────── */
.header-container {
    padding: 1rem;
    margin: 0;
    width: 100%;
    margin-top: -1rem;
}
.header-text {
    font-size: 32px;
    font-weight: bold;
    color: #333333;
    margin-bottom: 0;
}
.subheader-text {
    color: #c0c0c0;
    font-size: 18px;
    margin-bottom: 10px;
}

/* ── 로그인 ────────────────────────────────────────────── */
.login-container {
    max-width: 420px;
    margin: 20px auto;
    padding: 20px;
    background-color: #f0f0f0;
    border-radius: 8px;
}
.logo-container { text-align: center; margin-bottom: 20px; }
.stTextInput > div > div > input {
    border: 0px solid #ddd;
    padding: 10px;
    border-radius: 0;
    margin-bottom: 0;
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
.warning-text {
    color: red;
    font-weight: bold;
    margin-bottom: 12px;
    font-size: 16px;
    text-align: right;
}
.info-text { font-size: 15px; color: #666; }
.footer {
    text-align: center;
    position: fixed;
    bottom: 60px;
    width: 100%;
    color: #333;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 세션 / 헬퍼
# ════════════════════════════════════════════════════════════
headerSection = st.container()
mainSection   = st.container()
loginSection  = st.container()
logOutSection = st.container()


def get_user_id():
    return st.session_state.get(COOKIE_TOKEN)

def set_user_id(user_id):
    st.session_state[COOKIE_TOKEN] = user_id

def is_user_logged_in():
    return st.session_state.get("loggedIn", False)

def LoggedOut_Clicked():
    st.session_state["loggedIn"] = False

def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button("Log Out", key="logout", on_click=LoggedOut_Clicked)

def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        set_user_id(userName)
        st.session_state["loggedIn"] = True
    else:
        st.session_state["loggedIn"] = False
        st.error("유효하지 않은 ID 또는 패스워드 입니다.")

# ════════════════════════════════════════════════════════════
# 로그인 페이지
# ════════════════════════════════════════════════════════════
def show_login_page():
    st.markdown("""
    <div class="header-container">
        <h1 class="header-text">
            <span style='color:#c0c0c0;'>KT WIZ</span>
            <span style='color:#333333;'> PITCHING ANALYTICS</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)

    left_col, mid1, mid2, right_col = st.columns([0.5, 4, 5, 0.5])

    with mid1:
        st.markdown('<div class="logo-container" style="padding-top:80px;">', unsafe_allow_html=True)
        st.image("ktwiz_emblem.png", width=260)
        st.markdown("</div>", unsafe_allow_html=True)

    with mid2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="warning-text">※허가된 사용자 외 사용을 금함</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-text">케이티 위즈</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader-text">투수 분석페이지에 오신것을 환영합니다.</div>', unsafe_allow_html=True)
        st.markdown('<hr style="margin:0;">', unsafe_allow_html=True)

        # ✅ label 에 공백 없이 실제 텍스트를 주고 label_visibility="collapsed" 로 숨김
        userName = st.text_input(
            "아이디",
            placeholder="아이디",
            label_visibility="collapsed",
        )
        password = st.text_input(
            "비밀번호",
            placeholder="비밀번호",
            type="password",
            label_visibility="collapsed",
        )
        st.session_state["password"] = password

        st.button("로그인", on_click=LoggedIn_Clicked, args=(userName, password))
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2 = st.columns([1, 3])
        with c1:
            st.checkbox("아이디 저장", key="remember_id")
        with c2:
            st.markdown(
                '<div class="info-text">아이디와 비밀번호를 입력하여 로그인 후 사용해 주세요.</div>',
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════
# 메인 페이지
# ════════════════════════════════════════════════════════════
def show_main_page():
    show_logout_page()

    # ── 사이드바: 리그 → 팀 → 선수 ─────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ 필터")
        st.markdown("---")

        # 1) 리그 선택
        selected_league = st.selectbox(
            "🏆 리그 선택",
            options=LEAGUE_OPTIONS,
            key="selected_league",
        )

        # 2) 리그 데이터 로드 (캐시)
        with st.spinner("데이터 로딩 중..."):
            league_df = load_league_data(selected_league)

        if league_df.empty:
            st.warning("해당 리그 데이터가 없습니다.")
            return

        # 3) 팀 선택
        team_list = get_team_list(league_df)
        if not team_list:
            st.warning("팀 정보를 찾을 수 없습니다.")
            return

        default_team_idx = 0
        for i, t in enumerate(team_list):
            if "KT" in str(t).upper():
                default_team_idx = i
                break

        selected_team = st.selectbox(
            "🏟️ 팀 선택",
            options=team_list,
            index=default_team_idx,
            key="selected_team",
        )

        # 4) 선수 선택
        pitcher_options = get_pitcher_list(league_df, selected_team)
        if not pitcher_options:
            st.warning("해당 팀의 투수 데이터가 없습니다.")
            return

        pitcher_labels = [p["label"] for p in pitcher_options]
        pitcher_values = [p["value"] for p in pitcher_options]

        selected_pitcher_label = st.selectbox(
            "🧢 투수 선택",
            options=pitcher_labels,
            key="selected_pitcher_label",
        )
        selected_pitcher = pitcher_values[pitcher_labels.index(selected_pitcher_label)]

        st.markdown("---")

        # 5) 메뉴 버튼
        menu_items = [
            ("📊 시즌 스탯",     "season_stats"),
            ("🎯 무브먼트 차트", "movement"),
            ("📍 로케이션",      "location"),
            ("🔄 구종 비율",     "pitch_ratio"),
            ("📈 스윙 분석",     "swing"),
            ("🎥 투구 트래킹",   "pitch_track"),
        ]
        if "current_menu" not in st.session_state:
            st.session_state.current_menu = "season_stats"

        for label, key in menu_items:
            if st.button(label, key=f"menu_{key}"):
                st.session_state.current_menu = key

    # ── 선수 데이터 필터링 ──────────────────────────────────
    player_df = get_player_df(league_df, selected_pitcher)

    if player_df.empty:
        st.warning(f"'{selected_pitcher}' 의 데이터가 없습니다.")
        return

    # ── 헤더 ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="header-container">
        <h1 class="header-text">
            <span style='color:#c0c0c0;'>KT WIZ</span>
            <span style='color:#333333;'> PITCHING ANALYTICS</span>
            <span style='color:#c0c0c0; font-size:18px;'> · {selected_pitcher}</span>
        </h1>
        <div class="subheader-text">{selected_league} · {selected_team}</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.session_state.current_menu

    # ════════════════════════════════════════════════════════
    # 메뉴별 콘텐츠
    # ════════════════════════════════════════════════════════

    if menu == "season_stats":
        st.subheader("📊 시즌 스탯")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**전체**")
            try:
                st.dataframe(stats(player_df), use_container_width=True)
            except Exception as e:
                st.error(f"스탯 계산 오류: {e}")
        with col2:
            st.markdown("**좌/우 타자별**")
            try:
                st.dataframe(season_stand(player_df), use_container_width=True)
            except Exception as e:
                st.error(f"스탯 계산 오류: {e}")
        st.markdown("**구종별**")
        try:
            st.dataframe(season_pitchname(player_df), use_container_width=True)
        except Exception as e:
            st.error(f"구종별 스탯 오류: {e}")

    elif menu == "movement":
        st.subheader("🎯 무브먼트 차트")
        try:
            mv_df = movement_dataframe(player_df)
            fig   = season_movement_chart(mv_df)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"무브먼트 차트 오류: {e}")

    elif menu == "location":
        st.subheader("📍 로케이션")
        tab_r, tab_l = st.tabs(["vs 우타 (R)", "vs 좌타 (L)"])
        with tab_r:
            try:
                st.plotly_chart(season_location_fig(player_df, "R"), use_container_width=True)
            except Exception as e:
                st.error(f"로케이션 오류: {e}")
        with tab_l:
            try:
                st.plotly_chart(season_location_fig(player_df, "L"), use_container_width=True)
            except Exception as e:
                st.error(f"로케이션 오류: {e}")

    elif menu == "pitch_ratio":
        st.subheader("🔄 구종 비율")
        try:
            st.plotly_chart(season_pitched_fig(player_df), use_container_width=True)
        except Exception as e:
            st.error(f"구종 비율 오류: {e}")

    elif menu == "swing":
        st.subheader("📈 스윙 분석")
        tab_all, tab_r, tab_l = st.tabs(["전체", "vs 우타 (R)", "vs 좌타 (L)"])
        with tab_all:
            try:
                st.plotly_chart(create_pitcher_swing_map(player_df), use_container_width=True)
            except Exception as e:
                st.error(f"스윙 맵 오류: {e}")
        with tab_r:
            try:
                st.plotly_chart(create_pitcher_swing_map_stand(player_df, "R"), use_container_width=True)
            except Exception as e:
                st.error(f"스윙 맵 오류: {e}")
        with tab_l:
            try:
                st.plotly_chart(create_pitcher_swing_map_stand(player_df, "L"), use_container_width=True)
            except Exception as e:
                st.error(f"스윙 맵 오류: {e}")

    elif menu == "pitch_track":
        st.subheader("🎥 투구 트래킹")
        try:
            st.plotly_chart(season_pitchtrack_chart(player_df), use_container_width=True)
        except Exception as e:
            st.error(f"투구 트래킹 오류: {e}")

# ════════════════════════════════════════════════════════════
# 진입점
# ════════════════════════════════════════════════════════════
if is_user_logged_in():
    show_main_page()
else:
    show_login_page()
