import os
import pandas as pd
import requests
from io import BytesIO
import streamlit as st

# ════════════════════════════════════════════════════════════
# 1. 설정
# ════════════════════════════════════════════════════════════

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

OWNER    = "Henryjeon1"
REPO     = "ktdata"
TAG_NAME = "KoreaBaseballOrganization"

# ★ BUG FIX: app.py LEAGUE_LABELS 값과 키 이름을 일치시킴
LEAGUE_FILES = {
    "KBO":   "KoreaBaseballOrganization.parquet",
    "NPB":   "NPB.parquet",
    "AAA":   "AAA.parquet",
    "Minor": "Minor.parquet",   # 기존 "KBO_Minor" → "Minor"
}

CACHE_DIR = "/tmp"
MIN_YEAR  = 2023

# ════════════════════════════════════════════════════════════
# 2. 데이터 로드
# ════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="리그 데이터를 불러오는 중입니다...", ttl=3600) # 1시간 동안 메모리 유지

def load_league_data(league_name: str, min_year: int = 2023) -> pd.DataFrame:
    """
    지정한 리그 데이터를 GitHub Release에서 가져오거나 로컬 캐시에서 로드합니다.
    """
    if league_name not in LEAGUE_FILES:
        st.error(f"[{league_name}] 정의되지 않은 리그입니다.")
        return pd.DataFrame()

    file_name = LEAGUE_FILES[league_name]
    # CACHE_DIR가 없으면 현재 디렉토리에 생성 (권한 문제 방지)
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except:
            pass 
    
    cache_path = os.path.join(CACHE_DIR, file_name)

    # 1. 로컬 파일 캐시 확인
    if os.path.exists(cache_path):
        try:
            df_tmp = pd.read_parquet(cache_path)
            # 데이터 타입 최적화 (메모리 사용량 감소)
            df_tmp = _optimize_dataframe(df_tmp)
            return df_tmp[df_tmp["game_year"] >= min_year] if "game_year" in df_tmp.columns else df_tmp
        except Exception as e:
            st.warning(f"캐시 읽기 실패, 재다운로드 시도: {e}")
            if os.path.exists(cache_path): os.remove(cache_path)

    # 2. GitHub API 호출 (네트워크 최적화)
    release_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG_NAME}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    try:
        response = requests.get(release_url, headers=headers, timeout=15)
        response.raise_for_status()
        assets = response.json().get("assets", [])
        target_asset = next((a for a in assets if a["name"] == file_name), None)
        
        if not target_asset:
            st.error(f"{file_name} 파일을 찾을 수 없습니다.")
            return pd.DataFrame()

        # 파일 다운로드 (Session 유지로 성능 향상)
        with requests.Session() as session:
            session.headers.update({
                "Accept": "application/octet-stream",
                "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
            })
            res = session.get(target_asset["url"], timeout=60)
            res.raise_for_status()

        # 3. 데이터프레임 처리 및 로컬 저장
        df_tmp = pd.read_parquet(BytesIO(res.content))
        df_tmp.to_parquet(cache_path, index=False)
        
        df_tmp = _optimize_dataframe(df_tmp)
        return df_tmp[df_tmp["game_year"] >= min_year] if "game_year" in df_tmp.columns else df_tmp

    except Exception as e:
        st.error(f"데이터 로딩 중 치명적 오류 발생: {e}")
        return pd.DataFrame()

