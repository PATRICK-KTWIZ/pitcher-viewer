import pandas as pd
import streamlit as st
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

PITCH_ORDER = [
    "4-Seam Fastball", "2-Seam Fastball", "Cutter", "Slider",
    "Sweeper", "Curveball", "Changeup", "Split-Finger",
]
COLOR_MAP = {
    "4-Seam Fastball": "red",
    "2-Seam Fastball": "pink",
    "Cutter":          "purple",
    "Slider":          "green",
    "Changeup":        "blue",
    "Curveball":       "orange",
    "Split-Finger":    "brown",
    "Sweeper":         "gold",
}
YEAR_COLORS = ["#E63946", "#2196F3", "#FF9800", "#4CAF50", "#9C27B0", "#00BCD4"]

# ════════════════════════════════════════════════════════════
# 공통 축 / 레이아웃 헬퍼
# ════════════════════════════════════════════════════════════
def _movement_axis_lines(fig):
    for v in [-80, -60, -40, -20, 20, 40, 60, 80]:
        fig.add_vline(x=v, line_width=0.7, line_dash="dash",
                      line_color="rgba(108,122,137,0.8)")
        fig.add_hline(y=v, line_width=0.7, line_dash="dash",
                      line_color="rgba(108,122,137,0.8)")
    fig.add_vline(x=0, line_width=2, line_color="rgba(108,122,137,0.8)")
    fig.add_hline(y=0, line_width=2, line_color="rgba(108,122,137,0.8)")
    return fig


def _movement_layout(fig, width=600, height=600):
    fig.update_yaxes(
        range=[-0.7, 0.7], mirror=True,
        showline=True, linewidth=1, linecolor="#dbdbdb",
        ticks="outside", tickwidth=1, tickcolor="#dbdbdb", showgrid=True,
    )
    fig.update_xaxes(
        range=[-0.7, 0.7], mirror=True,
        showline=True, linewidth=1, linecolor="#dbdbdb",
        ticks="outside", tickwidth=1, tickcolor="#dbdbdb", showgrid=True,
    )
    fig.update_layout(
        showlegend=True,
        width=width, height=height,
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#dbdbdb", width=2),
        )],
    )
    return fig


# ════════════════════════════════════════════════════════════
# 무브먼트 차트 (과거 시즌 회색 처리)
# ════════════════════════════════════════════════════════════
def season_movement_chart(dataframe: pd.DataFrame):
    """
    최신 시즌은 구종별 컬러, 과거 시즌은 회색(투명도 낮춤)으로 표시.
    """
    df = dataframe.copy()
    if df.empty:
        return go.Figure()

    latest_year = int(df["game_year"].max())
    fig = go.Figure()

    # ── 과거 시즌 (회색) ────────────────────────────────────
    past_df = df[df["game_year"] < latest_year]
    if not past_df.empty:
        past_years = sorted(past_df["game_year"].unique())
        for yr in past_years:
            yr_df = past_df[past_df["game_year"] == yr]
            fig.add_trace(go.Scatter(
                x=yr_df["hor_break"],
                y=yr_df["ver_break"],
                mode="markers",
                marker=dict(size=10, color="rgba(180,180,180,0.35)", line=dict(width=0)),
                name=str(yr),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "구종: %{customdata[1]}<br>"
                    "날짜: %{customdata[2]}<br>"
                    "타자: %{customdata[3]}<br>"
                    "결과: %{customdata[4]}<extra></extra>"
                ),
                customdata=yr_df[["pitname", "pitch_name", "game_date", "batname", "events"]].values,
            ))

    # ── 최신 시즌 (구종별 컬러) ─────────────────────────────
    latest_df = df[df["game_year"] == latest_year]
    for pitch in PITCH_ORDER:
        p_df = latest_df[latest_df["pitch_name"] == pitch]
        if p_df.empty:
            continue
        color = COLOR_MAP.get(pitch, "gray")
        hover_cols = ["pitname", "pitch_name", "game_date", "batname",
                      "events", "description"]
        # 존재하는 컬럼만 사용
        avail = [c for c in hover_cols if c in p_df.columns]
        fig.add_trace(go.Scatter(
            x=p_df["hor_break"],
            y=p_df["ver_break"],
            mode="markers",
            marker=dict(size=14, color=color, opacity=0.85,
                        line=dict(width=0.5, color="white")),
            name=f"{pitch} ({latest_year})",
            hovertemplate=(
                f"<b>{{{{customdata[0]}}}} · {pitch}</b><br>"
                "날짜: %{customdata[2]}<br>"
                "타자: %{customdata[3]}<br>"
                "결과: %{customdata[4]}<extra></extra>"
            ),
            customdata=p_df[avail].values,
        ))

    fig = _movement_axis_lines(fig)
    fig = _movement_layout(fig)
    fig.update_layout(
        title=dict(
            text=f"Movement Chart  <span style='font-size:12px;color:gray'>"
                 f"(컬러={latest_year} / 회색=과거시즌)</span>",
            font=dict(size=14),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="left", x=0, font=dict(size=10),
        ),
    )
    return fig


