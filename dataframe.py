import streamlit as st
import pandas as pd
import numpy as np
import pymysql

def dataframe(level, player_id, password):

    db = pymysql.connect(host='14.49.30.59', port = 33067, user = 'ktwiz', passwd = password, db = 'ktwiz', charset='utf8', autocommit=True)

    db.ping ()
  
    cursor = db.cursor()
    sql = """SELECT

    -- game id
    gameid

    -- pitch_type
    , PITKIND AS pitch_type

    -- game date
    , `DATE`

    -- release_speed
    , ROUND( Relspeed*0.621371,1) as release_speed

    -- release_pos_x
    , ROUND(RelSide*3.28084,2) AS release_pos_x

    -- release_pos_z
    , ROUND(RelHeight*3.28084,2) AS release_pos_z

    -- pitname
    , pitname

    -- batname
    , batname

    -- batter
    , batterid  AS batter

    -- pitcher
    , pitcherid as pitcher

    -- events
    , case when playresult = 'Out' then 'field_out'
        when playresult = 'FieldersChoice' then 'fielders_choice_out'
        when playresult = 'Error' then 'field_error'
        when playresult = 'Single' then 'single'
        when playresult = 'Double' then 'double'
        when playresult = 'Triple' then 'triple'
        when playresult = 'HomeRun' then 'home_run'
        when playresult = 'Sacrifice' and distance >= 30 then 'sac_fly'
        when playresult = 'Sacrifice' and distance < 30 then 'sac_bunt'
        when playresult = 'Undefined' and pitchcall = 'HitByPitch' then 'hit_by_pitch'
        when playresult = 'Undefined' and korbb = 'Strikeout' then 'strikeout'
        when playresult = 'Undefined' and korbb = 'Walk' then 'walk' else NULL END as events

    -- description
    , case when pitchCall in('FoulBall', 'FoulballFieldable', 'FoulballNotFieldable') then 'foul'
        when pitchCall in ('BallCalled', 'BallinDirt', 'BallAutomatic') then 'ball'
        when pitchCall in ('StrikeCalled', 'AutomaticStrike', 'StrikeAutomatic') then 'called_strike'
        when pitchCall = 'StrikeSwinging' then 'swinging_strike'
        when pitchCall = 'InPlay' and playresult in ('Double','Single','HomeRun','Error','Triple','FieldersChoice')  and  runsscored = 0 then 'hit_into_play_no_out'
        when pitchCall = 'InPlay' and runsscored >= 1 then 'hit_into_play_score'
        when pitchCall = 'InPlay' and playresult in ('Out','Sacrifice') and runsscored = 0 then 'hit_into_play'
        when pitchCall = 'HitByPitch' or playresult = 'HitByPitch'  then 'hit_by_pitch'
        when pitchCall = 'BallIntentional' then 'pitchout'
        else null END AS description

    -- zone
    , '' AS 'zone'

    -- des
    , 'des'

    -- stand
    , CASE WHEN BATTERSIDE = 'RIGHT' THEN 'R' WHEN BATTERSIDE = 'LEFT' THEN 'L' ELSE NULL END AS stand

    -- p_throws
    , CASE WHEN PITCHERTHROWS = 'RIGHT' THEN 'R' WHEN PITCHERTHROWS = 'LEFT' THEN 'L' ELSE NULL END  AS p_throws

    -- pitcherteam
    , pitcherteam

    -- batterteam
    , batterteam

    -- hometeam, awayteam
    , HomeTeam, AwayTeam

    -- type
    , CASE WHEN pitchCall IN ('BallinDirt','BallCalled','HitByPitch','BallIntentional','BallAutomatic') THEN 'B'
        WHEN PITCHCALL IN ('StrikeCalled','FoulBall','StrikeSwinging','StrikeAutomatic','FoulBallNotFieldable','FoulBallFieldable') THEN 'S' 
        WHEN PITCHCALL IN ('InPlay') THEN 'X' ELSE NULL END AS 'type'

    -- bb_type
    -- , CASE WHEN pitchcall='inplay' AND exitspeed >= 1 and angle < 10 then 'Groundball'
    -- 	WHEN pitchcall='inplay' AND exitspeed >= 1 and angle >= 25 and angle < 50 then 'Flyball'
    -- 	WHEN pitchcall='inplay' AND exitspeed >= 1 and angle >= 10 and angle < 25 then 'LineDrive'
    -- 	WHEN pitchcall='inplay' AND exitspeed >= 1 and angle >= 50 then 'Popup' ELSE NULL END AS bb_type          -- bb_type 계산용
    , case when pitchcall  = 'inplay' and TaggedHitType = 'GroundBall' then 'ground_ball' 
        when pitchcall  = 'inplay' and TaggedHitType = 'LineDrive' then 'line_drive'
        when pitchcall  = 'inplay' and TaggedHitType = 'FlyBall' then 'fly_ball'
        when pitchcall  = 'inplay' and TaggedHitType = 'Popup' then 'popup'
        when pitchcall  = 'inplay' and TaggedHitType = 'Bunt' then 'bunt'
        else null end as bb_type

    -- count
    , balls , strikes 

    -- pfx_x, pfx_z
    , HorzBreak * 0.032808 AS pfx_x , InducedVertBreak *0.032808 as pfx_z

    -- plate_x, plate_z
    , PlateLocSide as plate_x	, PlateLocHeight as plate_z

    -- outs
    ,  Outs AS outs_when_up

    -- inning
    , inning

    -- topbot
    , Top_Bottom as inning_topbot

    -- hit_distance_sc
    , round(DISTANCE * 3.28084,0) AS hit_distance_sc

    -- launch speed
    , round(EXITSPEED * 0.621371 ,1) as launch_speed

    -- launch angle
    , round(ANGLE,0) AS launch_angle

    -- release_extension
    , round(SpinRate,0) as release_spin_rate	, round(SpinAxis,1) as release_spin_axis ,  round(Extension * 3.28084,2) as release_extension

    -- launch speed angle
    , case 
        when (EXITSPEED/ 1.609344 * 1.5 - angle) >= 117
        and (EXITSPEED/ 1.609344 + angle) >= 124
        and EXITSPEED/ 1.609344 >= 98
        and angle between 4 and 50
        and pitchcall = 'InPlay'
        then 6 -- 'Barrel'

        when (EXITSPEED/ 1.609344 * 1.5 - angle) >= 111
        and (EXITSPEED/ 1.609344 + angle) >= 119
        and EXITSPEED/ 1.609344 >= 95
        and angle between 0 and 52
        and pitchcall = 'InPlay'
        then 5 -- 'Solid-Contact'

        when EXITSPEED/ 1.609344 <= 59
        and pitchcall = 'InPlay'
        then 1 -- 'Poorly-Weak'

        when (EXITSPEED/ 1.609344 * 2 - angle) >= 87
        and angle <= 41
        and (EXITSPEED/ 1.609344 * 2 + angle) <= 175
        and (EXITSPEED/ 1.609344 + angle * 1.3) >= 89
        and EXITSPEED/ 1.609344 between 59 and 72
        and pitchcall = 'InPlay'
        then 4 -- 'Flare-or-Burner'

        when (EXITSPEED/ 1.609344 + angle * 1.3) <= 112
        and (EXITSPEED/ 1.609344 + angle * 1.55) >= 92
        and EXITSPEED/ 1.609344 between 72 and 86
        and pitchcall = 'InPlay'
        then 4 -- 'Flare-or-Burner'

        when angle <= 20
        and (EXITSPEED/ 1.609344 + angle * 2.4) >= 98
        and EXITSPEED/ 1.609344 between 86 and 95
        and pitchcall = 'InPlay'
        then 4 -- 'Flare-or-Burner'

        when (EXITSPEED/ 1.609344 - angle) >= 76
        and (EXITSPEED/ 1.609344 + angle * 2.4) >= 98
        and EXITSPEED/ 1.609344 >= 95
        and angle <= 30
        and pitchcall = 'InPlay'
        then 4 -- 'Flare-or-Burner'

        when (EXITSPEED/ 1.609344 + angle * 2) >= 116
        and pitchcall = 'InPlay'
        then 3 -- 'Poorly-Under'

        when (EXITSPEED/ 1.609344 + angle * 2) <= 116
        and pitchcall = 'InPlay'
        then 2 -- 'Poorly-Topped'

    else NULL -- 'Unclassified'
    end AS launch_speed_angle

    -- pitch_number
    , pitchofpa AS pitch_number

    -- pa of inning
    , paofinning

    -- pitch name
    , CASE WHEN PITKIND = 'FF' THEN '4-Seam Fastball'
        WHEN PITKIND = 'CH' THEN 'Changeup'
        WHEN PITKIND = 'SL' THEN 'Slider'
        WHEN PITKIND = 'CU' THEN 'Curveball'
        WHEN PITKIND = 'ST' THEN 'Sweeper'
        WHEN PITKIND = 'FS' THEN 'Split-Finger'
        WHEN PITKIND IN ('FT','SI') THEN '2-Seam Fastball'
        WHEN PITKIND = 'FC' THEN 'Cutter' ELSE PITKIND END AS pitch_name
    -- , PlateLocSide, PlateLocHeight

    , home_score_cn
    , away_score_cn
    , LEVEL
    , vertrelangle
    , case when bearing >= 0 then 'R' WHEN BEARING < 0 THEN 'L' ELSE NULL END as direction
    , round(ContactPositionX,2) , round(ContactPositionY,2) , round(ContactPositionZ,2)

    , case when pitchcall = 'inplay' and bearing >= 0 and bearing <= 45 then convert(round(distance *cos(radians(45-bearing)),0),int)
    when pitchcall = 'inplay' and bearing < 0 and bearing >= -45 then convert(round(distance *cos(radians(45 + abs(bearing))),0),int) else '' end as groundxside
    , case when pitchcall = 'inplay' and bearing >= 0 and bearing <= 45 then convert(round(distance *sin(radians(45-bearing)),0),int)
    when pitchcall = 'inplay' and bearing < 0 and bearing >= -45 then convert(round(distance *sin(radians(45 + abs(bearing))),0),int) else '' end as groundyside

    -- year
    , SEASON AS game_year

    -- hit spin rate
    , hitspinrate

    -- catcher
    , catcher as catcher

    -- trace
    , px0, x5, x10, x15, x20, x25, x30, x35, x40, x45, x50
    , pz0, z5, z10, z15, z20, z25, z30, z35, z40, z45, z50


    -- pitkind
        FROM 
            
            (
            SELECT a.*, substring(GameID ,1,4) as SEASON
            , CASE WHEN pit_kind_cd = '31' THEN 'FF'
            WHEN pit_kind_cd = '32' THEN 'CU'
            WHEN pit_kind_cd = '33' THEN 'SL'
            WHEN pit_kind_cd = '34' THEN 'CH'
            WHEN pit_kind_cd = '35' THEN 'FS'
            WHEN pit_kind_cd = '36' THEN 'SI'
            WHEN pit_kind_cd = '37' THEN 'FT'
            WHEN pit_kind_cd = '38' THEN 'FC'
            WHEN pit_kind_cd = '131' THEN 'ST'
            WHEN PIT_KIND_CD IS NULL and (AUTOPITCHTYPE = 'Fastball' OR AUTOPITCHTYPE = 'Four-Seam')  then 'FF'
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Sinker' then 'SI' 
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Curveball' then 'CU' 
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Slider' then 'SL'
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Changeup' then 'CH'
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Splitter' then 'FS'
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Cutter' then 'FC'
            WHEN PIT_KIND_CD IS NULL and AUTOPITCHTYPE = 'Sweeper' then 'ST'
            ELSE 'OT' END  AS PITKIND
            
            , PITCHER as pitname, BATTER as batname 
        
            , POS1_P_ID, POS2_P_ID, POS3_P_ID, POS4_P_ID, POS5_P_ID, POS6_P_ID, POS7_P_ID, POS8_P_ID, POS9_P_ID
            , home_score_cn , away_score_cn
            , c.x0 as px0, x5, x10, x15, x20, x25, x30, x35, x40, x45, x50
            , c.z0 as pz0, z5, z10, z15, z20, z25, z30, z35, z40, z45, z50

            FROM 
                pda_trackman a
            -- JOIN
                Left outer join 
                pda_analyzer b
                ON a.game_seq = b.game_seq AND a.pit_seq = b.pit_seq
                Left outer join 
                pda_calculate c
                ON a.game_seq = c.game_seq AND a.PitchNo = c.pitch_no
                
            ) ZZ
        
        
    WHERE 

    -- game year
    -- gameid Like '2020%'
    gameid >= '2023'

    AND level IN ({0})

    AND pitcherid = {1}

    order by gameid, pitchno  """


    cursor.execute(sql.format(level, player_id))
    raw = cursor.fetchall()

    df=pd.DataFrame([[item.decode('latin-1') if isinstance(item, bytes) else item for item in row] for row in raw],
                      columns = ['game_id','pitch_type', 'game_date', 'release_speed', 'release_pos_x', 'release_pos_z',  'pitname', 'batname', 'batter', 'pitcher', 'events', 'description', 'zone', 'des', 'stand', 'p_throw', 'pitcherteam','batterteam', 'hometeam' , 'awayteam',
                                'type', 'bb_type', 'balls', 'strikes', 'pfx_x', 'pfx_z', 'plate_x', 'plate_z', 'out_when_up', 'inning', 'inning_topbot', 'hit_distance_sc',
                                'launch_speed','launch_angle','release_spin_rate','release_spin_axis', 'release_extension',
                                'launch_speed_angle','pitch_number','PAofinning','pitch_name','home_score','away_score','level','verrelangle','launch_direction', 'contactX' , 'contactY' , 'contactZ', 'groundX','groundY','game_year','hit_spin_rate', 'catcher',
                                'x0', 'x5', 'x10', 'x15', 'x20', 'x25', 'x30', 'x35', 'x40', 'x45', 'x50',
                                'z0', 'z5', 'z10', 'z15', 'z20', 'z25', 'z30', 'z35', 'z40', 'z45', 'z50'])

    # df.to_sql(name='dataframe', con=db, ttl=360)
  
    cursor = db.cursor()
    height_sql = """
    select * from player_info  
    where TM_ID = {0}
    """

    cursor.execute(height_sql.format(player_id))
    height_raw = cursor.fetchall()

    height_df=pd.DataFrame(height_raw, columns = ['game_year', 'team', 'team_tm_major', 'team_tm_minor','KBO_ID','batter','NAME','POS','BackNum','engName','Birthday','Height','Weight','PitcherThrows','BatterSide'])

    df['game_year'] = df['game_year'].astype(int)
    height_df['game_year'] = height_df['game_year'].astype(int)

    df = pd.merge(df, height_df[['game_year', 'batter', 'Height', 'Weight']], on=['game_year', 'batter'], how='left')

    db.commit()  
    db.close()

    if len(df) > 0:

        df['plate_x'] = df['plate_x'] * -1.0
        df['pfx_x'] = df['pfx_x'] * -1.0

        df['hit_distance'] = df['hit_distance_sc']*0.3048

        conv_fac = 0.3048
        df['rel_height'] = df['release_pos_z']*conv_fac
        df['rel_side'] = df['release_pos_x']*conv_fac
        df['hor_break'] = df['pfx_x']*conv_fac
        df['ver_break'] = df['pfx_z']*conv_fac

        p_type = df[['pitcher','rel_height']]
        rel_height = p_type.groupby(['pitcher'], as_index=False).mean()
        rel_height['type'] = rel_height['rel_height'].apply(lambda x: 'S' if x <= 1.5 else 'R')
        side_arm = rel_height[rel_height['type'] == 'S']

        y = side_arm['pitcher'].unique()

        df['side_arm'] = df['pitcher'].apply(lambda x: 'S' if x in y else 'Reg')
        df['p_throws'] = df['pitcher'].apply(lambda x: 'S' if x in y else list(set(df.loc[df['pitcher'] == x, 'p_throw'].unique()))[0])

        df['Height'] = pd.to_numeric(df['Height'], errors='coerce')

        # 신장 가져오기
        df['high'] = np.where(df['Height'].isnull(), 1.049 , (df['Height'] * 0.5575 + 3.5) / 100)
        df['low']  = np.where(df['Height'].isnull(), 0.463 , (df['Height'] * 0.2704 - 3.5) / 100)
        # 신장이 없는 경우는 일단 183cm 기준으로 가져오는 것으로 함
        df['1/3'] = (df['low'] + ((df['high'] - df['low']) / 3))
        df['2/3'] = (df['high'] - ((df['high'] - df['low']) / 3))

        df['zonehigh'] = df['high'] + 0.11
        df['corehigh'] = df['high'] - 0.11
        df['corelow'] = df['low'] + 0.11
        df['zonelow'] = df['low'] - 0.11

        condition9 = [
            (df['plate_x'] > -0.271) & (df['plate_x'] < 0.271) & (df['plate_z'] > df['low'] ) & (df['plate_z'] < df['high']),
            (df['plate_x'] > -0.381) & (df['plate_x'] < 0.381) & (df['plate_z'] > df['zonelow']) & (df['plate_z'] < df['zonehigh'])
            
        ]

        choicelist9 = ['IN', 'OUT']

        df['INOUT'] = np.select(condition9, choicelist9, default= 'Not Specified')

        condition0 = [
                    (df['plate_x'] > -0.271) & (df['plate_x'] < -0.0903) & (df['plate_z'] > df['2/3']) & (df['plate_z'] < df['high']),
                    (df['plate_x'] > -0.0903) & (df['plate_x'] < 0.0903) & (df['plate_z'] > df['2/3']) & (df['plate_z'] < df['high']),
                    (df['plate_x'] > 0.0903) & (df['plate_x'] < 0.271) & (df['plate_z'] > df['2/3']) & (df['plate_z'] < df['high']),
                    
                    (df['plate_x'] > -0.271) & (df['plate_x'] < -0.0903) & (df['plate_z'] > df['1/3']) & (df['plate_z'] < df['2/3']),
                    (df['plate_x'] > -0.0903) & (df['plate_x'] < 0.0903) & (df['plate_z'] > df['1/3']) & (df['plate_z'] < df['2/3']),
                    (df['plate_x'] > 0.0903) & (df['plate_x'] < 0.271) & (df['plate_z'] > df['1/3']) & (df['plate_z'] < df['2/3']),
                    
                    (df['plate_x'] > -0.271) & (df['plate_x'] < -0.0903) & (df['plate_z'] > df['low']) & (df['plate_z'] < df['1/3']),
                    (df['plate_x'] > -0.0903) & (df['plate_x'] < 0.0903) & (df['plate_z'] > df['low']) & (df['plate_z'] < df['1/3']),
                    (df['plate_x'] > 0.0903) & (df['plate_x'] < 0.271) & (df['plate_z'] > df['low']) & (df['plate_z'] < df['1/3']),
                    
                    (df['INOUT'] == 'OUT') & (df['plate_x'] < 0) & (df['plate_z'] > 0.75) ,
                    (df['INOUT'] == 'OUT') & (df['plate_x'] > 0) & (df['plate_z'] > 0.75) ,
                    (df['INOUT'] == 'OUT') & (df['plate_x'] < 0) & (df['plate_z'] < 0.75) ,
                    (df['INOUT'] == 'OUT') & (df['plate_x'] > 0) & (df['plate_z'] < 0.75) ,
                    
                    
        ]

        choicelist0 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]

        df['zone'] = np.select(condition0, choicelist0, default= 99)

        pa = ['double','double_play','field_error','field_out','fielders_choice_out','force_out','grounded_into_double_play','hit_by_pitch','home_run','sac_bunt','sac_fly','sac_fly_double_play','single','strikeout','strikeout_double_play','triple','walk']
        ab = ['double','double_play','field_error','field_out','fielders_choice_out','force_out','grounded_into_double_play','home_run','single','strikeout','strikeout_double_play','triple']
        hit = ['double','home_run','single','triple']
        swing = ['foul','foul_tip','hit_into_play','hit_into_play_no_out','hit_into_play_score','swinging_strike','swing_strike_blocked']
        con = ['foul','foul_tip','hit_into_play','hit_into_play_no_out','hit_into_play_score']
        whiff = ['swinging_strike','swing_strike_blocked']
        foul = ['foul','foul_tip']

        df['pa'] = df['events'].apply(lambda x: 1 if x in pa else 0)
        df['ab'] = df['events'].apply(lambda x: 1 if x in ab else 0)
        df['hit'] = df['events'].apply(lambda x: 1 if x in hit else 0)
        df['swing'] = df['description'].apply(lambda x: 1 if x in swing else 0)
        df['con'] = df['description'].apply(lambda x: 1 if x in con else 0)
        df['whiff'] = df['description'].apply(lambda x: 1 if x in whiff else 0)
        df['foul'] = df['description'].apply(lambda x: 1 if x in foul else 0)

        df['z_in'] = df['zone'].apply(lambda x: 1 if x < 10 else None)
        df['z_out'] = df['zone'].apply(lambda x: 1 if x > 10 else None)

        df['balls'] = df['balls'].apply(str)
        df['strikes'] = df['strikes'].apply(str)
        df['count'] = df['balls'].str.cat(df['strikes'], sep='-')

        speed_fac = 1.609344
        distance_fac = 0.3048

        df['rel_speed(km)'] = df['release_speed']*speed_fac
        df['exit_speed(km)'] = df['launch_speed']*speed_fac
        df['rel_height'] = df['release_pos_z']*distance_fac
        df['rel_side'] = df['release_pos_x']*distance_fac
        df['extension'] = df['release_extension']*distance_fac
        # df['hit_distance'] = df['hit_distance_sc']*distance_fac

        p_type = df[['pitcher','rel_height']]
        rel_height = p_type.groupby(['pitcher'], as_index=False).mean()

        rel_height['type'] = rel_height['rel_height'].apply(lambda x: 'S' if x <= 1.5 else 'R')
        side_arm = rel_height[rel_height['type'] == 'S']
        y = side_arm['pitcher'].unique()

        df['p_type'] = df['pitcher'].apply(lambda x: 'S' if x in y else 'R')

        def pkind(x):

            if x == '4-Seam Fastball':
                return 'Fastball'
            elif x == '2-Seam Fastball':
                return 'Fastball'
            elif x == 'Cutter':
                return 'Fastball'
            elif x == 'Slider':
                return 'Breaking'
            elif x == 'Curveball':
                return 'Breaking'
            elif x == 'Sweeper':
                return 'Breaking'
            elif x == 'Changeup':
                return 'Off_Speed'
            elif x == 'Split-Finger':
                return 'Off_Speed'
            else:
                return 'OT'


        df['p_kind'] = df['pitch_name'].apply(lambda x: pkind(x))

        def count(x):

            if x == '0-0':
                return 'First_Pitch'
            elif x == '3-2':
                return 'Else'
            elif x == '0-1':
                return 'Else'
            elif x == '0-2':
                return 'After_2S'
            elif x == '1-1':
                return 'Else'
            elif x == '1-2':
                return 'After_2S'
            elif x == '2-2':
                return 'After_2S'
            elif x == '1-0':
                return 'Hitting'
            elif x == '2-0':
                return 'Hitting'
            elif x == '2-1':
                return 'Hitting'
            elif x == '3-0':
                return 'Else'
            elif x == '3-1':
                return 'Else'

        df['count_value'] = df['count'].apply(lambda x: count(x))

        df['after_2s'] = df['count_value'].apply(lambda x: 1 if x == 'After_2S' else None)
        df['hitting'] = df['count_value'].apply(lambda x: 1 if x == 'Hitting' else None)
        df['else'] = df['count_value'].apply(lambda x: 1 if x == 'Else' else None)

        df['ld'] = df['bb_type'].apply(lambda x: 1 if x == 'Line_Drive' else None)
        df['fb'] = df['bb_type'].apply(lambda x: 1 if x == 'Fly_Ball' else None)
        df['gb'] = df['bb_type'].apply(lambda x: 1 if x == 'Ground_Ball' else None)
        df['pu'] = df['bb_type'].apply(lambda x: 1 if x == 'Popup' else None)

        df['single'] = df['events'].apply(lambda x: 1 if x == 'single' else None)
        df['double'] = df['events'].apply(lambda x: 1 if x == 'double' else None)
        df['triple'] = df['events'].apply(lambda x: 1 if x == 'triple' else None)
        df['home_run'] = df['events'].apply(lambda x: 1 if x == 'home_run' else None)
        df['walk'] = df['events'].apply(lambda x: 1 if x == 'walk' else None)
        df['strikeout'] = df['events'].apply(lambda x: 1 if x == 'strikeout' else None)
        df['hit_by_pitch'] = df['events'].apply(lambda x: 1 if x == 'hit_by_pitch' else None)
        df['sac_fly'] = df['events'].apply(lambda x: 1 if x == 'sac_fly' else None)
        df['sac_bunt'] = df['events'].apply(lambda x: 1 if x == 'sac_bunt' else None)
        df['field_out'] = df['events'].apply(lambda x: 1 if x == 'field_out' else None)

        df['inplay'] = df['type'].apply(lambda x: 1 if x == 'X' else None)

        df['weak'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 1 else None)
        df['topped'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 2 else None)
        df['under'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 3 else None)
        df['flare'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 4 else None)
        df['solid_contact'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 5 else None)
        df['barrel'] = df['launch_speed_angle'].apply(lambda x: 1 if x == 6 else None)
        df['plus_lsa4'] = df['launch_speed_angle'].apply(lambda x: 1 if x >=4 else None)
        df['cs'] = df['description'].apply(lambda x: 1 if x == 'called_strike' else None)

        # github용
        # df['game_date'] = pd.to_datetime(df['game_date'], format='mixed', dayfirst=True)

        # vscode용
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')

        condition1 = [
                    (df['zone'] == 1) & (df['swing'] != 1),
                    (df['zone'] == 3) & (df['swing'] != 1),
                    (df['zone'] == 4) & (df['swing'] != 1),
                    (df['zone'] == 6) & (df['swing'] != 1),
                    (df['zone'] == 7) & (df['swing'] != 1),
                    (df['zone'] == 9) & (df['swing'] != 1),
        ]

        choicelist1 = ['Left_take','Right_take', 'Left_take', 'Right_take', 'Left_take', 'R_Right_takeake']

        df['l_r'] = np.select(condition1, choicelist1, default='Not Specified')

        condition2 = [
                    (df['zone'] == 1) & (df['swing'] != 1),
                    (df['zone'] == 2) & (df['swing'] != 1),
                    (df['zone'] == 3) & (df['swing'] != 1),
                    (df['zone'] == 7) & (df['swing'] != 1),
                    (df['zone'] == 8) & (df['swing'] != 1),
                    (df['zone'] == 9) & (df['swing'] != 1),
        ]

        choicelist2 = ['High_take','High_take', 'High_take', 'Low_take', 'Low_take', 'Low_take']

        df['h_l'] = np.select(condition2, choicelist2, default='Not Specified')

        df['z_left'] = df['zone'].apply(lambda x: 1 if x == 1 or x == 4 or x== 7 else 0)
        df['z_right'] = df['zone'].apply(lambda x: 1 if x == 3 or x == 6 or x== 9 else 0)
        df['z_high'] = df['zone'].apply(lambda x: 1 if x == 1 or x == 2 or x== 3 else 0)
        df['z_low'] = df['zone'].apply(lambda x: 1 if x == 7 or x == 8 or x== 9 else 0)

        condition3 = [
                    (df['plate_x'] > -0.381) & (df['plate_x'] < -0.161) & (df['plate_z'] > df['corehigh']) & (df['plate_z'] < df['zonehigh']),
                    (df['plate_x'] > -0.161) & (df['plate_x'] < 0.161) & (df['plate_z'] > df['corehigh']) & (df['plate_z'] < df['zonehigh']),
                    (df['plate_x'] > 0.161) & (df['plate_x'] < 0.381) & (df['plate_z'] > df['corehigh']) & (df['plate_z'] < df['zonehigh']),
                    (df['plate_x'] > -0.381) & (df['plate_x'] < -0.161) & (df['plate_z'] > df['corelow']) & (df['plate_z'] < df['corehigh']),
                    (df['plate_x'] > -0.161) & (df['plate_x'] < 0.161) & (df['plate_z'] > df['corelow']) & (df['plate_z'] < df['corehigh']),
                    (df['plate_x'] > 0.161) & (df['plate_x'] < 0.381) & (df['plate_z'] > df['corelow']) & (df['plate_z'] < df['corehigh']),
                    (df['plate_x'] > -0.381) & (df['plate_x'] < -0.161) & (df['plate_z'] > df['zonelow']) & (df['plate_z'] < df['corelow']),
                    (df['plate_x'] > -0.161) & (df['plate_x'] < 0.161) & (df['plate_z'] > df['zonelow']) & (df['plate_z'] < df['corelow']),
                    (df['plate_x'] > 0.161) & (df['plate_x'] < 0.381) & (df['plate_z'] > df['zonelow']) & (df['plate_z'] < df['corelow']),
        ]

        choicelist3 = ['nz1','nz2', 'nz3', 'nz4', 'core', 'nz6','nz7','nz8','nz9']

        df['new_zone'] = np.select(condition3, choicelist3, default='Not Specified')

        df['DH'] = df['game_id'].str[-1]

        ndf = df[['game_year', 'game_date', 'inning', 'hometeam','home_score', 'awayteam','away_score',
         'pitch_number','balls', 'strikes', 'zone', 'new_zone','stand', 'p_throw', 'p_throws', 'p_type', 'type', 'bb_type','events', 'description', 'hor_break','ver_break','plate_x','plate_z',
         'pitcherteam', 'pitname', 'pitcher','catcher','batterteam', 'batname', 'batter',
         'rel_speed(km)','release_spin_rate', 'release_spin_axis','rel_height', 'rel_side', 'extension','pitch_name', 'p_kind',
         'exit_speed(km)','launch_angle','launch_direction','hit_distance','hit_spin_rate','launch_speed_angle', 'contactX', 'contactY', 'contactZ', 'groundX', 'groundY', 'l_r','h_l',
         'pa', 'ab', 'hit', 'swing', 'con', 'whiff','foul','z_in','z_out','count', 'count_value', 'z_left','z_right','z_high','z_low',
          'ld','fb','gb','pu','single','double','triple','home_run','walk','strikeout','hit_by_pitch','sac_fly','sac_bunt','field_out','inplay',
          'weak','topped','under','flare','solid_contact','barrel','plus_lsa4','level','DH','cs', 'Height', 'high', 'low', '2/3', '1/3', 'zonehigh', 'corehigh', 'corelow', 'zonelow',
          'x0', 'x5', 'x10', 'x15', 'x20', 'x25', 'x30', 'x35', 'x40', 'x45', 'x50',
          'z0', 'z5', 'z10', 'z15', 'z20', 'z25', 'z30', 'z35', 'z40', 'z45', 'z50'
        ]]

        def ntype(x):

            if x == 'called_strike':
                return 'strike'
            elif x == 'ball':
                return 'ball'   
            elif x == 'hit_into_play':
                return 'inplay'  
            elif x == 'hit_into_play_no_out':
                return 'inplay'   
            elif x == 'hit_into_play_score':
                return 'inplay'   
            elif x == 'swinging_strike':
                return 'whiff'   
            elif x == 'swing_strike_blocked':
                return 'whiff'   
            elif x == 'foul':
                return 'foul'   
            elif x == 'hit_by_pitch':
                return 'hit_by_pitch'   

        ndf['ntype'] = ndf['description'].apply(lambda x: ntype(x))

        z_df = ndf[ndf['zone'] < 10]
        z_df['z_swing'] = z_df['swing'].apply(lambda x: 1 if x == 1 else 0)
        z_df['z_con'] = z_df['con'].apply(lambda x: 1 if x == 1 else 0)
        z_df['z_inplay'] = z_df['inplay'].apply(lambda x: 1 if x == 1 else 0)

        z_swing = z_df[['z_swing']]
        z_con = z_df[['z_con']]
        z_inplay = z_df[['z_inplay']]

        o_df = ndf[ndf['zone'] > 10]
        o_df['o_swing'] = o_df['swing'].apply(lambda x: 1 if x == 1 else 0)
        o_df['o_con'] = o_df['con'].apply(lambda x: 1 if x == 1 else 0)
        o_df['o_inplay'] = o_df['inplay'].apply(lambda x: 1 if x == 1 else 0)

        o_swing = o_df[['o_swing']]
        o_con = o_df[['o_con']]
        o_inplay = o_df[['o_inplay']]

        f_pitch = ndf[ndf['count'] == '0-0']
        f_pitch['f_swing'] = f_pitch['swing'].apply(lambda x: 1 if x == 1 else 0)
        f_swing = f_pitch[['f_swing']]

        inplay_df = ndf[ndf['type'] == 'X']
        inplay_df = inplay_df[['exit_speed(km)','launch_angle']]
        inplay_df.columns = ['exit_velocity','launch_angleX']

        whiff = ndf[ndf['whiff'] == 1]
        whiff['z_str_swing'] = whiff['zone'].apply(lambda x: 1 if x < 10 else 0)
        z_ztr_swing = whiff[['z_str_swing']]

        ndf = ndf.join(z_swing, how='outer')
        ndf = ndf.join(o_swing, how='outer')
        ndf = ndf.join(z_con, how='outer')
        ndf = ndf.join(o_con, how='outer')
        ndf = ndf.join(f_swing, how='outer')
        ndf = ndf.join(inplay_df, how='outer')
        ndf = ndf.join(z_ztr_swing, how='outer')
        ndf = ndf.join(z_inplay, how='outer')
        ndf = ndf.join(o_inplay, how='outer')

        ndf['f_pitch'] = ndf['count'].apply(lambda x: 1 if x == '0-0' else 0)

        ndf['Left_take'] = ndf['l_r'].apply(lambda x: 1 if x == 'Left_take' else 0)
        ndf['Right_take'] = ndf['l_r'].apply(lambda x: 1 if x == 'Right_take' else 0)
        ndf['High_take'] = ndf['h_l'].apply(lambda x: 1 if x == 'High_take' else 0)
        ndf['Low_take'] = ndf['h_l'].apply(lambda x: 1 if x == 'Low_take' else 0)

        ndf['looking'] = ndf['description'].apply(lambda x: 1 if x == "ball" or x == "called_strike" else 0)

        ndf['so'] = ndf['zone'].apply(lambda x: 1 if x == 1 else 0)

        ot = ndf[ndf['p_kind'] == 'OT'].index
        ndf = ndf.drop(ot)

        ndf['z_in'].fillna(0, inplace=True)

        ndf['month'] = ndf['game_date'].dt.month

        # 리그 레벨에 따라 다른 시즌 날짜 적용
        if level == 'KBO':
            
            start18 = '2018-04-01'
            end18 = '2018-10-18'
            start19 = '2019-03-23'
            end19 = '2019-10-01'
            start20 = '2020-05-05'
            end20 = '2020-10-31'
            start21 = '2021-04-03'
            end21 = '2021-10-30'
            start22 = '2022-04-02'
            end22 = '2022-10-11'
            start23 = '2023-04-01'
            end23 = '2023-10-30'
            start24 = '2024-03-23'
            end24 = '2024-10-01'        
            start25 = '2025-03-22'
            end25 = '2025-10-01'    
        
            season18 = ndf[(ndf['game_date'] >= start18) & (ndf['game_date'] <= end18)]
            season19 = ndf[(ndf['game_date'] >= start19) & (ndf['game_date'] <= end19)]
            season20 = ndf[(ndf['game_date'] >= start20) & (ndf['game_date'] <= end20)]
            season21 = ndf[(ndf['game_date'] >= start21) & (ndf['game_date'] <= end21)]
            season22 = ndf[(ndf['game_date'] >= start22) & (ndf['game_date'] <= end22)]
            season23 = ndf[(ndf['game_date'] >= start23) & (ndf['game_date'] <= end23)]
            season24 = ndf[(ndf['game_date'] >= start24) & (ndf['game_date'] <= end24)]
            season25 = ndf[(ndf['game_date'] >= start25) & (ndf['game_date'] <= end25)]
        
            player_df = pd.concat([season18, season19, season20, season21, season22, season23, season24, season25], ignore_index=True)
        
        elif level == 'KBO_Minor':
            # KBO_Minor 리그의 시즌 날짜 설정
            start23 = '2023-04-04'
            end23 = '2023-09-24'
            start24 = '2024-03-26'
            end24 = '2024-10-05'
            start25 = '2025-03-14'
            end25 = '2025-10-01'
            
            # 각 시즌 데이터 필터링
            season23 = ndf[(ndf['game_date'] >= start23) & (ndf['game_date'] <= end23)]
            season24 = ndf[(ndf['game_date'] >= start24) & (ndf['game_date'] <= end24)]
            season25 = ndf[(ndf['game_date'] >= start25) & (ndf['game_date'] <= end25)]
            
            # 필터링된 데이터 합치기
            player_df = pd.concat([season23, season24, season25], ignore_index=True)
        else:
            # 다른 리그의 경우 기본적으로 원본 데이터 사용
            player_df = ndf
        
        # 공통 처리
        player_df = player_df.reset_index(drop=True)
        player_df['game_date'] = pd.to_datetime(player_df['game_date'])
        
    else:
        raise ValueError("데이터가 존재하지 않습니다.")
            
    return player_df
    



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
    # 기본값 설정
    merged_base_df['avg'] = 0.0
    merged_base_df['obp'] = 0.0
    merged_base_df['slg'] = 0.0
    merged_base_df['ops'] = 0.0
    
    # avg 계산 (안전한 나눗셈)
    mask_ab = merged_base_df['ab'] > 0
    if mask_ab.any():
        merged_base_df.loc[mask_ab, 'avg'] = merged_base_df.loc[mask_ab, 'hit'] / merged_base_df.loc[mask_ab, 'ab']
    
    # obp 계산 (안전한 나눗셈)
    obp_denominator = merged_base_df['ab'] + merged_base_df['hit_by_pitch'] + merged_base_df['walk'] + merged_base_df['sac_fly']
    mask_obp = obp_denominator > 0
    if mask_obp.any():
        obp_numerator = merged_base_df['hit'] + merged_base_df['hit_by_pitch'] + merged_base_df['walk']
        merged_base_df.loc[mask_obp, 'obp'] = obp_numerator[mask_obp] / obp_denominator[mask_obp]
    
    # slg 계산 (안전한 나눗셈)
    slg_numerator = ((merged_base_df['single'] * 1) + (merged_base_df['double'] * 2) + 
                     (merged_base_df['triple'] * 3) + (merged_base_df['home_run'] * 4))
    if mask_ab.any():
        merged_base_df.loc[mask_ab, 'slg'] = slg_numerator[mask_ab] / merged_base_df.loc[mask_ab, 'ab']
    
    # ops 계산
    merged_base_df['ops'] = merged_base_df['obp'] + merged_base_df['slg']
    
    # 스트라이크존 관련 통계 (안전한 나눗셈)
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
    
    # 스트라이크존 밖 관련 통계 (안전한 나눗셈)
    if mask_player.any():
        merged_base_df.loc[mask_player, 'o%'] = merged_base_df.loc[mask_player, 'z_out'] / merged_base_df.loc[mask_player, 'pitname']
    
    mask_z_out = merged_base_df['z_out'] > 0
    if mask_z_out.any():
        merged_base_df.loc[mask_z_out, 'o_swing%'] = merged_base_df.loc[mask_z_out, 'o_swing'] / merged_base_df.loc[mask_z_out, 'z_out']
    
    mask_o_swing = merged_base_df['o_swing'] > 0
    if mask_o_swing.any():
        merged_base_df.loc[mask_o_swing, 'o_con%'] = merged_base_df.loc[mask_o_swing, 'o_con'] / merged_base_df.loc[mask_o_swing, 'o_swing']
        merged_base_df.loc[mask_o_swing, 'o_inplay%'] = merged_base_df.loc[mask_o_swing, 'o_inplay'] / merged_base_df.loc[mask_o_swing, 'o_swing']
    
    # 기타 스윙 관련 통계 (안전한 나눗셈)
    mask_f_pitch = merged_base_df['f_pitch'] > 0
    if mask_f_pitch.any():
        merged_base_df.loc[mask_f_pitch, 'f_swing%'] = merged_base_df.loc[mask_f_pitch, 'f_swing'] / merged_base_df.loc[mask_f_pitch, 'f_pitch']
    
    if mask_player.any():
        merged_base_df.loc[mask_player, 'swing%'] = merged_base_df.loc[mask_player, 'swing'] / merged_base_df.loc[mask_player, 'pitname']
    
    mask_swing = merged_base_df['swing'] > 0
    if mask_swing.any():
        merged_base_df.loc[mask_swing, 'whiff%'] = merged_base_df.loc[mask_swing, 'whiff'] / merged_base_df.loc[mask_swing, 'swing']
        merged_base_df.loc[mask_swing, 'inplay_sw'] = merged_base_df.loc[mask_swing, 'inplay'] / merged_base_df.loc[mask_swing, 'swing']

    merged_base_df['total_contact'] = (merged_base_df['weak'] + 
                                      merged_base_df['topped'] + 
                                      merged_base_df['under'] + 
                                      merged_base_df['flare'] + 
                                      merged_base_df['solid_contact'] + 
                                      merged_base_df['barrel'])
    
    # 합계가 0보다 큰 경우에만 계산 수행
    mask_contact = merged_base_df['total_contact'] > 0
    
    if mask_contact.any():
        # 각 타구 타입별 비율 계산 (전체 타구 타입 합계로 나눔)
        merged_base_df.loc[mask_contact, 'weak'] = merged_base_df.loc[mask_contact, 'weak'] / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'topped'] = merged_base_df.loc[mask_contact, 'topped'] / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'under'] = merged_base_df.loc[mask_contact, 'under'] / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'flare'] = merged_base_df.loc[mask_contact, 'flare'] / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'solid_contact'] = merged_base_df.loc[mask_contact, 'solid_contact'] / merged_base_df.loc[mask_contact, 'total_contact']
        merged_base_df.loc[mask_contact, 'barrel'] = merged_base_df.loc[mask_contact, 'barrel'] / merged_base_df.loc[mask_contact, 'total_contact']
    

    merged_base_df['plus_lsa4'] = merged_base_df['flare'] + merged_base_df['solid_contact'] + merged_base_df['barrel']
    
    # 접근 방식 분류 추가
    kbo_z_swing = 0.654
    kbo_o_swing = 0.261
    
    # NaN 값을 처리하기 위한 조건
    # z_swing%와 o_swing% 값이 있는 행만 처리
    valid_rows = merged_base_df['z_swing%'].notna() & merged_base_df['o_swing%'].notna()
    
    # 기본값 설정
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

    # 출력할 컬럼 선택
    stats_output_df = merged_base_df[['game_date', 'pitname', 'pa', 'ab', 'hit', 'walk', 'strikeout','rel_speed(km)', 
                                     'inplay_pit', 'exit_velocity', 'launch_angleX',  
                                     'avg', 'obp', 'slg', 'ops', 'z%', 'z_swing%', 'z_con%', 'z_inplay%', 
                                     'o%', 'o_swing%', 'o_con%', 'o_inplay%', 'f_swing%', 'swing%', 'whiff%', 
                                     'inplay_sw', 'weak', 'topped', 'under', 'flare', 'solid_contact', 
                                     'barrel', 'approach', 'plus_lsa4']]


    # 퍼센트 표시 열 목록
    percent_columns = ['inplay_pit', 'z%', 'z_swing%', 'z_con%', 'z_inplay%', 'o%', 'o_swing%', 'o_con%', 
                      'o_inplay%', 'f_swing%', 'swing%', 'whiff%', 'inplay_sw',
                      'weak', 'topped', 'under', 'flare', 'solid_contact', 'barrel', 'plus_lsa4']
    
    # 퍼센트 열 중 타구 품질 지표를 제외한 열에 대해 값을 100배로 변환
    for col in percent_columns:
        stats_output_df[col] = stats_output_df[col] * 100
                
    # 반올림할 컬럼과 소수점 자릿수 정의
    round_dict = {
        'game_date':0, 'pitname':0,'pa': 0, 'ab': 0, 'hit': 0, 'walk': 0, 'strikeout': 0, 'rel_speed(km)': 1, 'inplay_pit': 1, 
        'exit_velocity': 1, 'launch_angleX': 1, 'hit_spin_rate': 0, 'avg': 3, 
        'obp': 3, 'slg': 3, 'ops': 3, 'z%': 1, 'z_swing%': 1, 'z_con%': 1, 
        'z_inplay%': 1, 'o%': 1, 'o_swing%': 1, 'o_con%': 1, 'o_inplay%': 1, 
        'f_swing%': 1, 'swing%': 1, 'whiff%': 1, 'inplay_sw': 1, 'inplay%': 1, 
        'weak': 1, 'topped': 1, 'under': 1, 'flare': 1, 'solid_contact': 1, 'barrel': 1,
        'plus_lsa4': 1
    }

    # 중복 제거
    round_dict_corrected = {k: v for i, (k, v) in enumerate(round_dict.items()) if k not in list(round_dict.keys())[:i]}

    # 존재하는 컬럼만 반올림
    existing_columns = {col: dec for col, dec in round_dict_corrected.items() if col in stats_output_df.columns}
    if existing_columns:
        # 숫자 컬럼만 반올림
        for col, dec in existing_columns.items():
            try:
                if pd.api.types.is_numeric_dtype(stats_output_df[col]):
                    stats_output_df[col] = stats_output_df[col].round(dec)
            except:
                pass  # 오류 발생 시 무시

    # 값 포맷팅 (NaN을 "-"로 변환)
    for column, decimals in round_dict_corrected.items():
        if column in stats_output_df.columns:
            try:
                # NaN 값 처리를 위한 함수
                def format_value(x):
                    if pd.isna(x):
                        return "-"  # NaN 값을 "-"로 표시
                    elif decimals == 0:
                        try:
                            return f"{int(x)}"  # 소수점 없는 정수
                        except:
                            return "-"  # 변환 실패 시 "-" 표시
                    else:
                        try:
                            # 퍼센트 컬럼에 % 기호 추가
                            if column in percent_columns:
                                return f"{float(x):.{decimals}f}%"  # % 기호 추가
                            else:
                                return f"{float(x):.{decimals}f}"  # 소수점 고정 표시
                        except:
                            return "-"  # 변환 실패 시 "-" 표시
                
                stats_output_df[column] = stats_output_df[column].apply(format_value)
            except Exception as e:
                print(f"열 '{column}' 처리 중 오류 발생: {e}")
                continue

    return stats_output_df
