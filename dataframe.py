import pandas as pd
import numpy as np
import os
import requests
from io import BytesIO
import streamlit as st

# ════════════════════════════════════════════════════════════
# 설정
# ════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER    = "Henryjeon1"
REPO     = "ktdata"
TAG_NAME = "KoreaBaseballOrganization"

LEAGUE_FILES = {
    "KBO(1군)":   "KoreaBaseballOrganization.parquet",
    "KBO(2군)":   "KBO_Minor.parquet",
    "AAA(마이너)": "AAA.parquet",
    "KBA(아마)":   "TeamExclusive.parquet",
}

CACHE_DIR = "/tmp"

# ════════════════════════════════════════════════════════════
# 데이터 로드 (GitHub Release → parquet)
# ════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_league_data(league_option: str, min_year: int = 2023) -> pd.DataFrame:
    """
    league_option : "KBO(1군)" | "KBO(2군)" | "AAA(마이너)" | "KBA(아마)"
    """
    file_name  = LEAGUE_FILES.get(league_option)
    if file_name is None:
        return pd.DataFrame()

    cache_path = os.path.join(CACHE_DIR, file_name)

    # ── 로컬 캐시 우선 ──────────────────────────────────────
    if os.path.exists(cache_path):
        df_tmp = pd.read_parquet(cache_path)
        return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp

    # ── GitHub Release 다운로드 ─────────────────────────────
    release_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}"
        f"/releases/tags/{TAG_NAME}"
    )
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response = requests.get(release_url, headers=headers, timeout=30)
    if response.status_code != 200:
        st.error(f"Release 접근 실패: {response.status_code}")
        return pd.DataFrame()

    assets       = response.json().get("assets", [])
    target_asset = next((a for a in assets if a["name"] == file_name), None)
    if not target_asset:
        st.error(f"{file_name} 파일을 찾을 수 없습니다.")
        return pd.DataFrame()

    with requests.Session() as session:
        session.headers.update({
            "Accept": "application/octet-stream",
            **({"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}),
        })
        res = session.get(target_asset["url"], timeout=60)
        if res.status_code != 200:
            st.error(f"다운로드 실패: {res.status_code}")
            return pd.DataFrame()
        try:
            df_tmp = pd.read_parquet(BytesIO(res.content))
            df_tmp.to_parquet(cache_path, index=False)
            return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp
        except Exception as e:
            st.error(f"파싱 실패: {e}")
            return pd.DataFrame()


# ════════════════════════════════════════════════════════════
# 투수 목록 생성 (리그 데이터 → 팀 / 선수 드롭다운)
# ════════════════════════════════════════════════════════════
def get_team_list(df: pd.DataFrame) -> list:
    """pitcherteam 컬럼 기준 팀 목록 반환"""
    if "pitcherteam" not in df.columns:
        return []
    latest_year = df["game_year"].max()
    teams = (
        df[df["game_year"] == latest_year]["pitcherteam"]
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(teams)


def get_pitcher_list(df: pd.DataFrame, team: str) -> list:
    """팀 필터링 후 투수 목록 반환 → [{"label": "홍길동 (R)", "value": "홍길동"}, ...]"""
    latest_year = df["game_year"].max()
    df_team = df[
        (df["game_year"] == latest_year) &
        (df["pitcherteam"] == team)
    ]
    throws_col = next(
        (c for c in ["p_throws", "throws", "pitch_hand", "pitcher_throws"]
         if c in df.columns), None
    )
    agg = {"pitname": "first"}
    if throws_col:
        agg[throws_col] = lambda x: x.mode()[0] if len(x) > 0 else ""

    grp = df_team.groupby("pitcher").agg(agg).reset_index()
    options = []
    for _, row in grp.iterrows():
        name  = row["pitname"] if pd.notna(row.get("pitname")) else str(row["pitcher"])
        throw = f" ({row[throws_col]})" if throws_col and pd.notna(row.get(throws_col)) else ""
        options.append({"label": f"{name}{throw}", "value": name})
    options.sort(key=lambda x: x["value"])
    return options


# ════════════════════════════════════════════════════════════
# 선수 데이터 필터링
# ════════════════════════════════════════════════════════════
def get_player_df(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """pitname 기준으로 선수 데이터 필터링"""
    return df[df["pitname"] == player_name].copy()


# ════════════════════════════════════════════════════════════
# 기존 stats 계산 함수들 (definition.py 에서 사용)
# ════════════════════════════════════════════════════════════
OUT_EVENTS = [
    "field_out", "strikeout", "grounded_into_double_play",
    "double_play", "force_out", "sac_fly", "sac_bunt",
    "fielders_choice_out", "strikeout_double_play",
    "other_out", "triple_play",
]


def base_df(player_df: pd.DataFrame) -> pd.DataFrame:
    df = player_df.copy()

    # game_year 컬럼 확보
    if "game_year" not in df.columns and "game_date" in df.columns:
        df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
        df["game_year"] = df["game_date"].dt.year

    # PA 단위 이벤트 플래그
    df["is_K"]   = df["events"].isin(["strikeout", "strikeout_double_play"])
    df["is_BB"]  = df["events"].isin(["walk", "intent_walk"])
    df["is_HR"]  = df["events"] == "home_run"
    df["is_HBP"] = df["events"] == "hit_by_pitch"
    df["is_out"] = df["events"].isin(OUT_EVENTS)
    df["is_swinging_strike"] = df["description"].isin(
        ["swinging_strike", "swinging_strike_blocked", "foul_tip"]
    )
    df["is_called_strike"] = df["description"] == "called_strike"
    df["is_inplay"] = df["description"].isin(
        ["hit_into_play", "hit_into_play_no_out", "hit_into_play_score"]
    )
    return df


def stats_df(merged_df: pd.DataFrame) -> pd.DataFrame:
    idx_cols = [c for c in ["game_year", "stand", "pitch_name"] if c in merged_df.columns]

    pitch_stats = merged_df.groupby(idx_cols).agg(
        total_pitch=("pitch_number", "count") if "pitch_number" in merged_df.columns
                    else ("is_swinging_strike", "count"),
        swstr=("is_swinging_strike", "sum"),
        called_str=("is_called_strike", "sum"),
    ).reset_index()

    pa_df = merged_df[merged_df["events"].notna()]
    pa_stats = pa_df.groupby(idx_cols).agg(
        PA=("is_K", "count"),
        K=("is_K", "sum"),
        BB=("is_BB", "sum"),
        HR=("is_HR", "sum"),
        HBP=("is_HBP", "sum"),
        outs=("is_out", "sum"),
    ).reset_index()

    result = pitch_stats.merge(pa_stats, on=idx_cols, how="left")
    result["IP"]     = (result["outs"] / 3).round(1)
    result["K%"]     = (result["K"]    / result["PA"]          * 100).round(1)
    result["BB%"]    = (result["BB"]   / result["PA"]          * 100).round(1)
    result["SwStr%"] = (result["swstr"] / result["total_pitch"] * 100).round(1)
    result["CSW%"]   = (
        (result["called_str"] + result["swstr"]) / result["total_pitch"] * 100
    ).round(1)

    if len(idx_cols) > 1:
        result = result.set_index(idx_cols)
    else:
        result = result.set_index(idx_cols[0])

    return result


def pivot_base_df(player_df: pd.DataFrame, pivot_index: str) -> pd.DataFrame:
    df = base_df(player_df)
    return df  # groupby는 stats_df 내부에서 처리
