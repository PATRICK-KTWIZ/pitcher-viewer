import pandas as pd
from datetime import timedelta
from dataframe import dataframe, base_df, stats_df, pivot_base_df
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
# from IPython.display import display, HTML

def select_league(option):

    if option == "KBO(1군)":
        league = "'KoreaBaseballOrganization'"
        return league
    elif option == "KBO(2군)":
        league = "'KBO Minors'"
        return league
    elif option == "AAA(마이너)":
        league =  "'aaa'"
        return league
    elif option == "KBA(아마)":
        league =  "'TeamExclusive'"
        return league
    else:
        league == "'KoreaBaseballOrganization'"
        return league


def stats(player_df):

    merged_base_df = base_df(player_df)
    stats_output_df = stats_df(merged_base_df)
    
    season_stats_df = stats_output_df.reindex([2025, 2024, 2023])

    return season_stats_df


def season_stand(player_df):

    season = player_df['game_year'] >= 2023
    sdf = player_df[season]

    pivot_index = 'stand'

    merged_base_df = pivot_base_df(sdf,pivot_index)
    season_pthrows_df = stats_df(merged_base_df)

    season_pthrows_df = season_pthrows_df.reindex([2025, 2024, 2023], level='game_year')
    season_pthrows_df = season_pthrows_df.reindex(['R','L'], level='stand')

    season_pthrows_df = season_pthrows_df.reset_index()
    season_pthrows_df = season_pthrows_df.astype({'game_year':'str'})

    return season_pthrows_df


def season_stand_pitchname(player_df):

    season = player_df['game_year'] >= 2023
    sdf = player_df[season]

    pivot_index = ['stand', 'pitch_name']

    merged_base_df = pivot_base_df(sdf,pivot_index)
    season_stand_pitchname_df = stats_df(merged_base_df)

    season_stand_pitchname_df = season_stand_pitchname_df.reindex([2025, 2024, 2023], level='game_year')
    season_stand_pitchname_df = season_stand_pitchname_df.reindex(['R','L'], level='stand')
    season_stand_pitchname_df = season_stand_pitchname_df.reindex(['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Sweeper', 'Curveball', 'Changeup', 'Split-Finger'], level='pitch_name')

    season_stand_pitchname_df = season_stand_pitchname_df.reset_index()
    season_stand_pitchname_df = season_stand_pitchname_df.astype({'game_year':'str'})

    return season_stand_pitchname_df


def season_pitchname(player_df):

    season = player_df['game_year'] >= 2023
    sdf = player_df[season]

    pivot_index = 'pitch_name'

    merged_base_df = pivot_base_df(sdf,pivot_index)
    season_pitchname_df = stats_df(merged_base_df)

    season_pitchname_df = season_pitchname_df.reindex([2025, 2024, 2023], level='game_year')
    season_pitchname_df = season_pitchname_df.reindex(['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Curveball','Changeup','Split-Finger'], level='pitch_name')

    season_pitchname_df = season_pitchname_df.reset_index()
    season_pitchname_df = season_pitchname_df.astype({'game_year':'str'})

    return season_pitchname_df


def stats_viewer(dataframe):

    stats_viewer_df = dataframe[['game_date', 'pitname','pa','ab','hit','walk','strikeout','inplay_pit','exit_velocity','launch_angleX','obp','slg','avg','ops','weak','topped','under','flare','solid_contact','barrel']]
    stats_viewer_df = stats_viewer_df.rename(columns={'game_year':'구분','game_date':'경기수','pitname':'투구수','pa':'타석','ab':'타수','hit':'피안타','walk':'볼넷','strikeout':'삼진','inplay_pit':'투구당 인플레이','avg':'피안타율','obp':'피출루율','slg':'피장타율','ops':'피OPS', 'exit_velocity':'허용타구속도','launch_angleX':'허용발사각도',
                                                      'weak':'Weak','topped':'Topped','under':'Under','flare':'Flare','solid_contact':'Solid Contact','barrel':'Barrel'})

    return stats_viewer_df

