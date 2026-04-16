import os
import pandas as pd
import numpy as np
from io import BytesIO
import requests

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

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

# ════════════════════════════════════════════════════════════
# 2. 데이터 로드
# ════════════════════════════════════════════════════════════
MIN_YEAR = 2023

def load_league_data(league_name, min_year=MIN_YEAR):
    file_name  = LEAGUE_FILES[league_name]
    cache_path = os.path.join(CACHE_DIR, file_name)
    if os.path.exists(cache_path):
        print(f"[{league_name}] 로컬 캐시에서 로드 중...")
        df_tmp = pd.read_parquet(cache_path)
        return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp

    print(f"[{league_name}] GitHub Release에서 다운로드 중...")
    release_url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG_NAME}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    response    = requests.get(release_url, headers=headers)
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
            "Accept": "application/octet-stream",
            "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else ""
        })
        res = session.get(target_asset["url"])
        if res.status_code != 200:
            print(f"다운로드 실패: {res.status_code}")
            return pd.DataFrame()
        try:
            df_tmp = pd.read_parquet(BytesIO(res.content))
            df_tmp.to_parquet(cache_path, index=False)   # 캐시는 전체 저장
            print(f"[{league_name}] 불러오기 성공 & 캐시 저장 완료 ({df_tmp.shape[0]:,}행)")
            return df_tmp[df_tmp["game_year"] >= min_year] if min_year else df_tmp
        except Exception as e:
            print(f"파싱 실패: {e}")
            return pd.DataFrame()



