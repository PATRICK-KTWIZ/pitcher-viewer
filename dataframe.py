import os
import pandas as pd
import numpy as np
from io import BytesIO
import requests

# ════════════════════════════════════════════════════════════
# 1. 설정
# ════════════════════════════════════════════════════════════

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

OWNER    = "Henryjeon1"
REPO     = "ktdata"
TAG_NAME = "KoreaBaseballOrganization"

LEAGUE_FILES = {
    "KBO":   "KoreaBaseballOrganization.parquet",
    "NPB":   "NPB.parquet",
    "AAA":   "AAA.parquet",
    "Minor": "Minor.parquet",
}
LEAGUE_LABELS = {
    "KBO":   "KBO",
    "NPB":   "NPB",
    "AAA":   "AAA",
    "Minor": "KBO_Minor",
}

CACHE_DIR = "/tmp"
MIN_YEAR  = 2023

# ════════════════════════════════════════════════════════════
# 2. 데이터 로드
# ════════════════════════════════════════════════════════════

def load_league_data(league_name: str, min_year: int = MIN_YEAR) -> pd.DataFrame:
    """
    league_name 에 해당하는 parquet 데이터를 로드한다.
    로컬 캐시가 있으면 캐시에서, 없으면 GitHub Release에서 다운로드한다.
    """
    if league_name not in LEAGUE_FILES:
        print(f"[{league_name}] LEAGUE_FILES에 정의되지 않은 리그입니다.")
        return pd.DataFrame()

    file_name  = LEAGUE_FILES[league_name]
    cache_path = os.path.join(CACHE_DIR, file_name)

    # ── 로컬 캐시 우선 로드 ───────────────────────────────────────────────
    if os.path.exists(cache_path):
        print(f"[{league_name}] 로컬 캐시에서 로드 중...")
        df_tmp = pd.read_parquet(cache_path)
        return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp

    # ── GitHub Release에서 다운로드 ──────────────────────────────────────
    print(f"[{league_name}] GitHub Release에서 다운로드 중...")
    release_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG_NAME}"
    headers     = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    response = requests.get(release_url, headers=headers)
    if response.status_code != 200:
        print(f"Release 접근 실패: {response.status_code}")
        return pd.DataFrame()

    assets       = response.json().get("assets", [])
    target_asset = next((a for a in assets if a["name"] == file_name), None)
    if not target_asset:
        print(f"{file_name} 파일을 찾을 수 없습니다.")
        return pd.DataFrame()

    with requests.Session() as session:
        session.headers.update({
            "Accept"       : "application/octet-stream",
            "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else ""
        })
        res = session.get(target_asset["url"])
        if res.status_code != 200:
            print(f"다운로드 실패: {res.status_code}")
            return pd.DataFrame()
        try:
            df_tmp = pd.read_parquet(BytesIO(res.content))
            df_tmp.to_parquet(cache_path, index=False)
            print(f"[{league_name}] 불러오기 성공 & 캐시 저장 완료 ({df_tmp.shape[0]:,}행)")
            return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp
        except Exception as e:
            print(f"파싱 실패: {e}")
            return pd.DataFrame()


# ════════════════════════════════════════════════════════════
# 3. definition.py 에서 사용하는 집계 헬퍼 함수
# ════════════════════════════════════════════════════════════

