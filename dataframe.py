import os
import pandas as pd
import numpy as np
from io import BytesIO
import requests
import streamlit as st

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
    if league_name not in LEAGUE_FILES:
        print(f"[{league_name}] LEAGUE_FILES에 정의되지 않은 리그입니다.")
        return pd.DataFrame()

    file_name  = LEAGUE_FILES[league_name]
    cache_path = os.path.join(CACHE_DIR, file_name)

    if os.path.exists(cache_path):
        print(f"[{league_name}] 로컬 캐시에서 로드 중...")
        df_tmp = pd.read_parquet(cache_path)
        return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp

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
# 3. 집계 헬퍼 함수 (definition.py 에서 사용)
# ════════════════════════════════════════════════════════════

def base_df(player_df):

    game = pd.pivot_table(player_df, index='game_year', values='game_date', aggfunc='nunique', margins=False)
    pitched = pd.pivot_table(player_df, index='game_year', values='pitname', aggfunc='count', margins=False)
    rel_speed = pd.pivot_table(player_df, index='game_year', values='rel_speed(km)', aggfunc='mean', margins=False)
    inplay = pd.pivot_table(player_df, index='game_year', values='inplay', aggfunc='sum', margins=False)
    exit_velocity = pd.pivot_table(player_df, index='game_year', values='exit_velocity', aggfunc='mean', margins=False)
    launch_angleX = pd.pivot_table(player_df, index='game_year', values='launch_angleX', aggfunc='mean', margins=False)

    hit = pd.pivot_table(player_df, index='game_year', values='hit', aggfunc='sum', margins=False)
    ab = pd.pivot_table(player_df, index='game_year', values='ab', aggfunc='sum', margins=False)
    pa = pd.pivot_table(player_df, index='game_year', values='pa', aggfunc='sum', margins=False)
    single = pd.pivot_table(player_df, index='game_year', values='single', aggfunc='sum', margins=False)
    double = pd.pivot_table(player_df, index='game_year', values='double', aggfunc='sum', margins=False)
    triple = pd.pivot_table(player_df, index='game_year', values='triple', aggfunc='sum', margins=False)
    home_run = pd.pivot_table(player_df, index='game_year', values='home_run', aggfunc='sum', margins=False)
    walk = pd.pivot_table(player_df, index='game_year', values='walk', aggfunc='sum', margins=False)
    strikeout = pd.pivot_table(player_df, index='game_year', values='strikeout', aggfunc='sum', margins=False)
    hit_by_pitch = pd.pivot_table(player_df, index='game_year', values='hit_by_pitch', aggfunc='sum', margins=False)
    sac_fly = pd.pivot_table(player_df, index='game_year', values='sac_fly', aggfunc='sum', margins=False)

    z_in = pd.pivot_table(player_df, index='game_year', values='z_in', aggfunc='sum', margins=False)
    z_swing = pd.pivot_table(player_df, index='game_year', values='z_swing', aggfunc='sum', margins=False)
    z_con = pd.pivot_table(player_df, index='game_year', values='z_con', aggfunc='sum', margins=False)
    z_out = pd.pivot_table(player_df, index='game_year', values='z_out', aggfunc='sum', margins=False)
    z_inplay = pd.pivot_table(player_df, index='game_year', values='z_inplay', aggfunc='sum', margins=False)
    o_swing = pd.pivot_table(player_df, index='game_year', values='o_swing', aggfunc='sum', margins=False)
    o_con = pd.pivot_table(player_df, index='game_year', values='o_con', aggfunc='sum', margins=False)
    o_inplay = pd.pivot_table(player_df, index='game_year', values='o_inplay', aggfunc='sum', margins=False)

    f_swing = pd.pivot_table(player_df, index='game_year', values='f_swing', aggfunc='sum', margins=False)
    f_pitch = pd.pivot_table(player_df, index='game_year', values='f_pitch', aggfunc='sum', margins=False)
    swing = pd.pivot_table(player_df, index='game_year', values='swing', aggfunc='sum', margins=False)
    whiff = pd.pivot_table(player_df, index='game_year', values='whiff', aggfunc='sum', margins=False)

    weak = pd.pivot_table(player_df, index='game_year', values='weak', aggfunc='sum', margins=False)
    topped = pd.pivot_table(player_df, index='game_year', values='topped', aggfunc='sum', margins=False)
    under = pd.pivot_table(player_df, index='game_year', values='under', aggfunc='sum', margins=False)
    flare = pd.pivot_table(player_df, index='game_year', values='flare', aggfunc='sum', margins=False)
    solid_contact = pd.pivot_table(player_df, index='game_year', values='solid_contact', aggfunc='sum', margins=False)
    barrel = pd.pivot_table(player_df, index='game_year', values='barrel', aggfunc='sum', margins=False)

    merged_base_df = pd.concat([game, pitched, rel_speed, inplay, exit_velocity, launch_angleX, hit, ab, pa, single, double, triple, home_run, walk, strikeout, hit_by_pitch, sac_fly,
                        z_in, z_swing, z_con, z_out, z_inplay, o_swing, o_con, o_inplay, f_swing, f_pitch, swing, whiff,
                        weak, topped, under, flare, solid_contact, barrel], axis=1)
    
    return merged_base_df