def swing_viewer(dataframe):

    swing_viewer_df = dataframe[['z%','z_swing%','z_con%', 'z_inplay%', 'o%','o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                                'plus_lsa4', 'approach']]
    swing_viewer_df = swing_viewer_df.rename(columns={'game_year':'구분',
                                                        'z%':'존투구%','z_swing%':'존스윙%','z_con%':'존컨택%', 'z_inplay%':'존인플레이%', 
                                                        'o%':'존외부%','o_swing%':'존외스윙%', 'o_con%':'존외컨택%', 'o_inplay%':'존외인플레이%', 
                                                        'f_swing%':'초구스윙%', 'swing%':'스윙%', 'whiff%':'헛스윙%','inplay_sw':'스윙당인플레이%',
                                                        'plus_lsa4':'LSA 4+', 'approach':'상대타격 어프로치'})

    return swing_viewer_df

def stats_viewer_stand(dataframe):

    stats_viewer_pthrows_df = dataframe[['stand','game_date','pitname','pa','ab','hit','walk','strikeout','inplay_pit','exit_velocity','launch_angleX','obp','slg','avg','ops','weak','topped','under','flare','solid_contact','barrel']]
    
    stats_viewer_pthrows_df = stats_viewer_pthrows_df.rename(columns={'game_year':'구분','stand':'타자유형','game_date':'경기수','pitname':'투구수','pa':'타석','ab':'타수','hit':'안타','walk':'볼넷','strikeout':'삼진','avg':'타율','obp':'출루율','slg':'장타율','ops':'OPS','weak':'Weak','topped':'Topped','under':'Under','flare':'Flare','solid_contact':'Solid Contact','barrel':'Barrel',
                                                        'exit_velocity':'타구속도','launch_angleX':'발사각도','hit_spin_rate':'타구스핀량'})

    return stats_viewer_pthrows_df

def swing_viewer_stand(dataframe):

    swing_viewer_pthrows_df = dataframe[['stand','z%','z_swing%','z_con%', 'z_inplay%', 'o%','o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                                'plus_lsa4', 'approach']]
    swing_viewer_pthrows_df = swing_viewer_pthrows_df.rename(columns={'game_year':'구분','stand':'타자유형',
                                                        'z%':'존투구%','z_swing%':'존스윙%','z_con%':'존컨택%', 'z_inplay%':'존인플레이%', 
                                                        'o%':'존외부%','o_swing%':'존외스윙%', 'o_con%':'존외컨택%', 'o_inplay%':'존외인플레이%', 
                                                        'f_swing%':'초구스윙%', 'swing%':'스윙%', 'whiff%':'헛스윙%','inplay_sw':'스윙당인플레이%',
                                                        'plus_lsa4':'LSA 4+', 'approach':'타격 어프로치'})

    return swing_viewer_pthrows_df


def stats_viewer_stand_pitchname(dataframe):

    stats_viewer_stand_pitchname_df = dataframe[['stand','pitch_name','game_date','pitname','pa','ab','hit','walk','strikeout','inplay_pit','exit_velocity','launch_angleX','obp','slg','avg','ops','weak','topped','under','flare','solid_contact','barrel']]
    
    stats_viewer_stand_pitchname_df = stats_viewer_stand_pitchname_df.rename(columns={'game_year':'구분','stand':'타자유형','game_date':'경기수','pitname':'투구수','pa':'타석','ab':'타수','hit':'안타','walk':'볼넷','strikeout':'삼진','avg':'타율','obp':'출루율','slg':'장타율','ops':'OPS','weak':'Weak','topped':'Topped','under':'Under','flare':'Flare','solid_contact':'Solid Contact','barrel':'Barrel',
                                                        'exit_velocity':'타구속도','launch_angleX':'발사각도','hit_spin_rate':'타구스핀량'})

    return stats_viewer_stand_pitchname_df

def swing_viewer_stand_pitchname(dataframe):

    stats_viewer_stand_pitchname_df = dataframe[['stand','pitch_name','z%','z_swing%','z_con%', 'z_inplay%', 'o%','o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                                'plus_lsa4', 'approach']]
    stats_viewer_stand_pitchname_df = stats_viewer_stand_pitchname_df.rename(columns={'game_year':'구분','stand':'타자유형',
                                                        'z%':'존투구%','z_swing%':'존스윙%','z_con%':'존컨택%', 'z_inplay%':'존인플레이%', 
                                                        'o%':'존외부%','o_swing%':'존외스윙%', 'o_con%':'존외컨택%', 'o_inplay%':'존외인플레이%', 
                                                        'f_swing%':'초구스윙%', 'swing%':'스윙%', 'whiff%':'헛스윙%','inplay_sw':'스윙당인플레이%',
                                                        'plus_lsa4':'LSA 4+', 'approach':'타격 어프로치'})

    return stats_viewer_stand_pitchname_df


def stats_viewer_pitchname(dataframe):

    stats_viewer_pitchname_df = dataframe[['pitch_name','pitname','pa','ab','hit','walk','strikeout','inplay_pit','exit_velocity','launch_angleX','obp','slg','avg','ops','weak','topped','under','flare','solid_contact','barrel']]
    stats_viewer_pitchname_df = stats_viewer_pitchname_df.rename(columns={'game_year':'구분','pitch_name':'세부구종','game_date':'경기수','pitname':'투구수','pa':'타석','ab':'타수','hit':'안타','walk':'볼넷','strikeout':'삼진','avg':'타율','obp':'출루율','slg':'장타율','ops':'OPS','weak':'Weak','topped':'Topped','under':'Under','flare':'Flare','solid_contact':'Solid Contact','barrel':'Barrel',
                                                        'exit_velocity':'타구속도','launch_angleX':'발사각도','hit_spin_rate':'타구스핀량'})

    return stats_viewer_pitchname_df

def swing_viewer_pitchname(dataframe):

    swing_viewer_pitchname_df = dataframe[['pitch_name','z%','z_swing%','z_con%', 'z_inplay%', 'o%','o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                                'plus_lsa4', 'approach']]
    swing_viewer_pitchname_df = swing_viewer_pitchname_df.rename(columns={'game_year':'구분','pitch_name':'세부구종',
                                                        'z%':'존투구%','z_swing%':'존스윙%','z_con%':'존컨택%', 'z_inplay%':'존인플레이%', 
                                                        'o%':'존외부%','o_swing%':'존외스윙%', 'o_con%':'존외컨택%', 'o_inplay%':'존외인플레이%', 
                                                        'f_swing%':'초구스윙%', 'swing%':'스윙%', 'whiff%':'헛스윙%','inplay_sw':'스윙당인플레이%',
                                                        'plus_lsa4':'LSA 4+', 'approach':'타격 어프로치'})

    return swing_viewer_pitchname_df


def movement_dataframe(dataframe):

    mov_df = dataframe
    agg_funcs = {
    'pitname': 'count',
    'rel_speed(km)': 'mean',
    'release_spin_rate': 'mean',
    'ver_break': 'mean',
    'hor_break': 'mean',
    'rel_height': 'mean',
    'rel_side': 'mean',
    'extension': 'mean'

    }

    grouped_df = mov_df.groupby(['game_year', 'pitch_name']).agg(agg_funcs)

    grouped_df['ver_break'] =  grouped_df['ver_break'] * 100
    grouped_df['hor_break'] =  grouped_df['hor_break'] * 100


    # 반올림
    grouped_df = grouped_df.round({'rel_speed(km)': 1, 'release_spin_rate': 0, 'ver_break':1,'hor_break':1,'rel_height':2,'extension':2,'rel_side':2})

    # 인덱스 재정렬
    grouped_df = grouped_df.reindex([2025, 2024, 2023], level='game_year')
    grouped_df = grouped_df.reindex(['4-Seam Fastball', '2-Seam Fastball', 'Cutter', 'Slider', 'Curveball', 'Sweeper', 'Changeup', 'Split-Finger'], level='pitch_name')

    grouped_df = grouped_df.reset_index()
    grouped_df = grouped_df.rename(columns={'game_year':'연도','pitch_name':'구종','pitname':'투구수','rel_speed(km)':'평균구속', 'release_spin_rate':'평균회전수','ver_break':'수직Mov','hor_break':'수평Mov',
                                            'rel_height':'릴리스 높이','rel_side':'릴리스 좌우', 'extension': '익스텐션'})
    
    grouped_df = grouped_df.reset_index(drop=True)

    return grouped_df


