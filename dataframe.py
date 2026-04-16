import pandas as pd
import numpy as np
import os
import requests
from io import BytesIO

# ════════════════════════════════════════════════════════════
# 설정
# ════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER    = "Henryjeon1"
REPO     = "ktdata"
TAG_NAME = "KoreaBaseballOrganization"

LEAGUE_FILES = {
    "KBO(1군)":    "KoreaBaseballOrganization.parquet",
    "KBO(2군)":    "KBO_Minor.parquet",
    "AAA(마이너)": "AAA.parquet",
    "KBA(아마)":   "TeamExclusive.parquet",
}

CACHE_DIR = "/tmp"

# ════════════════════════════════════════════════════════════
# 데이터 로드 ── st.cache_data 제거, 순수 함수로 변경
# (Streamlit context 밖에서도 안전하게 동작)
# ════════════════════════════════════════════════════════════
_mem_cache: dict = {}   # 메모리 캐시 (프로세스 재시작 전까지 유지)

def load_league_data(league_option: str, min_year: int = 2023) -> pd.DataFrame:
    """
    league_option : "KBO(1군)" | "KBO(2군)" | "AAA(마이너)" | "KBA(아마)"
    예외를 raise 하여 호출부(app.py)에서 traceback 을 표시하게 함.
    """
    # ── 메모리 캐시 ─────────────────────────────────────────
    cache_key = f"{league_option}_{min_year}"
    if cache_key in _mem_cache:
        return _mem_cache[cache_key]

    file_name = LEAGUE_FILES.get(league_option)
    if file_name is None:
        raise ValueError(f"알 수 없는 리그 옵션: {league_option}")

    cache_path = os.path.join(CACHE_DIR, file_name)

    # ── 로컬 파일 캐시 ───────────────────────────────────────
    if os.path.exists(cache_path):
        df_tmp = pd.read_parquet(cache_path)
        result = df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp
        _mem_cache[cache_key] = result
        return result

    # ── GitHub Release 다운로드 ──────────────────────────────
    release_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}"
        f"/releases/tags/{TAG_NAME}"
    )
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    response = requests.get(release_url, headers=headers, timeout=30)
    if response.status_code != 200:
        raise ConnectionError(
            f"GitHub Release 접근 실패 (status={response.status_code})\n"
            f"URL: {release_url}\n"
            f"응답: {response.text[:300]}"
        )

    assets = response.json().get("assets", [])
    target_asset = next((a for a in assets if a["name"] == file_name), None)
    if target_asset is None:
        available = [a["name"] for a in assets]
        raise FileNotFoundError(
            f"'{file_name}' 파일을 Release 에서 찾을 수 없습니다.\n"
            f"사용 가능한 파일 목록: {available}"
        )

    dl_headers = {"Accept": "application/octet-stream"}
    if GITHUB_TOKEN:
        dl_headers["Authorization"] = f"token {GITHUB_TOKEN}"

    res = requests.get(target_asset["url"], headers=dl_headers, timeout=120)
    if res.status_code != 200:
        raise ConnectionError(f"파일 다운로드 실패 (status={res.status_code})")

    df_tmp = pd.read_parquet(BytesIO(res.content))
    df_tmp.to_parquet(cache_path, index=False)   # 로컬 캐시 저장

    result = df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp
    _mem_cache[cache_key] = result
    return result


# ════════════════════════════════════════════════════════════
# 투수 목록 생성
# ════════════════════════════════════════════════════════════
def get_team_list(df: pd.DataFrame) -> list:
    if "pitcherteam" not in df.columns:
        raise KeyError(
            f"'pitcherteam' 컬럼이 없습니다. "
            f"실제 컬럼 목록: {list(df.columns)}"
        )
    latest_year = df["game_year"].max()
    teams = (
        df[df["game_year"] == latest_year]["pitcherteam"]
        .dropna().unique().tolist()
    )
    return sorted(teams)


def get_pitcher_list(df: pd.DataFrame, team: str) -> list:
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
        throw = (
            f" ({row[throws_col]})"
            if throws_col and pd.notna(row.get(throws_col)) else ""
        )
        options.append({"label": f"{name}{throw}", "value": name})
    options.sort(key=lambda x: x["value"])
    return options


def get_player_df(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    return df[df["pitname"] == player_name].copy()


# ════════════════════════════════════════════════════════════
# stats 계산 함수
# ════════════════════════════════════════════════════════════
OUT_EVENTS = [
    "field_out", "strikeout", "grounded_into_double_play",
    "double_play", "force_out", "sac_fly", "sac_bunt",
    "fielders_choice_out", "strikeout_double_play",
    "other_out", "triple_play",
]


def base_df(player_df: pd.DataFrame) -> pd.DataFrame:
    df = player_df.copy()
    if "game_year" not in df.columns and "game_date" in df.columns:
        df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
        df["game_year"] = df["game_date"].dt.year

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
    idx_cols = [c for c in ["game_year", "stand", "pitch_name"]
                if c in merged_df.columns]

    count_col = "pitch_number" if "pitch_number" in merged_df.columns else "is_swinging_strike"

    pitch_stats = merged_df.groupby(idx_cols).agg(
        total_pitch=(count_col, "count"),
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
    result["K%"]     = (result["K"]    / result["PA"]           * 100).round(1)
    result["BB%"]    = (result["BB"]   / result["PA"]           * 100).round(1)
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
    return base_df(player_df)