def pivot_base_df(player_df, pivot_index):

    game = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='game_date', aggfunc='nunique', margins=True))
    pitched = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='pitname', aggfunc='count', margins=True))
    rel_speed = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='rel_speed(km)', aggfunc='mean', margins=True))
    inplay = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='inplay', aggfunc='sum', margins=True))
    exit_velocity = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='exit_velocity', aggfunc='mean', margins=True))
    launch_angleX = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='launch_angleX', aggfunc='mean', margins=True))
    hit_spin_rate = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='hit_spin_rate', aggfunc='mean', margins=True))

    hit = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='hit', aggfunc='sum', margins=True))
    ab = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='ab', aggfunc='sum', margins=True))
    pa = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='pa', aggfunc='sum', margins=True))
    single = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='single', aggfunc='sum', margins=True))
    double = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='double', aggfunc='sum', margins=True))
    triple = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='triple', aggfunc='sum', margins=True))
    home_run = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='home_run', aggfunc='sum', margins=True))
    walk = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='walk', aggfunc='sum', margins=True))
    strikeout = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='strikeout', aggfunc='sum', margins=True))
    hit_by_pitch = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='hit_by_pitch', aggfunc='sum', margins=True))
    sac_fly = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='sac_fly', aggfunc='sum', margins=True))

    z_in = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='z_in', aggfunc='sum', margins=True))
    z_swing = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='z_swing', aggfunc='sum', margins=True))
    z_con = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='z_con', aggfunc='sum', margins=True))
    z_out = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='z_out', aggfunc='sum', margins=True))
    z_inplay = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='z_inplay', aggfunc='sum', margins=True))
    o_swing = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='o_swing', aggfunc='sum', margins=True))
    o_con = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='o_con', aggfunc='sum', margins=True))
    o_inplay = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='o_inplay', aggfunc='sum', margins=True))

    f_swing = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='f_swing', aggfunc='sum', margins=True))
    f_pitch = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='f_pitch', aggfunc='sum', margins=True))
    swing = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='swing', aggfunc='sum', margins=True))
    whiff = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='whiff', aggfunc='sum', margins=True))

    weak = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='weak', aggfunc='sum', margins=True))
    topped = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='topped', aggfunc='sum', margins=True))
    under = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='under', aggfunc='sum', margins=True))
    flare = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='flare', aggfunc='sum', margins=True))
    solid_contact = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='solid_contact', aggfunc='sum', margins=True))
    barrel = player_df.groupby(['game_year']).apply(lambda x: x.pivot_table(index=pivot_index, values='barrel', aggfunc='sum', margins=True))

    pivot_df = pd.concat([game, pitched, rel_speed, inplay, exit_velocity, launch_angleX, hit_spin_rate, hit, ab, pa, single, double, triple, home_run, walk, strikeout, hit_by_pitch, sac_fly,
                        z_in, z_swing, z_con, z_out, z_inplay, o_swing, o_con, o_inplay, f_swing, f_pitch, swing, whiff,
                        weak, topped, under, flare, solid_contact, barrel], axis=1)
    
    return pivot_df