def _optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임 메모리 최적화 및 날짜 형식 정리"""
    # 숫자형 데이터 타입 다운캐스팅
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = df[col].astype('int32')
    
    # game_date가 문자열인 경우 datetime으로 변환
    if 'game_date' in df.columns:
        df['game_date'] = pd.to_datetime(df['game_date']).dt.date
        
    return df


# ════════════════════════════════════════════════════════════
# 3. 집계 헬퍼 함수 (definition.py 에서 사용)
# ════════════════════════════════════════════════════════════

# 집계할 컬럼 정의 (중복 제거 & 가독성 향상)
_SUM_COLS = [
    'inplay', 'hit', 'ab', 'pa', 'single', 'double', 'triple', 'home_run',
    'walk', 'strikeout', 'hit_by_pitch', 'sac_fly',
    'z_in', 'z_swing', 'z_con', 'z_out', 'z_inplay',
    'o_swing', 'o_con', 'o_inplay', 'f_swing', 'f_pitch', 'swing', 'whiff',
    'weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel',
]
_MEAN_COLS = ['rel_speed(km)', 'exit_velocity', 'launch_angleX']
_COUNT_COLS_GAME = {'game_date': 'nunique', 'pitname': 'count'}


def base_df(player_df: pd.DataFrame) -> pd.DataFrame:
    """game_year 단일 인덱스 집계"""
    agg = {'game_date': 'nunique', 'pitname': 'count'}
    for c in _MEAN_COLS:
        if c in player_df.columns:
            agg[c] = 'mean'
    for c in _SUM_COLS:
        if c in player_df.columns:
            agg[c] = 'sum'

    return player_df.groupby('game_year').agg(agg)


def pivot_base_df(player_df: pd.DataFrame, pivot_index) -> pd.DataFrame:
    """game_year + pivot_index 멀티 인덱스 집계.
    ★ BUG FIX: groupby().apply(pivot_table) 방식 → groupby + agg 방식으로 교체
       (pandas 2.x 에서 groupby.apply 내부 pivot_table deprecated 경고 해소)
    """
    if isinstance(pivot_index, str):
        group_keys = ['game_year', pivot_index]
    else:
        group_keys = ['game_year'] + list(pivot_index)

    agg = {'game_date': 'nunique', 'pitname': 'count'}
    for c in _MEAN_COLS + ['hit_spin_rate']:
        if c in player_df.columns:
            agg[c] = 'mean'
    for c in _SUM_COLS:
        if c in player_df.columns:
            agg[c] = 'sum'

    pivot_df = player_df.groupby(group_keys).agg(agg)
    return pivot_df


def stats_df(merged_base_df: pd.DataFrame) -> pd.DataFrame:
    df = merged_base_df.copy()   # ★ BUG FIX: SettingWithCopyWarning 방지

    # ── 타율 / 출루율 / 장타율 / OPS ──────────────────────────────────────────
    df['avg'] = 0.0
    df['obp'] = 0.0
    df['slg'] = 0.0
    df['ops'] = 0.0

    mask_ab = df['ab'] > 0
    df.loc[mask_ab, 'avg'] = df.loc[mask_ab, 'hit'] / df.loc[mask_ab, 'ab']

    obp_denom = df['ab'] + df['hit_by_pitch'] + df['walk'] + df['sac_fly']
    mask_obp  = obp_denom > 0
    df.loc[mask_obp, 'obp'] = (
        (df.loc[mask_obp, 'hit'] + df.loc[mask_obp, 'hit_by_pitch'] + df.loc[mask_obp, 'walk'])
        / obp_denom[mask_obp]
    )

    slg_num = (df['single'] * 1 + df['double'] * 2 + df['triple'] * 3 + df['home_run'] * 4)
    df.loc[mask_ab, 'slg'] = slg_num[mask_ab] / df.loc[mask_ab, 'ab']
    df['ops'] = df['obp'] + df['slg']

    # ── 투구 관련 비율 ────────────────────────────────────────────────────────
    mask_pit = df['pitname'] > 0
    df.loc[mask_pit, 'z%']        = df.loc[mask_pit, 'z_in']    / df.loc[mask_pit, 'pitname']
    df.loc[mask_pit, 'inplay_pit']= df.loc[mask_pit, 'inplay']  / df.loc[mask_pit, 'pitname']
    df.loc[mask_pit, 'o%']        = df.loc[mask_pit, 'z_out']   / df.loc[mask_pit, 'pitname']
    df.loc[mask_pit, 'swing%']    = df.loc[mask_pit, 'swing']   / df.loc[mask_pit, 'pitname']

    mask_zin   = df['z_in']    > 0
    mask_zsw   = df['z_swing'] > 0
    mask_zout  = df['z_out']   > 0
    mask_osw   = df['o_swing'] > 0
    mask_fp    = df['f_pitch'] > 0
    mask_sw    = df['swing']   > 0

    df.loc[mask_zin,  'z_swing%']  = df.loc[mask_zin,  'z_swing']  / df.loc[mask_zin,  'z_in']
    df.loc[mask_zsw,  'z_con%']    = df.loc[mask_zsw,  'z_con']    / df.loc[mask_zsw,  'z_swing']
    df.loc[mask_zsw,  'z_inplay%'] = df.loc[mask_zsw,  'z_inplay'] / df.loc[mask_zsw,  'z_swing']
    df.loc[mask_zout, 'o_swing%']  = df.loc[mask_zout, 'o_swing']  / df.loc[mask_zout, 'z_out']
    df.loc[mask_osw,  'o_con%']    = df.loc[mask_osw,  'o_con']    / df.loc[mask_osw,  'o_swing']
    df.loc[mask_osw,  'o_inplay%'] = df.loc[mask_osw,  'o_inplay'] / df.loc[mask_osw,  'o_swing']
    df.loc[mask_fp,   'f_swing%']  = df.loc[mask_fp,   'f_swing']  / df.loc[mask_fp,   'f_pitch']
    df.loc[mask_sw,   'whiff%']    = df.loc[mask_sw,   'whiff']    / df.loc[mask_sw,   'swing']
    df.loc[mask_sw,   'inplay_sw'] = df.loc[mask_sw,   'inplay']   / df.loc[mask_sw,   'swing']

    # ── LSA 타구 질 ──────────────────────────────────────────────────────────
    lsa_cols      = ['weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel']
    df['total_contact'] = df[lsa_cols].sum(axis=1)
    mask_con = df['total_contact'] > 0
    for c in lsa_cols:
        df.loc[mask_con, c] = df.loc[mask_con, c] / df.loc[mask_con, 'total_contact']
    df['plus_lsa4'] = df['flare'] + df['solid_contact'] + df['barrel']

    # ── 타격 어프로치 ─────────────────────────────────────────────────────────
    kbo_z = 0.654
    kbo_o = 0.261
    valid  = df['z_swing%'].notna() & df['o_swing%'].notna()
    df['approach'] = 'Not Specified'
    if valid.any():
        conditions = [
            valid & (df['z_swing%'] >= kbo_z) & (df['o_swing%'] >= kbo_o),
            valid & (df['z_swing%'] >= kbo_z) & (df['o_swing%'] <  kbo_o),
            valid & (df['z_swing%'] <  kbo_z) & (df['o_swing%'] >= kbo_o),
            valid & (df['z_swing%'] <  kbo_z) & (df['o_swing%'] <  kbo_o),
        ]
        df['approach'] = np.select(conditions, ['Aggressive', 'Selective', 'Non_Selective', 'Passive'],
                                   default='Not Specified')

    # ── 출력 컬럼 선택 ────────────────────────────────────────────────────────
    output_cols = [
        'game_date', 'pitname', 'pa', 'ab', 'hit', 'walk', 'strikeout', 'rel_speed(km)',
        'inplay_pit', 'exit_velocity', 'launch_angleX',
        'avg', 'obp', 'slg', 'ops',
        'z%', 'z_swing%', 'z_con%', 'z_inplay%',
        'o%', 'o_swing%', 'o_con%', 'o_inplay%',
        'f_swing%', 'swing%', 'whiff%', 'inplay_sw',
        'weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel',
        'approach', 'plus_lsa4',
    ]
    existing_cols     = [c for c in output_cols if c in df.columns]
    stats_output_df   = df[existing_cols].copy()

    # ── 퍼센트 변환 ──────────────────────────────────────────────────────────
    percent_columns = [
        'inplay_pit', 'z%', 'z_swing%', 'z_con%', 'z_inplay%',
        'o%', 'o_swing%', 'o_con%', 'o_inplay%',
        'f_swing%', 'swing%', 'whiff%', 'inplay_sw',
        'weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel', 'plus_lsa4',
    ]
    for col in percent_columns:
        if col in stats_output_df.columns:
            stats_output_df[col] = stats_output_df[col] * 100

    # ── 포맷팅 ────────────────────────────────────────────────────────────────
    round_dict = {
        'game_date': 0, 'pitname': 0, 'pa': 0, 'ab': 0, 'hit': 0, 'walk': 0,
        'strikeout': 0, 'rel_speed(km)': 1, 'inplay_pit': 1,
        'exit_velocity': 1, 'launch_angleX': 1,
        'avg': 3, 'obp': 3, 'slg': 3, 'ops': 3,
        'z%': 1, 'z_swing%': 1, 'z_con%': 1, 'z_inplay%': 1,
        'o%': 1, 'o_swing%': 1, 'o_con%': 1, 'o_inplay%': 1,
        'f_swing%': 1, 'swing%': 1, 'whiff%': 1, 'inplay_sw': 1,
        'weak': 1, 'topped': 1, 'under': 1, 'flare': 1,
        'solid_contact': 1, 'barrel': 1, 'plus_lsa4': 1,
    }

    def _fmt(x, decimals, is_pct):
        if pd.isna(x):
            return "-"
        try:
            if decimals == 0:
                return str(int(x))
            return f"{float(x):.{decimals}f}{'%' if is_pct else ''}"
        except Exception:
            return "-"

    for col, dec in round_dict.items():
        if col not in stats_output_df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(stats_output_df[col]):
            continue
        is_pct = col in percent_columns
        stats_output_df[col] = stats_output_df[col].apply(lambda x, d=dec, p=is_pct: _fmt(x, d, p))

    return stats_output_df