# ════════════════════════════════════════════════════════════
# 피치 트래킹 차트
# ════════════════════════════════════════════════════════════
def season_pitchtrack_chart(dataframe):
    sdf = dataframe

    zone = pd.DataFrame(dict(
        x=[-0.23, 0.23, 0.23, -0.23, -0.23],
        y=[0.45,  0.45, 1.05, 1.05,  0.45],
    ))
    tracey = [0, 1.524, 3.048, 4.572, 6.096, 7.62,
              9.114, 10.668, 12.192, 13.716, 15.24]

    XL, XR, ZB, ZT = -0.23, 0.23, 0.45, 1.05
    ZX = [XL, XL, XR, XR, XL]
    ZY = [0, 0, 0, 0, 0]
    ZZ = [ZB, ZT, ZT, ZB, ZB]

    fig = go.Figure()

    pitch_groups = {
        "4-Seam Fastball": sdf[sdf.pitch_name == "4-Seam Fastball"],
        "2-Seam Fastball": sdf[sdf.pitch_name == "2-Seam Fastball"],
        "Cutter":          sdf[sdf.pitch_name == "Cutter"],
        "Slider":          sdf[sdf.pitch_name == "Slider"],
        "Sweeper":         sdf[sdf.pitch_name == "Sweeper"],
        "Curveball":       sdf[sdf.pitch_name == "Curveball"],
        "Changeup":        sdf[sdf.pitch_name == "Changeup"],
        "Split-Finger":    sdf[sdf.pitch_name == "Split-Finger"],
    }

    for pitch_name, p_df in pitch_groups.items():
        if p_df.empty:
            continue
        color = COLOR_MAP.get(pitch_name, "gray")
        avail_hover = [c for c in ["pitname", "rel_speed(km)", "pitch_name",
                                    "game_date", "batname", "events",
                                    "exit_velocity", "description",
                                    "launch_speed_angle", "launch_angle"]
                       if c in p_df.columns]
        fig.add_trace(go.Scatter3d(
            x=p_df["rel_pos_x"] if "rel_pos_x" in p_df.columns else [],
            y=p_df["rel_pos_y"] if "rel_pos_y" in p_df.columns else [],
            z=p_df["rel_pos_z"] if "rel_pos_z" in p_df.columns else [],
            mode="markers",
            marker=dict(size=3, color=color, opacity=0.6),
            name=pitch_name,
        ))

    # 스트라이크 존
    fig.add_trace(go.Scatter3d(
        x=ZX, y=ZY, z=ZZ,
        mode="lines",
        line=dict(color="black", width=3),
        name="Strike Zone",
        showlegend=False,
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-0.5, 0.5], title="X"),
            yaxis=dict(range=[0, 18],     title="Distance"),
            zaxis=dict(range=[0, 2.5],    title="Z"),
            aspectmode="manual",
            aspectratio=dict(x=1, y=3, z=1),
        ),
        width=700, height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="white",
    )
    return fig