def stats_df(merged_base_df):
    merged_base_df['avg'] = 0.0
    merged_base_df['obp'] = 0.0
    merged_base_df['slg'] = 0.0
    merged_base_df['ops'] = 0.0
    
    mask_ab = merged_base_df['ab'] > 0
    if mask_ab.any():
        merged_base_df.loc[mask_ab, 'avg'] = merged_base_df.loc[mask_ab, 'hit'] / merged_base_df.loc[mask_ab, 'ab']
    
    obp_denominator = merged_base_df['ab'] + merged_base_df['hit_by_pitch'] + merged_base_df['walk'] + merged_base_df['sac_fly']
    mask_obp = obp_denominator > 0
    if mask_obp.any():
        obp_numerator = merged_base_df['hit'] + merged_base_df['hit_by_pitch'] + merged_base_df['walk']
        merged_base_df.loc[mask_obp, 'obp'] = obp_numerator[mask_obp] / obp_denominator[mask_obp]
    
    slg_numerator = ((merged_base_df['single'] * 1) + (merged_base_df['double'] * 2) + 
                     (merged_base_df['triple'] * 3) + (merged_base_df['home_run'] * 4))
    if mask_ab.any():
        merged_base_df.loc[mask_ab, 'slg'] = slg_numerator[mask_ab] / merged_base_df.loc[mask_ab, 'ab']
    
    merged_base_df['ops'] = merged_base_df['obp'] + merged_base_df['slg']
    
    mask_player = merged_base_df['pitname'] > 0
    if mask_player.any():
        merged_base_df.loc[mask_player, 'z%'] = merged_base_df.loc[mask_player, 'z_in'] / merged_base_df.loc[mask_player, 'pitname']
        merged_base_df.loc[mask_player, 'inplay_pit'] = merged_base_df.loc[mask_player, 'inplay'] / merged_base_df.loc[mask_player, 'pitname']
    
    mask_z_in = merged_base_df['z_in'] > 0
    if mask_z_in.any():
        merged_base_df.loc[mask_z_in, 'z_swing%'] = merged_base_df.loc[mask_z_in, 'z_swing'] / merged_base_df.loc[mask_z_in, 'z_in']
    
    mask_z_swing = merged_base_df['z_swing'] > 0
    if mask_z_swing.any():
        merged_base_df.loc[mask_z_swing, 'z_con%'] = merged_base_df.loc[mask_z_swing, 'z_con'] / merged_base_df.loc[mask_z_swing, 'z_swing']
        merged_base_df.loc[mask_z_swing, 'z_inplay%'] = merged_base_df.loc[mask_z_swing, 'z_inplay'] / merged_base_df.loc[mask_z_swing, 'z_swing']
    
    if mask_player.any():
        merged_base_df.loc[mask_player, 'o%'] = merged_base_df.loc[mask_player, 'z_out'] / merged_base_df.loc[mask_player, 'pitname']
    
    mask_z_out = merged_base_df['z_out'] > 0
    if mask_z_out.any():
        merged_base_df.loc[mask_z_out, 'o_swing%'] = merged_base_df.loc[mask_z_out, 'o_swing'] / merged_base_df.loc[mask_z_out, 'z_out']
    
    mask_o_swing = merged_base_df['o_swing'] > 0
    if mask_o_swing.any():
        merged_base_df.loc[mask_o_swing, 'o_con%'] = merged_base_df.loc[mask_o_swing, 'o_con'] / merged_base_df.loc[mask_o_swing, 'o_swing']
        merged_base_df.loc[mask_o_swing, 'o_inplay%'] = merged_base_df.loc[mask_o_swing, 'o_inplay'] / merged_base_df.loc[mask_o_swing, 'o_swing']
    
    mask_f_pitch = merged_base_df['f_pitch'] > 0
    if mask_f_pitch.any():
        merged_base_df.loc[mask_f_pitch, 'f_swing%'] = merged_base_df.loc[mask_f_pitch, 'f_swing'] / merged_base_df.loc[mask_f_pitch, 'f_pitch']
    
    if mask_player.any():
        merged_base_df.loc[mask_player, 'swing%'] = merged_base_df.loc[mask_player, 'swing'] / merged_base_df.loc[mask_player, 'pitname']
    
    mask_swing = merged_base_df['swing'] > 0
    if mask_swing.any():
        merged_base_df.loc[mask_swing, 'whiff%'] = merged_base_df.loc[mask_swing, 'whiff'] / merged_base_df.loc[mask_swing, 'swing']
        merged_base_df.loc[mask_swing, 'inplay_sw'] = merged_base_df.loc[mask_swing, 'inplay'] / merged_base_df.loc[mask_swing, 'swing']

    merged_base_df['total_contact'] = (merged_base_df['weak'] + merged_base_df['topped'] + 
                                       merged_base_df['under'] + merged_base_df['flare'] + 
                                       merged_base_df['solid_contact'] + merged_base_df['barrel'])
    
    mask_contact = merged_base_df['total_contact'] > 0
    if mask_contact.any():
        merged_base_df.loc[mask_contact, 'weak']         = merged_base_df.loc[mask_contact, 'weak']         / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'topped']       = merged_base_df.loc[mask_contact, 'topped']       / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'under']        = merged_base_df.loc[mask_contact, 'under']        / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'flare']        = merged_base_df.loc[mask_contact, 'flare']        / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'solid_contact']= merged_base_df.loc[mask_contact, 'solid_contact']/ merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'barrel']       = merged_base_df.loc[mask_contact, 'barrel']       / merged_base_df.loc[mask_contact, 'total_contact']

    merged_base_df['plus_lsa4'] = merged_base_df['flare'] + merged_base_df['solid_contact'] + merged_base_df['barrel']
    
    kbo_z_swing = 0.654
    kbo_o_swing = 0.261
    valid_rows = merged_base_df['z_swing%'].notna() & merged_base_df['o_swing%'].notna()
    merged_base_df['approach'] = 'Not Specified'
    if valid_rows.any():
        condition = [
            (merged_base_df['z_swing%'] >= kbo_z_swing) & (merged_base_df['o_swing%'] >= kbo_o_swing) & valid_rows,
            (merged_base_df['z_swing%'] >= kbo_z_swing) & (merged_base_df['o_swing%'] < kbo_o_swing) & valid_rows,
            (merged_base_df['z_swing%'] < kbo_z_swing) & (merged_base_df['o_swing%'] >= kbo_o_swing) & valid_rows,
            (merged_base_df['z_swing%'] < kbo_z_swing) & (merged_base_df['o_swing%'] < kbo_o_swing) & valid_rows
        ]
        choicelist = ['Aggressive', 'Selective', 'Non_Selective', 'Passive']
        merged_base_df['approach'] = np.select(condition, choicelist, default='Not Specified')

    stats_output_df = merged_base_df[['game_date', 'pitname', 'pa', 'ab', 'hit', 'walk', 'strikeout','rel_speed(km)', 
                                     'inplay_pit', 'exit_velocity', 'launch_angleX',  
                                     'avg', 'obp', 'slg', 'ops', 'z%', 'z_swing%', 'z_con%', 'z_inplay%', 
                                     'o%', 'o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%', 
                                     'inplay_sw', 'weak', 'topped', 'under', 'flare', 'solid_contact', 
                                     'barrel', 'approach', 'plus_lsa4']]

    percent_columns = ['inplay_pit', 'z%', 'z_swing%', 'z_con%', 'z_inplay%', 'o%', 'o_swing%', 'o_con%', 
                      'o_inplay%', 'f_swing%', 'swing%', 'whiff%', 'inplay_sw',
                      'weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel', 'plus_lsa4']
    for col in percent_columns:
        stats_output_df[col] = stats_output_df[col] * 100
                
    round_dict = {
        'game_date':0, 'pitname':0,'pa': 0, 'ab': 0, 'hit': 0, 'walk': 0, 'strikeout': 0, 'rel_speed(km)': 1, 'inplay_pit': 1, 
        'exit_velocity': 1, 'launch_angleX': 1, 'hit_spin_rate': 0, 'avg': 3, 
        'obp': 3, 'slg': 3, 'ops': 3, 'z%': 1, 'z_swing%': 1, 'z_con%': 1, 
        'z_inplay%': 1, 'o%': 1, 'o_swing%': 1, 'o_con%': 1, 'o_inplay%': 1, 
        'f_swing%': 1, 'swing%': 1, 'whiff%': 1, 'inplay_sw': 1, 'inplay%': 1, 
        'weak': 1, 'topped': 1, 'under': 1, 'flare': 1, 'solid_contact': 1, 'barrel': 1,
        'plus_lsa4': 1
    }

    round_dict_corrected = {k: v for i, (k, v) in enumerate(round_dict.items()) if k not in list(round_dict.keys())[:i]}
    existing_columns = {col: dec for col, dec in round_dict_corrected.items() if col in stats_output_df.columns}
    if existing_columns:
        for col, dec in existing_columns.items():
            try:
                if pd.api.types.is_numeric_dtype(stats_output_df[col]):
                    stats_output_df[col] = stats_output_df[col].round(dec)
            except:
                pass

    for column, decimals in round_dict_corrected.items():
        if column in stats_output_df.columns:
            try:
                def format_value(x):
                    if pd.isna(x):
                        return "-"
                    elif decimals == 0:
                        try:
                            return f"{int(x)}"
                        except:
                            return "-"
                    else:
                        try:
                            if column in percent_columns:
                                return f"{float(x):.{decimals}f}%"
                            else:
                                return f"{float(x):.{decimals}f}"
                        except:
                            return "-"
                stats_output_df[column] = stats_output_df[column].apply(format_value)
            except Exception as e:
                print(f"열 '{column}' 처리 중 오류 발생: {e}")
                continue

    return stats_output_df
