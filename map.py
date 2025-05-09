import pandas as pd
import streamlit as st
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go

def season_movement_chart(dataframe):

    fig = px.scatter(dataframe, x="hor_break", y="ver_break", color="pitch_name",
                 category_orders = {"pitch_name" : ['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Curveball','Changeup','Split-Finger','Sweeper']},
                 color_discrete_map={
                "4-Seam Fastball": "red",
                "2-Seam Fastball": "pink",
                "Cutter": "purple",
                "Slider": "blue",
                "Changeup": "green",
                "Curveball": "orange",
                "Split-Finger": "brown",
                "Sweeper": "yellow"

                },
                 hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","game_date", "batname", "events","exit_velocity","description","launch_speed_angle","launch_angle"],
                 template = 'plotly_white')


    fig.update_yaxes(range=[-0.7, 0.7], mirror=True, 
                    showline=True, linewidth=1, linecolor='#dbdbdb', 
                    ticks='outside', tickwidth=1, tickcolor='#dbdbdb',
                    showgrid=True)

    fig.update_xaxes(range=[-0.7, 0.7], mirror=True, 
                    showline=True, linewidth=1, linecolor='#dbdbdb', 
                    ticks='outside', tickwidth=1, tickcolor='#dbdbdb',
                    showgrid=True)

    fig.update_traces(marker=dict(size=18))

    fig.update_layout(showlegend=False,
                    width = 600, height = 600,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=0.1, r=0.1, t=0.1, b=0.1),
                    shapes=[
                        # 전체 테두리 추가
                        dict(
                            type='rect',
                            xref='paper', yref='paper',
                            x0=0, y0=0, x1=1, y1=1,
                            line=dict(color= '#dbdbdb', width=2)
                        )
                    ]
                    )
    
    opacity = 0.8


    fig.add_vline(x=-80, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=-60, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=-40, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=-20, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=0,    line_width=2, line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=20, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=40, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=60,  line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_vline(x=80, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')

    fig.add_hline(y=-80, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=-60, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=-40, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=-20, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=0,    line_width=2, line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=20, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=40, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=60, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')
    fig.add_hline(y=80, line_width=0.7, line_dash='dash', line_color='rgba(108,122,137,0.8)')


    return fig

def season_pitchtrack_chart(dataframe):

    sdf = dataframe

    # 스트라이크존 설정
    #B
    zone = pd.DataFrame(dict(
        x = [-0.23, 0.23, 0.23, -0.23, -0.23],
        y = [0.45, 0.45, 1.05, 1.05, 0.45]
    ))

    # Y축 기준 설정
    tracey=[0, 1.524, 3.048, 4.572, 6.096, 7.62, 9.114, 10.668, 12.192, 13.716, 15.24]

    # 존 기준
    XL = -0.23
    XR = 0.23
    ZB = 0.45
    ZT = 1.05

    # ZONE XYZ 설정

    ZX = [XL, XL, XR, XR, XL]
    ZY = [0, 0, 0, 0, 0]    # 홈플레이트 끝 기준
    ZZ = [ZB, ZT, ZT, ZB, ZB]

    # 두께
    ticks = 20

    # 사이즈
    size = 5

    # 거리
    dis = 6

    # 구종별로 데이터프레임
    fourseam = sdf.loc[(sdf.pitch_name == "4-Seam Fastball" )]
    twoseam= sdf.loc[(sdf.pitch_name == "2-Seam Fastball" )]
    cutter = sdf.loc[(sdf.pitch_name == "Cutter" )]
    slider = sdf.loc[(sdf.pitch_name == "Slider" ) ]
    changeup = sdf.loc[(sdf.pitch_name == "Changeup" )]
    splitter = sdf.loc[(sdf.pitch_name == "Split-Finger" ) ]
    curve = sdf.loc[(sdf.pitch_name == "Curveball" ) ]
    sweeper = sdf.loc[(sdf.pitch_name == "Sweeper" ) ]

    fourseamx = [fourseam.x0.mean(), fourseam.x5.mean(), fourseam.x10.mean(), fourseam.x15.mean(), fourseam.x20.mean(), fourseam.x25.mean(), \
        fourseam.x30.mean(), fourseam.x35.mean(), fourseam.x40.mean(), fourseam.x45.mean(), fourseam.x50.mean()]
    fourseamz = [fourseam.z0.mean(), fourseam.z5.mean(), fourseam.z10.mean(), fourseam.z15.mean(), fourseam.z20.mean(), fourseam.z25.mean(), \
        fourseam.z30.mean(), fourseam.z35.mean(), fourseam.z40.mean(), fourseam.z45.mean(), fourseam.z50.mean()]

    twoseamx = [twoseam.x0.mean(), twoseam.x5.mean(), twoseam.x10.mean(), twoseam.x15.mean(), twoseam.x20.mean(), twoseam.x25.mean(), \
        twoseam.x30.mean(), twoseam.x35.mean(), twoseam.x40.mean(), twoseam.x45.mean(), twoseam.x50.mean()]
    twoseamz = [twoseam.z0.mean(), twoseam.z5.mean(), twoseam.z10.mean(), twoseam.z15.mean(), twoseam.z20.mean(), twoseam.z25.mean(), \
        twoseam.z30.mean(), twoseam.z35.mean(), twoseam.z40.mean(), twoseam.z45.mean(), twoseam.z50.mean()]

    cutterx = [cutter.x0.mean(), cutter.x5.mean(), cutter.x10.mean(), cutter.x15.mean(), cutter.x20.mean(), cutter.x25.mean(), \
        cutter.x30.mean(), cutter.x35.mean(), cutter.x40.mean(), cutter.x45.mean(), cutter.x50.mean()]
    cutterz = [cutter.z0.mean(), cutter.z5.mean(), cutter.z10.mean(), cutter.z15.mean(), cutter.z20.mean(), cutter.z25.mean(), \
        cutter.z30.mean(), cutter.z35.mean(), cutter.z40.mean(), cutter.z45.mean(), cutter.z50.mean()]

    sliderx = [slider.x0.mean(), slider.x5.mean(), slider.x10.mean(), slider.x15.mean(), slider.x20.mean(), slider.x25.mean(), \
        slider.x30.mean(), slider.x35.mean(), slider.x40.mean(), slider.x45.mean(), slider.x50.mean()]
    sliderz = [slider.z0.mean(), slider.z5.mean(), slider.z10.mean(), slider.z15.mean(), slider.z20.mean(), slider.z25.mean(), \
        slider.z30.mean(), slider.z35.mean(), slider.z40.mean(), slider.z45.mean(), slider.z50.mean()]

    changeupx = [changeup.x0.mean(), changeup.x5.mean(), changeup.x10.mean(), changeup.x15.mean(), changeup.x20.mean(), changeup.x25.mean(), \
        changeup.x30.mean(), changeup.x35.mean(), changeup.x40.mean(), changeup.x45.mean(), changeup.x50.mean()]
    changeupz = [changeup.z0.mean(), changeup.z5.mean(), changeup.z10.mean(), changeup.z15.mean(), changeup.z20.mean(), changeup.z25.mean(), \
        changeup.z30.mean(), changeup.z35.mean(), changeup.z40.mean(), changeup.z45.mean(), changeup.z50.mean()]

    splitterx = [splitter.x0.mean(), splitter.x5.mean(), splitter.x10.mean(), splitter.x15.mean(), splitter.x20.mean(), splitter.x25.mean(), \
        splitter.x30.mean(), splitter.x35.mean(), splitter.x40.mean(), splitter.x45.mean(), splitter.x50.mean()]
    splitterz = [splitter.z0.mean(), splitter.z5.mean(), splitter.z10.mean(), splitter.z15.mean(), splitter.z20.mean(), splitter.z25.mean(), \
        splitter.z30.mean(), splitter.z35.mean(), splitter.z40.mean(), splitter.z45.mean(), splitter.z50.mean()]

    curvex = [curve.x0.mean(), curve.x5.mean(), curve.x10.mean(), curve.x15.mean(), curve.x20.mean(), curve.x25.mean(), \
        curve.x30.mean(), curve.x35.mean(), curve.x40.mean(), curve.x45.mean(), curve.x50.mean()]
    curvez = [curve.z0.mean(), curve.z5.mean(), curve.z10.mean(), curve.z15.mean(), curve.z20.mean(), curve.z25.mean(), \
        curve.z30.mean(), curve.z35.mean(), curve.z40.mean(), curve.z45.mean(), curve.z50.mean()]

    sweeperx = [sweeper.x0.mean(), sweeper.x5.mean(), sweeper.x10.mean(), sweeper.x15.mean(), sweeper.x20.mean(), sweeper.x25.mean(), \
        sweeper.x30.mean(), sweeper.x35.mean(), sweeper.x40.mean(), sweeper.x45.mean(), sweeper.x50.mean()]
    sweeperz = [sweeper.z0.mean(), sweeper.z5.mean(), sweeper.z10.mean(), sweeper.z15.mean(), sweeper.z20.mean(), sweeper.z25.mean(), \
        sweeper.z30.mean(), sweeper.z35.mean(), sweeper.z40.mean(), sweeper.z45.mean(), sweeper.z50.mean()]
    
    fig = px.line_3d(x=fourseamx, y=tracey, z = fourseamz)

    # 포심

    fig.add_trace(go.Scatter3d(x=fourseamx, y=tracey, z=fourseamz, mode='lines',line = dict(color='red', width=ticks)))
    fig.add_trace(go.Scatter3d(x=[fourseamx[0]], y=[tracey[0]], z=[fourseamz[0]],mode = 'markers',marker=dict(color='red', size= size)))
    fig.add_trace(go.Scatter3d(x=[fourseamx[dis]], y=[tracey[dis]], z=[fourseamz[dis]],mode = 'markers',marker=dict(color='red', size= size)))

    # # 투심
    fig.add_trace(go.Scatter3d(x=twoseamx, y=tracey, z=twoseamz,mode='lines',line = dict(color='pink',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[twoseamx[0]], y=[tracey[0]], z=[twoseamz[0]],mode = 'markers',marker=dict(color='pink', size= size)))
    fig.add_trace(go.Scatter3d(x=[twoseamx[dis]], y=[tracey[dis]], z=[twoseamz[dis]],mode = 'markers',marker=dict(color='pink', size= size)))

    # # 커터
    fig.add_trace(go.Scatter3d(x=cutterx, y=tracey, z=cutterz,mode='lines',line = dict(color='purple',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[cutterx[0]], y=[tracey[0]], z=[cutterz[0]],mode = 'markers',marker=dict(color='purple', size= size)))
    fig.add_trace(go.Scatter3d(x=[cutterx[dis]], y=[tracey[dis]], z=[cutterz[dis]],mode = 'markers',marker=dict(color='purple', size= size)))

    # 슬라이더
    fig.add_trace(go.Scatter3d(x=sliderx, y=tracey, z=sliderz,mode='lines',line = dict(color='green',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[sliderx[0]], y=[tracey[0]], z=[sliderz[0]],mode = 'markers',marker=dict(color='green', size= size)))
    fig.add_trace(go.Scatter3d(x=[sliderx[dis]], y=[tracey[dis]], z=[sliderz[dis]],mode = 'markers',marker=dict(color='green', size= size)))

    # # 체인지업
    fig.add_trace(go.Scatter3d(x=changeupx, y=tracey, z=changeupz,mode='lines',line = dict(color='green',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[changeupx[0]], y=[tracey[0]], z=[changeupz[0]],mode = 'markers',marker=dict(color='green', size= size)))
    fig.add_trace(go.Scatter3d(x=[changeupx[dis]], y=[tracey[dis]], z=[changeupz[dis]],mode = 'markers',marker=dict(color='green', size= size)))

    # # # 포크
    fig.add_trace(go.Scatter3d(x=splitterx, y=tracey, z=splitterz,mode='lines',line = dict(color='brown',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[splitterx[0]], y=[tracey[0]], z=[splitterz[0]],mode = 'markers',marker=dict(color='brown', size= size)))
    fig.add_trace(go.Scatter3d(x=[splitterx[dis]], y=[tracey[dis]], z=[splitterz[dis]],mode = 'markers',marker=dict(color='brown', size= size)))

    # # 커브
    fig.add_trace(go.Scatter3d(x=curvex, y=tracey, z=curvez,mode='lines',line = dict(color='orange',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[curvex[0]], y=[tracey[0]], z=[curvez[0]],mode = 'markers',marker=dict(color='orange', size= size)))
    fig.add_trace(go.Scatter3d(x=[curvex[dis]], y=[tracey[dis]], z=[curvez[dis]],mode = 'markers',marker=dict(color='orange', size= size)))

    # # 스위퍼
    fig.add_trace(go.Scatter3d(x=sweeperx, y=tracey, z=sweeperz,mode='lines',line = dict(color='orange',width=ticks)))
    fig.add_trace(go.Scatter3d(x=[sweeperx[0]], y=[tracey[0]], z=[sweeperz[0]],mode = 'markers',marker=dict(color='orange', size= size)))
    fig.add_trace(go.Scatter3d(x=[sweeperx[dis]], y=[tracey[dis]], z=[sweeperz[dis]],mode = 'markers',marker=dict(color='orange', size= size)))


    # 존 그리기

    fig.add_trace(go.Scatter3d(x=ZX, y=ZY, z=ZZ,mode='lines',line = dict(color='BLACK',width=10)))

    fig.update_scenes(xaxis_backgroundcolor= 'rgb(151, 146, 137)',yaxis_backgroundcolor= 'rgb(151, 146, 137)',zaxis_backgroundcolor= 'rgb(151, 146, 137)')
    fig.update_layout(scene = dict(xaxis = dict(range=[-1,1],),yaxis = dict(range=[-1,18],),zaxis = dict(range=[0,2],),),scene_aspectmode='manual',scene_aspectratio=dict(x=1, y=3, z=1),
                    width = 800,height = 600,autosize=False,margin=dict(l=0, r=0, b=0, t=0),showlegend=False)

    return fig

def season_pitched_fig(dataframe):
    season_pitched_fig = px.density_contour(dataframe, x='plate_x', y='plate_z', z='pitname', histfunc="count", facet_row='stand',
                        #  hover_name="pitname", hover_data=["rel_speed(km)","pitch_kind","events"],
                         category_orders={"stand": ['R', 'L']}, 
                         height = 800, width = 1600)
    
    # 컬러 스케일 변경 - 보라색에서 주황색, 노란색으로 변경
    season_pitched_fig.update_traces(
        contours_coloring="fill", 
        colorscale="Plasma",
        showscale=False
    )

    season_pitched_fig.update_layout(
        autosize=False,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis_range=[-0.45,0.45],
        yaxis_range=[0.27,1.25],
        xaxis_title=None,
        bargap = 0,
        xaxis = dict({'showgrid': False, 'zeroline': False}),
        yaxis = dict({'showgrid': False, 'zeroline': False}),
        showlegend=False,
        plot_bgcolor='rgba(13,8,135,1)',
        paper_bgcolor='rgba(255,255,255,1)'
    )

    # 모든 서브플롯에 대해 축 라벨 제거
    for i in range(1, len(season_pitched_fig.layout.annotations) + 1):
        season_pitched_fig.update_xaxes(title=None, row=i, col=1)
        season_pitched_fig.update_yaxes(title=None, row=i, col=1)
    
    # facet 라벨(R, L) 제거
    for annotation in season_pitched_fig.layout.annotations:
        annotation.text = ""

    season_pitched_fig.update_yaxes(gridcolor='rgba(13,8,135,1)')
    season_pitched_fig.update_xaxes(gridcolor='rgba(13,8,135,1)')

    homex = [-0.23, 0.23, 0.23, -0.23, -0.23]
    homey = [0.45, 0.45, 1.05, 1.05, 0.45]

    season_pitched_fig.append_trace(go.Scatter(x=homex,y=homey, mode = 'lines', line=dict(color='white', width=4) ), row = 'all' , col = 'all')
    season_pitched_fig.add_trace(go.Scatter(x=[0], y=[0.43], text=["<b>Strike Zone<b>"], mode="text", textfont_size=18, textfont_color='white',), row = 'all' , col = 'all')

    homex = [-0.12, 0.12, 0.12, -0.12, -0.12]
    homey = [0.59, 0.59, 0.91, 0.91, 0.59]

    season_pitched_fig.append_trace(go.Scatter(x=homex,y=homey, mode = 'lines', line=dict(color='red', width=3) ), row = 'all' , col = 'all')
    season_pitched_fig.add_trace(go.Scatter(x=[0], y=[0.57], text=["<b>Core Zone<b>"], mode="text", textfont_size=20, textfont_color='red',), row = 'all' , col = 'all')

    season_pitched_fig.add_shape(type="rect", x0=-0.34, y0=0.915, x1=-0.125, y1=1.15, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')
    season_pitched_fig.add_shape(type="rect", x0=-0.115, y0=0.915, x1=0.115, y1=1.15, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')
    season_pitched_fig.add_shape(type="rect", x0=0.125, y0=0.915, x1=0.34, y1=1.15, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')

    season_pitched_fig.add_shape(type="rect", x0=-0.34, y0=0.595, x1=-0.125, y1=0.905, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')
    season_pitched_fig.add_shape(type="rect", x0=0.125, y0=0.595, x1=0.34, y1=0.905, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')

    season_pitched_fig.add_shape(type="rect", x0=-0.34, y0=0.35, x1=-0.125, y1=0.585, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')
    season_pitched_fig.add_shape(type="rect", x0=-0.115, y0=0.35, x1=0.115, y1=0.585, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')
    season_pitched_fig.add_shape(type="rect", x0=0.125, y0=0.35, x1=0.34, y1=0.585, line=dict(color="white", width=1, dash='dash'), row = 'all' , col = 'all')



    return season_pitched_fig

def season_location_fig(dataframe, pitch_name):
    sdf = dataframe
    
    season_location_fig = px.density_contour(
        sdf, 
        x='plate_x', 
        y='plate_z', 
        z='pitname', 
        histfunc="count", 
        facet_col='pitch_name', 
        facet_row='stand',
        category_orders={"stand": ['R', 'L']},
        height=600, 
        width=2400,
        title= pitch_name
    )

    # 컬러바 제거
    season_location_fig.update_traces(showscale=False)

    season_location_fig.update_layout(
        autosize=False,
        margin=dict(l=0, r=0, t=30, b=20),
        xaxis_range=[-0.45,0.45],
        yaxis_range=[0.27,1.25],
        bargap = 0,
        # xaxis = dict({'showgrid': False, 'zeroline': False, 'showticklabels': False}),
        # yaxis = dict({'showgrid': False, 'zeroline': False, 'showticklabels': False}),
        showlegend=False,
        plot_bgcolor='rgba(13,8,135,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        title_x=0.3
    )

        # 모든 서브플롯에 대해 설정 적용
    season_location_fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,  # x축 숫자 제거
        title=None
    )
    
    season_location_fig.update_yaxes(
        showgrid=False, 
        zeroline=False, 
        showticklabels=False,  # y축 숫자 제거
        title=None
    )
    
        # 서브플롯 간 간격 줄이기
    season_location_fig.update_layout(
        grid=dict(rows=2, columns=1, pattern="independent"),
        grid_xgap=0.01,  # x 방향 간격 줄이기
        grid_ygap=1   # y 방향 간격 줄이기
    )

    # 모든 서브플롯에 대해 축 라벨 제거
    for i in range(1, len(season_location_fig.layout.annotations) + 1):
        season_location_fig.update_xaxes(title=None, row=i, col=1)
        season_location_fig.update_yaxes(title=None, row=i, col=1)
    
    # facet 라벨(R, L) 제거
    for annotation in season_location_fig.layout.annotations:
        annotation.text = ""


    season_location_fig.update_yaxes(gridcolor='rgba(13,8,135,1)')
    season_location_fig.update_xaxes(gridcolor='rgba(13,8,135,1)')

    season_location_fig.update_traces(contours_coloring="fill", colorscale="Plasma", contours_showlabels=False)

    homex = [-0.23, 0.23, 0.23, -0.23, -0.23]
    homey = [0.45, 0.45, 1.05, 1.05, 0.45]

    season_location_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='white', width=4)), row='all', col='all')
    season_location_fig.add_trace(go.Scatter(x=[0], y=[0.43], text=["<b>Strike Zone<b>"], mode="text", textfont_size=18, textfont_color='white'), row='all', col='all')

    homex = [-0.12, 0.12, 0.12, -0.12, -0.12]
    homey = [0.59, 0.59, 0.91, 0.91, 0.59]

    season_location_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='red', width=3)), row='all', col='all')
    season_location_fig.add_trace(go.Scatter(x=[0], y=[0.57], text=["<b>Core Zone<b>"], mode="text", textfont_size=20, textfont_color='red'), row='all', col='all')

    season_location_fig.add_shape(type="rect", x0=-0.34, y0=0.915, x1=-0.125, y1=1.15, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    season_location_fig.add_shape(type="rect", x0=-0.115, y0=0.915, x1=0.115, y1=1.15, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    season_location_fig.add_shape(type="rect", x0=0.125, y0=0.915, x1=0.34, y1=1.15, line=dict(color="white", width=1, dash='dash'), row='all', col='all')

    season_location_fig.add_shape(type="rect", x0=-0.34, y0=0.595, x1=-0.125, y1=0.905, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    season_location_fig.add_shape(type="rect", x0=0.125, y0=0.595, x1=0.34, y1=0.905, line=dict(color="white", width=1, dash='dash'), row='all', col='all')

    season_location_fig.add_shape(type="rect", x0=-0.34, y0=0.35, x1=-0.125, y1=0.585, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    season_location_fig.add_shape(type="rect", x0=-0.115, y0=0.35, x1=0.115, y1=0.585, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    season_location_fig.add_shape(type="rect", x0=0.125, y0=0.35, x1=0.34, y1=0.585, line=dict(color="white", width=1, dash='dash'), row='all', col='all')
    
    return season_location_fig

def create_pitcher_swing_map_stand(df, pitcher_name, year):
    # 스윙맵 데이터 생성
    called_strike_df = df[(df['description'] == "called_strike")]
    called_strike_df['swingmap'] = 'Called Strike'
    whiff_df = df[(df['whiff'] == 1)]
    whiff_df['swingmap'] = 'Whiff'
    ball_df = df[(df['type'] == "B")]
    ball_df['swingmap'] = 'Ball'
    foul_df = df[(df['foul'] == 1)]
    foul_df['swingmap'] = 'Foul'
    hit_df = df[(df['hit'] == 1)]
    hit_df['swingmap'] = 'Hit'
    out_df = df[(df['field_out'] == 1)]
    out_df['swingmap'] = 'Out'
    
    swingmap_df = pd.concat([called_strike_df, whiff_df, ball_df, foul_df, hit_df, out_df])
    
    # 색상 및 심볼 정의
    colors = {
        'Called Strike': 'rgba(24,85,144,0.6)', 
        'Whiff': 'rgba(247,222,52,1)', 
        'Ball': 'rgba(108,122,137,0.7)', 
        'Foul': 'rgba(241,106,227,0.5)', 
        'Hit': 'rgba(255,105,97,1)', 
        'Out': 'rgba(140,86,75,0.6)'
    }
    
    symbols = {
        '4-Seam Fastball': 'circle', 
        '2-Seam Fastball': 'triangle-down', 
        'Cutter': 'triangle-se', 
        'Slider': 'triangle-right', 
        'Curveball': 'triangle-up', 
        'Changeup': 'diamond', 
        'Split-Finger': 'square',
        'Sweeper': 'cross'
    }
    
        # 스윙맵 생성
    swing_scatter_fig = px.scatter(
        swingmap_df, 
        x='plate_x', 
        y='plate_z', 
        color='swingmap', 
        symbol='pitch_name', 
        facet_col='swingmap', 
        facet_row='stand',
        color_discrete_map=colors,
        hover_name="pitname", 
        hover_data=["rel_speed(km)", "pitch_name", "events", "exit_velocity", "description", "launch_speed_angle", "launch_angle"],
        category_orders={
            "swingmap": ['Called Strike', 'Ball', 'Foul', 'Whiff', 'Hit', 'Out',],
        },
        template="simple_white",
        height=600, 
        width=2400
    )
    
    # 심볼 설정
    for i, d in enumerate(swing_scatter_fig.data):
        if i < len(swing_scatter_fig.data):  # 안전 검사 추가
            pitch_name = swing_scatter_fig.data[i].name.split(', ')[1] if ', ' in swing_scatter_fig.data[i].name else ""
            if pitch_name in symbols:
                swing_scatter_fig.data[i].marker.symbol = symbols[pitch_name]
    
    # 레이아웃 업데이트
    swing_scatter_fig.update_layout(
        autosize=False,
        margin=dict(l=50, r=50, t=70, b=50),  # 상단 여백 증가
        xaxis_range=[-0.45, 0.45],
        yaxis_range=[0.27, 1.25],
        xaxis={'showgrid': False, 'zeroline': False},
        yaxis={'showgrid': False, 'zeroline': False},
        showlegend=False,
        plot_bgcolor='rgba(255,255,255,0.1)', 
        paper_bgcolor='rgba(255,255,255,1)',
    )
    
    # 모든 subplot에 대한 y축 제목 제거
    swing_scatter_fig.update_yaxes(title_text='')
    swing_scatter_fig.update_xaxes(title_text='')
    
    # 모든 annotation 업데이트
    for annotation in swing_scatter_fig.layout.annotations:
        # "swingmap=" 부분을 제거
        if "swingmap=" in annotation.text:
            annotation.update(text=annotation.text.replace("swingmap=", ""))
        # "pitch_name=" 부분을 제거
        elif "pitch_name=" in annotation.text:
            pitch_text = annotation.text.replace("pitch_name=", "")
            annotation.update(text=pitch_text)
            # 왼쪽으로 이동하지 않고 기본 위치 유지
        
        # 기존 스타일 업데이트는 유지
        annotation.update(font=dict(size=20, color='black', family='Arial, bold'))
        # 제목 위치 조정
        annotation.update(y=annotation.y + 0.02)
    
    swing_scatter_fig.update_traces(marker=dict(size=20))
    
    # 스트라이크 존 표시
    swing_scatter_fig.add_hline(y=0.59, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_hline(y=0.91, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_vline(x=-0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_vline(x=0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    
    # Core Zone 표시
    homex = [-0.12, 0.12, 0.12, -0.12, -0.12]
    homey = [0.59, 0.59, 0.91, 0.91, 0.59]
    swing_scatter_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='red', width=4)), row='all', col='all')
    swing_scatter_fig.add_trace(go.Scatter(x=[0], y=[0.57], text=["<b>Core Zone<b>"], mode="text", textfont_size=20, textfont_color='red'), row='all', col='all')
    
    # Strike Zone 표시
    homex = [-0.26, 0.26, 0.26, -0.26, -0.26]
    homey = [0.45, 0.45, 1.05, 1.05, 0.45]
    swing_scatter_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='rgba(108,122,137,0.9)', width=4)), row='all', col='all')
    swing_scatter_fig.add_trace(go.Scatter(x=[0], y=[0.43], text=["<b>Strike Zone<b>"], mode="text", textfont_size=20, textfont_color='rgba(108,122,137,0.9)'), row='all', col='all')
    
    # 축 선 스타일 설정
    swing_scatter_fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
    swing_scatter_fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
    
    # 차트 표시
    st.plotly_chart(swing_scatter_fig, use_container_width=True, key=f"swing_map_stand_{pitcher_name}_{year}")


def create_pitcher_swing_map(df, pitcher_name, year, ordered_pitches):
    # 스윙맵 데이터 생성
    called_strike_df = df[(df['description'] == "called_strike")]
    called_strike_df['swingmap'] = 'Called Strike'
    whiff_df = df[(df['whiff'] == 1)]
    whiff_df['swingmap'] = 'Whiff'
    ball_df = df[(df['type'] == "B")]
    ball_df['swingmap'] = 'Ball'
    foul_df = df[(df['foul'] == 1)]
    foul_df['swingmap'] = 'Foul'
    hit_df = df[(df['hit'] == 1)]
    hit_df['swingmap'] = 'Hit'
    out_df = df[(df['field_out'] == 1)]
    out_df['swingmap'] = 'Out'
    
    swingmap_df = pd.concat([called_strike_df, whiff_df, ball_df, foul_df, hit_df, out_df])
    
    # 색상 및 심볼 정의
    colors = {
        'Called Strike': 'rgba(24,85,144,0.6)', 
        'Whiff': 'rgba(247,222,52,1)', 
        'Ball': 'rgba(108,122,137,0.7)', 
        'Foul': 'rgba(241,106,227,0.5)', 
        'Hit': 'rgba(255,105,97,1)', 
        'Out': 'rgba(140,86,75,0.6)'
    }
    
    symbols = {
        '4-Seam Fastball': 'circle', 
        '2-Seam Fastball': 'triangle-down', 
        'Cutter': 'triangle-se', 
        'Slider': 'triangle-right', 
        'Curveball': 'triangle-up', 
        'Changeup': 'diamond', 
        'Split-Finger': 'square',
        'Sweeper': 'cross'
    }
    
    available_pitches = swingmap_df['pitch_name'].unique().tolist()
    filtered_ordered_pitches = [pitch for pitch in ordered_pitches if pitch in available_pitches]

        # 스윙맵 생성
    swing_scatter_fig = px.scatter(
        swingmap_df, 
        x='plate_x', 
        y='plate_z', 
        color='swingmap', 
        symbol='pitch_name', 
        facet_col='swingmap', 
        facet_row='pitch_name',
        color_discrete_map=colors,
        hover_name="pitname", 
        hover_data=["rel_speed(km)", "pitch_name", "events", "exit_velocity", "description", "launch_speed_angle", "launch_angle"],
        category_orders={
            "swingmap": ['Called Strike', 'Ball', 'Foul', 'Whiff', 'Hit', 'Out',],
            "pitch_name" : filtered_ordered_pitches
        },
        template="simple_white",
        height=300 * len(ordered_pitches), 
        width=2400
    )
    
    # 심볼 설정
    for i, d in enumerate(swing_scatter_fig.data):
        if i < len(swing_scatter_fig.data):  # 안전 검사 추가
            pitch_name = swing_scatter_fig.data[i].name.split(', ')[1] if ', ' in swing_scatter_fig.data[i].name else ""
            if pitch_name in symbols:
                swing_scatter_fig.data[i].marker.symbol = symbols[pitch_name]
    
    # 레이아웃 업데이트
    swing_scatter_fig.update_layout(
        autosize=False,
        margin=dict(l=50, r=50, t=70, b=50),  # 상단 여백 증가
        xaxis_range=[-0.45, 0.45],
        yaxis_range=[0.27, 1.25],
        xaxis={'showgrid': False, 'zeroline': False},
        yaxis={'showgrid': False, 'zeroline': False},
        showlegend=False,
        plot_bgcolor='rgba(255,255,255,0.1)', 
        paper_bgcolor='rgba(255,255,255,1)',
    )
    
    # 모든 subplot에 대한 y축 제목 제거
    swing_scatter_fig.update_yaxes(title_text='')
    swing_scatter_fig.update_xaxes(title_text='')
    
    # 모든 annotation 업데이트
    for annotation in swing_scatter_fig.layout.annotations:
        # "swingmap=" 부분을 제거
        if "swingmap=" in annotation.text:
            annotation.update(text=annotation.text.replace("swingmap=", ""))
        # "pitch_name=" 부분을 제거
        elif "pitch_name=" in annotation.text:
            pitch_text = annotation.text.replace("pitch_name=", "")
            annotation.update(text=pitch_text)
            # 왼쪽으로 이동하지 않고 기본 위치 유지
        
        # 기존 스타일 업데이트는 유지
        annotation.update(font=dict(size=20, color='black', family='Arial, bold'))
        # 제목 위치 조정
        annotation.update(y=annotation.y + 0.02)
    
    swing_scatter_fig.update_traces(marker=dict(size=20))
    
    # 스트라이크 존 표시
    swing_scatter_fig.add_hline(y=0.59, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_hline(y=0.91, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_vline(x=-0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    swing_scatter_fig.add_vline(x=0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
    
    # Core Zone 표시
    homex = [-0.12, 0.12, 0.12, -0.12, -0.12]
    homey = [0.59, 0.59, 0.91, 0.91, 0.59]
    swing_scatter_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='red', width=4)), row='all', col='all')
    swing_scatter_fig.add_trace(go.Scatter(x=[0], y=[0.57], text=["<b>Core Zone<b>"], mode="text", textfont_size=20, textfont_color='red'), row='all', col='all')
    
    # Strike Zone 표시
    homex = [-0.26, 0.26, 0.26, -0.26, -0.26]
    homey = [0.45, 0.45, 1.05, 1.05, 0.45]
    swing_scatter_fig.append_trace(go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='rgba(108,122,137,0.9)', width=4)), row='all', col='all')
    swing_scatter_fig.add_trace(go.Scatter(x=[0], y=[0.43], text=["<b>Strike Zone<b>"], mode="text", textfont_size=20, textfont_color='rgba(108,122,137,0.9)'), row='all', col='all')
    
    # 축 선 스타일 설정
    swing_scatter_fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
    swing_scatter_fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
    
    # 차트 표시
    st.plotly_chart(swing_scatter_fig, use_container_width=True, key=f"swing_map_season_{pitcher_name}_{year}")


def pitch_by_pitch_map(dataframe, width_per_batter=250, height=350):
    """
    투구 데이터를 이닝별, 타자별로 시각화하는 함수
    
    Parameters:
    -----------
    dataframe : DataFrame
        투구 데이터가 포함된 데이터프레임
    width_per_batter : int, optional (default=250)
        타자 한 명당 그래프 너비
    height : int, optional (default=400)
        그래프 높이
    
    Returns:
    --------
    dict
        이닝별 Plotly 그래프 객체가 저장된 딕셔너리
    """
    sdf = dataframe
    figures = {}  # 이닝별 그래프를 저장할 딕셔너리
    
    for i in sdf.inning.unique():
        # 해당 이닝 데이터 추출 및 인덱스 설정
        pitch_by_pitch_df = sdf[sdf['inning'] == i].reset_index(drop=True)
        pitch_by_pitch_df = pitch_by_pitch_df.reset_index()
        pitch_by_pitch_df['index'] = pitch_by_pitch_df['index'] + 1

        batter = len(pitch_by_pitch_df.batname.unique())
        
        # 동적 그래프 크기 계산 (타자 수에 따라 조정)
        total_width = batter * width_per_batter
        
        # 색상 및 심볼 매핑
        colors = {
            'called_strike': 'rgba(24,85,144,0.6)', 
            'swinging_strike': 'rgba(247,222,52,1)', 
            'ball': 'rgba(108,122,137,0.7)', 
            'foul': 'rgba(241,106,227,0.5)', 
            'hit_into_play_no_out': 'rgba(255,105,97,1)', 
            'hit_into_play_score': 'rgba(255,105,97,1)',
            'hit_into_play': 'rgba(140,86,75,0.6)'
        }
        symbols = {
            '4-Seam Fastball': 'circle', 
            '2-Seam Fastball': 'triangle-down', 
            'Cutter': 'triangle-se', 
            'Slider': 'triangle-right', 
            'Curveball': 'triangle-up', 
            'Changeup': 'diamond', 
            'Split-Finger': 'square', 
            'Sweeper': 'cross'
        }

        # 그래프 생성
        pitch_by_pitch_fig = px.scatter(
            pitch_by_pitch_df, 
            x='plate_x', 
            y='plate_z', 
            color='description', 
            symbol='pitch_name', 
            facet_col='batname', 
            facet_row='inning', 
            text='index',
            color_discrete_map=colors,
            hover_name="pitname", 
            hover_data=["rel_speed(km)", "pitch_name", "events", "exit_velocity", "description", "launch_speed_angle", "launch_angle"],
            template="simple_white",
            height=height,  # 사용자 정의 높이 적용
            width=total_width  # 타자 수에 따라 동적으로 너비 계산
        )

        # 심볼 설정
        for a, b in enumerate(pitch_by_pitch_fig.data):
            try:
                if ', ' in pitch_by_pitch_fig.data[a].name:
                    pitch_name = pitch_by_pitch_fig.data[a].name.split(', ')[1]
                    if pitch_name in symbols:
                        pitch_by_pitch_fig.data[a].marker.symbol = symbols[pitch_name]
            except (IndexError, AttributeError):
                continue  # 심볼 설정 중 오류 발생 시 계속 진행

        # 레이아웃 설정
        pitch_by_pitch_fig.update_layout(
            autosize=False,  # 자동 크기 조정 비활성화
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis_range=[-0.6, 0.6],
            yaxis_range=[0.0, 1.5],
            xaxis={'showgrid': False, 'zeroline': False},
            yaxis={'showgrid': False, 'zeroline': False},
            showlegend=False,
            plot_bgcolor='rgba(255,255,255,0.1)', 
            paper_bgcolor='rgba(255,255,255,1)'
        )

        # 모든 subplot에 대한 y축 제목 제거
        pitch_by_pitch_fig.update_yaxes(title_text='')
        pitch_by_pitch_fig.update_xaxes(title_text='')
        
        # 모든 annotation 업데이트
        for annotation in pitch_by_pitch_fig.layout.annotations:
            # "swingmap=" 부분을 제거
            if "batname=" in annotation.text:
                annotation.update(text=annotation.text.replace("batname=", ""))
            # "pitch_name=" 부분을 제거
            elif "inning=" in annotation.text:
                pitch_text = annotation.text.replace("inning=", "")
                annotation.update(text=pitch_text)
                # 왼쪽으로 이동하지 않고 기본 위치 유지
            
            # 기존 스타일 업데이트는 유지
            annotation.update(font=dict(size=20, color='black', family='Arial, bold'))
            # 제목 위치 조정
            annotation.update(y=annotation.y + 0.02)

        # 마커 및 텍스트 크기 설정
        pitch_by_pitch_fig.update_traces(marker=dict(size=40))
        pitch_by_pitch_fig.update_traces(textfont_size=24)

        # 코어존 및 스트라이크존 라인 추가
        pitch_by_pitch_fig.add_hline(y=0.59, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
        pitch_by_pitch_fig.add_hline(y=0.91, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
        pitch_by_pitch_fig.add_vline(x=-0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')
        pitch_by_pitch_fig.add_vline(x=0.12, line_width=2, line_dash='dash', line_color='rgba(30,30,30,0.8)')

        # 코어존 표시
        homex = [-0.12, 0.12, 0.12, -0.12, -0.12]
        homey = [0.59, 0.59, 0.91, 0.91, 0.59]
        pitch_by_pitch_fig.append_trace(
            go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='red', width=4)), 
            row='all', col='all'
        )
        pitch_by_pitch_fig.add_trace(
            go.Scatter(x=[0], y=[0.57], text=["<b>Core Zone<b>"], mode="text", textfont_size=20, textfont_color='red'), 
            row='all', col='all'
        )

        # 스트라이크존 표시
        homex = [-0.26, 0.26, 0.26, -0.26, -0.26]
        homey = [0.45, 0.45, 1.05, 1.05, 0.45]
        pitch_by_pitch_fig.append_trace(
            go.Scatter(x=homex, y=homey, mode='lines', line=dict(color='rgba(108,122,137,0.9)', width=4)), 
            row='all', col='all'
        )
        pitch_by_pitch_fig.add_trace(
            go.Scatter(x=[0], y=[0.43], text=["<b>Strike Zone<b>"], mode="text", textfont_size=20, textfont_color='rgba(108,122,137,0.9)'), 
            row='all', col='all'
        )

        # 축 라인 설정
        pitch_by_pitch_fig.update_xaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
        pitch_by_pitch_fig.update_yaxes(showline=True, linewidth=1, linecolor='rgba(108,122,137,0.9)', mirror=True)
        
        # 이닝별 그래프를 딕셔너리에 저장
        figures[i] = pitch_by_pitch_fig
    
    return figures