# ════════════════════════════════════════════════════════════
# 구종 비율 차트
# ════════════════════════════════════════════════════════════
def season_pitched_fig(dataframe):
    df = dataframe.copy()
    if df.empty:
        return go.Figure()

    latest_year = int(df["game_year"].max())
    df_latest   = df[df["game_year"] == latest_year]

    pitch_counts = (
        df_latest.groupby("pitch_name")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    pitch_counts["pct"] = (
        pitch_counts["count"] / pitch_counts["count"].sum() * 100
    ).round(1)

    colors = [COLOR_MAP.get(p, "gray") for p in pitch_counts["pitch_name"]]

    fig = go.Figure(go.Bar(
        x=pitch_counts["pitch_name"],
        y=pitch_counts["pct"],
        marker_color=colors,
        text=pitch_counts["pct"].astype(str) + "%",
        textposition="outside",
    ))
    fig.update_layout(
        title=f"구종 비율 ({latest_year})",
        yaxis_title="%",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ════════════════════════════════════════════════════════════
# 로케이션 차트
# ════════════════════════════════════════════════════════════
def season_location_fig(dataframe, stand="R"):
    df = dataframe.copy()
    if df.empty:
        return go.Figure()

    if "stand" in df.columns:
        df = df[df["stand"] == stand]

    latest_year = int(df["game_year"].max())
    df_latest   = df[df["game_year"] == latest_year]

    fig = px.scatter(
        df_latest,
        x="plate_x", y="plate_z",
        color="pitch_name",
        category_orders={"pitch_name": PITCH_ORDER},
        color_discrete_map=COLOR_MAP,
        hover_data=["pitname", "pitch_name", "game_date", "batname",
                    "events", "description"],
        template="plotly_white",
    )
    # 스트라이크 존
    fig.add_shape(type="rect",
                  x0=-0.2794, y0=0.4572, x1=0.2794, y1=1.0668,
                  line=dict(color="black", width=2))
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    fig.update_layout(
        title=f"Location ({stand}HB) · {latest_year}",
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0),
    )
    return fig


# ════════════════════════════════════════════════════════════
# 스윙 맵
# ════════════════════════════════════════════════════════════
def _swing_map_base(df, title="Swing Map"):
    fig = px.density_heatmap(
        df, x="plate_x", y="plate_z",
        nbinsx=20, nbinsy=20,
        color_continuous_scale="RdYlGn_r",
        template="plotly_white",
    )
    fig.add_shape(type="rect",
                  x0=-0.2794, y0=0.4572, x1=0.2794, y1=1.0668,
                  line=dict(color="black", width=2))
    fig.update_layout(
        title=title,
        height=450,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_pitcher_swing_map(dataframe):
    return _swing_map_base(dataframe, "Swing Map (전체)")


def create_pitcher_swing_map_stand(dataframe, stand="R"):
    df = dataframe[dataframe["stand"] == stand] if "stand" in dataframe.columns else dataframe
    return _swing_map_base(df, f"Swing Map ({stand}HB)")


# ════════════════════════════════════════════════════════════
# 투구별 맵
# ════════════════════════════════════════════════════════════
def pitch_by_pitch_map(dataframe):
    df = dataframe.copy()
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="plate_x", y="plate_z",
        color="pitch_name",
        symbol="description",
        category_orders={"pitch_name": PITCH_ORDER},
        color_discrete_map=COLOR_MAP,
        hover_data=["pitname", "pitch_name", "game_date",
                    "batname", "events", "description"],
        template="plotly_white",
    )
    fig.add_shape(type="rect",
                  x0=-0.2794, y0=0.4572, x1=0.2794, y1=1.0668,
                  line=dict(color="black", width=2))
    fig.update_traces(marker=dict(size=9, opacity=0.75))
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0, font=dict(size=9)),
    )
    return fig
