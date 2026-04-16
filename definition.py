import pandas as pd
from dataframe import base_df, stats_df, pivot_base_df

# ════════════════════════════════════════════════════════════
# 리그 선택 → 파일명 매핑 (dataframe.py 의 LEAGUE_FILES 와 동일 키)
# ════════════════════════════════════════════════════════════
LEAGUE_OPTIONS = ["KBO(1군)", "KBO(2군)", "AAA(마이너)", "KBA(아마)"]


# ════════════════════════════════════════════════════════════
# 기존 stats / season_stand 함수 (player_df 기반)
# ════════════════════════════════════════════════════════════
def stats(player_df):
    merged_base_df   = base_df(player_df)
    stats_output_df  = stats_df(merged_base_df)
    season_stats_df  = stats_output_df.reindex([2025, 2024, 2023])
    return season_stats_df


def season_stand(player_df):
    season = player_df["game_year"] >= 2023
    sdf    = player_df[season]

    pivot_index    = "stand"
    merged_base_df = pivot_base_df(sdf, pivot_index)
    season_df      = stats_df(merged_base_df)

    season_df = season_df.reindex([2025, 2024, 2023], level="game_year")
    season_df = season_df.reindex(["R", "L"],         level="stand")
    season_df = season_df.reset_index()
    season_df = season_df.astype({"game_year": "str"})
    return season_df


# ────────────────────────────────────────────────────────────
# 구종별 stats viewer
# ────────────────────────────────────────────────────────────
def season_pitchname(player_df):
    season = player_df["game_year"] >= 2023
    sdf    = player_df[season]

    pitch_order = [
        "4-Seam Fastball", "2-Seam Fastball", "Cutter", "Slider",
        "Sweeper", "Curveball", "Changeup", "Split-Finger",
    ]
    pivot_index    = "pitch_name"
    merged_base_df = pivot_base_df(sdf, pivot_index)
    season_df      = stats_df(merged_base_df)

    season_df = season_df.reindex([2025, 2024, 2023], level="game_year")
    season_df = season_df.reindex(
        [p for p in pitch_order if p in season_df.index.get_level_values("pitch_name")],
        level="pitch_name",
    )
    season_df = season_df.reset_index()
    season_df = season_df.astype({"game_year": "str"})
    return season_df


# ────────────────────────────────────────────────────────────
# stats_viewer / swing_viewer  (시즌 집계)
# ────────────────────────────────────────────────────────────
def _season_agg(player_df, cols, round_map=None):
    """공통 시즌 집계 헬퍼"""
    season = player_df["game_year"] >= 2023
    sdf    = player_df[season].copy()
    if round_map:
        for col, dec in round_map.items():
            if col in sdf.columns:
                sdf[col] = sdf[col].round(dec)
    return sdf


def stats_viewer(player_df):
    sdf = _season_agg(player_df, [])
    return sdf


def swing_viewer(player_df):
    sdf = _season_agg(player_df, [])
    return sdf


def stats_viewer_stand(player_df):
    sdf = _season_agg(player_df, [])
    return sdf


def swing_viewer_stand(player_df):
    sdf = _season_agg(player_df, [])
    return sdf


def movement_dataframe(player_df):
    season = player_df["game_year"] >= 2023
    sdf    = player_df[season].copy()
    return sdf


# ────────────────────────────────────────────────────────────
# pitchname 기반 viewer
# ────────────────────────────────────────────────────────────
def stats_viewer_pitchname(player_df):
    return _season_agg(player_df, [])


def swing_viewer_pitchname(player_df):
    return _season_agg(player_df, [])


def season_stand_pitchname(player_df):
    return season_pitchname(player_df)


def swing_viewer_stand_pitchname(player_df):
    return _season_agg(player_df, [])


def stats_viewer_stand_pitchname(player_df):
    return _season_agg(player_df, [])