def base_df(player_df: pd.DataFrame) -> pd.DataFrame:
    """
    투수 원시 데이터를 game_year 단위로 집계한 베이스 DataFrame 반환.
    """
    sdf = player_df.copy()

    # ── 기본 카운트 집계 ──────────────────────────────────────────────────
    agg = sdf.groupby("game_year").agg(
        game_date      = ("game_date",       "nunique"),   # 경기수
        pitname        = ("pitname",         "count"),     # 투구수
        pa             = ("pa_flag",         "sum"),       # 타석
        ab             = ("ab_flag",         "sum"),       # 타수
        hit            = ("hit",             "sum"),
        walk           = ("walk",            "sum"),
        strikeout      = ("strikeout",       "sum"),
        inplay         = ("inplay",          "sum"),
        exit_velocity  = ("exit_velocity",   "mean"),
        launch_angle   = ("launch_angle",    "mean"),
        total_bases    = ("total_bases",     "sum"),
        # 존 관련
        z_pitch        = ("z_pitch",         "sum"),
        o_pitch        = ("o_pitch",         "sum"),
        z_swing        = ("z_swing",         "sum"),
        o_swing        = ("o_swing",         "sum"),
        z_contact      = ("z_contact",       "sum"),
        o_contact      = ("o_contact",       "sum"),
        z_inplay       = ("z_inplay",        "sum"),
        o_inplay       = ("o_inplay",        "sum"),
        first_swing    = ("first_swing",     "sum"),
        first_pitch    = ("first_pitch",     "sum"),
        swing          = ("swing",           "sum"),
        whiff          = ("whiff",           "sum"),
        inplay_sw      = ("inplay_sw",       "sum"),
        # LSA
        lsa1           = ("lsa1",            "sum"),
        lsa2           = ("lsa2",            "sum"),
        lsa3           = ("lsa3",            "sum"),
        lsa4           = ("lsa4",            "sum"),
        lsa5           = ("lsa5",            "sum"),
        lsa6           = ("lsa6",            "sum"),
        # 존외 스윙 어프로치
        high_z_swing   = ("high_z_swing",    "sum"),
        high_o_swing   = ("high_o_swing",    "sum"),
        low_z_swing    = ("low_z_swing",     "sum"),
        low_o_swing    = ("low_o_swing",     "sum"),
    ).reset_index()

    return agg


def pivot_base_df(player_df: pd.DataFrame, pivot_index) -> pd.DataFrame:
    """
    pivot_index 를 추가 그룹 키로 사용하는 집계 DataFrame 반환.
    pivot_index : str 또는 list[str]
    """
    sdf = player_df.copy()

    if isinstance(pivot_index, str):
        group_keys = ["game_year", pivot_index]
    else:
        group_keys = ["game_year"] + list(pivot_index)

    agg = sdf.groupby(group_keys).agg(
        game_date      = ("game_date",       "nunique"),
        pitname        = ("pitname",         "count"),
        pa             = ("pa_flag",         "sum"),
        ab             = ("ab_flag",         "sum"),
        hit            = ("hit",             "sum"),
        walk           = ("walk",            "sum"),
        strikeout      = ("strikeout",       "sum"),
        inplay         = ("inplay",          "sum"),
        exit_velocity  = ("exit_velocity",   "mean"),
        launch_angle   = ("launch_angle",    "mean"),
        total_bases    = ("total_bases",     "sum"),
        z_pitch        = ("z_pitch",         "sum"),
        o_pitch        = ("o_pitch",         "sum"),
        z_swing        = ("z_swing",         "sum"),
        o_swing        = ("o_swing",         "sum"),
        z_contact      = ("z_contact",       "sum"),
        o_contact      = ("o_contact",       "sum"),
        z_inplay       = ("z_inplay",        "sum"),
        o_inplay       = ("o_inplay",        "sum"),
        first_swing    = ("first_swing",     "sum"),
        first_pitch    = ("first_pitch",     "sum"),
        swing          = ("swing",           "sum"),
        whiff          = ("whiff",           "sum"),
        inplay_sw      = ("inplay_sw",       "sum"),
        lsa1           = ("lsa1",            "sum"),
        lsa2           = ("lsa2",            "sum"),
        lsa3           = ("lsa3",            "sum"),
        lsa4           = ("lsa4",            "sum"),
        lsa5           = ("lsa5",            "sum"),
        lsa6           = ("lsa6",            "sum"),
        high_z_swing   = ("high_z_swing",    "sum"),
        high_o_swing   = ("high_o_swing",    "sum"),
        low_z_swing    = ("low_z_swing",     "sum"),
        low_o_swing    = ("low_o_swing",     "sum"),
    ).reset_index()

    return agg


def stats_df(agg: pd.DataFrame) -> pd.DataFrame:
    """
    base_df / pivot_base_df 결과를 받아 비율 지표를 계산하고
    game_year (+ 추가 인덱스) 를 인덱스로 설정한 DataFrame 반환.
    """
    df = agg.copy()

    # ── 비율 지표 계산 ────────────────────────────────────────────────────
    def _safe(num, den, scale=1, default=0.0):
        return np.where(den > 0, (num / den) * scale, default)

    df["inplay_pit"]    = _safe(df["inplay"],    df["pitname"])
    df["launch_angleX"] = df["launch_angle"].round(1)

    # 타율 / 출루율 / 장타율 / OPS
    df["avg"] = _safe(df["hit"],                          df["ab"])
    df["obp"] = _safe(df["hit"] + df["walk"],             df["pa"])
    df["slg"] = _safe(df["total_bases"],                  df["ab"])
    df["ops"] = df["obp"] + df["slg"]

    # LSA 비율
    lsa_total        = df[["lsa1","lsa2","lsa3","lsa4","lsa5","lsa6"]].sum(axis=1)
    df["weak"]        = _safe(df["lsa1"], lsa_total, 100)
    df["topped"]      = _safe(df["lsa2"], lsa_total, 100)
    df["under"]       = _safe(df["lsa3"], lsa_total, 100)
    df["flare"]       = _safe(df["lsa4"], lsa_total, 100)
    df["solid_contact"]= _safe(df["lsa5"], lsa_total, 100)
    df["barrel"]      = _safe(df["lsa6"], lsa_total, 100)

    # 존 / 스윙 지표
    total_pitch       = df["z_pitch"] + df["o_pitch"]
    df["z%"]          = _safe(df["z_pitch"],   total_pitch,   100)
    df["o%"]          = _safe(df["o_pitch"],   total_pitch,   100)
    df["z_swing%"]    = _safe(df["z_swing"],   df["z_pitch"], 100)
    df["o_swing%"]    = _safe(df["o_swing"],   df["o_pitch"], 100)
    df["z_con%"]      = _safe(df["z_contact"], df["z_swing"], 100)
    df["o_con%"]      = _safe(df["o_contact"], df["o_swing"], 100)
    df["z_inplay%"]   = _safe(df["z_inplay"],  df["z_swing"], 100)
    df["o_inplay%"]   = _safe(df["o_inplay"],  df["o_swing"], 100)
    df["f_swing%"]    = _safe(df["first_swing"],df["first_pitch"], 100)
    df["swing%"]      = _safe(df["swing"],     df["pitname"], 100)
    df["whiff%"]      = _safe(df["whiff"],     df["swing"],   100)
    df["inplay_sw"]   = _safe(df["inplay_sw"], df["swing"],   100)
    df["plus_lsa4"]   = df["flare"] + df["solid_contact"] + df["barrel"]

    # 타격 어프로치 분류
    league_z_swing_avg = 65.0   # 리그 평균값 (필요 시 조정)
    league_o_swing_avg = 30.0
    df["approach"] = np.select(
        [
            (df["z_swing%"] >= league_z_swing_avg) & (df["o_swing%"] >= league_o_swing_avg),
            (df["z_swing%"] >= league_z_swing_avg) & (df["o_swing%"] <  league_o_swing_avg),
            (df["z_swing%"] <  league_z_swing_avg) & (df["o_swing%"] >= league_o_swing_avg),
            (df["z_swing%"] <  league_z_swing_avg) & (df["o_swing%"] <  league_o_swing_avg),
        ],
        ["Free Swinger", "Zone Contact", "Chase", "Patient"],
        default="Unknown"
    )

    # ── 반올림 ────────────────────────────────────────────────────────────
    pct_cols = ["z%","o%","z_swing%","o_swing%","z_con%","o_con%",
                "z_inplay%","o_inplay%","f_swing%","swing%","whiff%","inplay_sw",
                "plus_lsa4","weak","topped","under","flare","solid_contact","barrel"]
    df[pct_cols]         = df[pct_cols].round(1)
    df["avg"]            = df["avg"].round(3)
    df["obp"]            = df["obp"].round(3)
    df["slg"]            = df["slg"].round(3)
    df["ops"]            = df["ops"].round(3)
    df["exit_velocity"]  = df["exit_velocity"].round(1)
    df["inplay_pit"]     = df["inplay_pit"].round(3)

    # ── 인덱스 설정 ───────────────────────────────────────────────────────
    # game_year 외 추가 컬럼이 있으면 MultiIndex
    extra_cols = [c for c in df.columns
                  if c not in (
                      ["game_year"] +
                      list(agg.columns[agg.columns != "game_year"])
                  ) or c in ["stand", "pitch_name"]]
    index_cols = ["game_year"]
    for c in ["stand", "pitch_name"]:
        if c in df.columns:
            index_cols.append(c)

    df = df.set_index(index_cols)
    return df
