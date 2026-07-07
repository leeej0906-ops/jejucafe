# -*- coding: utf-8 -*-
"""
제주도 카페 분석 & 지도 시각화 (Streamlit + Folium + MarkerCluster)

- 데이터: 제주상권 .csv  (cp949 인코딩)
- 지도: 마커 클릭 시 상호명(popup), 마우스 오버 시 법정동명(tooltip)
"""

import os
from urllib.parse import quote
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(page_title="제주도 카페 분석", page_icon="☕", layout="wide")

CSV_PATH = "제주상권 .csv"          # 파일명에 공백이 포함되어 있음
JEJU_CENTER = [33.38, 126.55]       # 제주도 중심 좌표


# ----------------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def load_cafes(path: str) -> pd.DataFrame:
    use_cols = [
        "상호명", "상권업종대분류명", "상권업종중분류명", "상권업종소분류명",
        "시군구명", "행정동명", "법정동명", "도로명주소", "경도", "위도",
    ]
    df = pd.read_csv(path, encoding="cp949", usecols=use_cols)

    # 카페만 필터링 (소분류명 == '카페')
    df = df[df["상권업종소분류명"] == "카페"].copy()

    # 좌표 정리
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df = df.dropna(subset=["경도", "위도"])

    # 제주도 좌표 범위로 이상치 제거
    df = df[df["위도"].between(33.0, 34.1) & df["경도"].between(126.0, 127.1)]

    # 결측 상호명 정리
    df["상호명"] = df["상호명"].fillna("(상호명 없음)")
    df["법정동명"] = df["법정동명"].fillna("(법정동 정보 없음)")
    df["도로명주소"] = df["도로명주소"].fillna("(도로명주소 정보 없음)")

    return df.reset_index(drop=True)


# ----------------------------------------------------------------------------
# 지도 생성
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="지도를 생성하는 중입니다...")
def build_map(df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=JEJU_CENTER, zoom_start=11, tiles="CartoDB positron")
    cluster = MarkerCluster(name="카페").add_to(m)

    for row in df.itertuples(index=False):
        # 마우스 클릭 시 표시할 팝업: 상호명 + 도로명주소(클릭 시 네이버 지도 검색 링크)
        map_url = "https://map.naver.com/p/search/" + quote(str(row.도로명주소))
        popup_html = (
            f"<div style='min-width:180px'>"
            f"<b style='font-size:14px'>{row.상호명}</b><br>"
            f"<a href='{map_url}' target='_blank' rel='noopener noreferrer' "
            f"style='font-size:12px;color:#1a73e8;text-decoration:underline'>"
            f"📍 {row.도로명주소}</a>"
            f"</div>"
        )
        folium.Marker(
            location=[row.위도, row.경도],
            # 마우스 클릭 시 상호명 + 도로명주소 표시
            popup=folium.Popup(popup_html, max_width=300),
            # 마우스 오버 시 법정동명 표시
            tooltip=row.법정동명,
            icon=folium.Icon(color="cadetblue", icon="coffee", prefix="fa"),
        ).add_to(cluster)

    folium.LayerControl().add_to(m)

    # 마커 클릭(팝업 오픈) 시, 마우스 오버로 떠 있던 툴팁(법정동명)을 즉시 숨김
    hide_tooltip_js = f"""
        {m.get_name()}.on('popupopen', function() {{
            document.querySelectorAll('.leaflet-tooltip').forEach(function(t) {{
                t.style.display = 'none';
            }});
        }});
    """
    m.get_root().script.add_child(folium.Element(hide_tooltip_js))
    return m


# ----------------------------------------------------------------------------
# 메인
# ----------------------------------------------------------------------------
def main():
    st.title("☕ 제주도 카페")

    if not os.path.exists(CSV_PATH):
        st.error(f"'{CSV_PATH}' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 두세요.")
        st.stop()

    df = load_cafes(CSV_PATH)

    # ---- 사이드바 필터 ----
    st.sidebar.header("🔎 필터")
    sigungu_opts = ["전체"] + sorted(df["시군구명"].dropna().unique().tolist())
    sel_sigungu = st.sidebar.selectbox("시군구", sigungu_opts)

    fdf = df if sel_sigungu == "전체" else df[df["시군구명"] == sel_sigungu]

    dong_opts = ["전체"] + sorted(fdf["법정동명"].dropna().unique().tolist())
    sel_dong = st.sidebar.selectbox("법정동", dong_opts)
    if sel_dong != "전체":
        fdf = fdf[fdf["법정동명"] == sel_dong]

    keyword = st.sidebar.text_input("상호명 검색")
    if keyword:
        fdf = fdf[fdf["상호명"].str.contains(keyword, case=False, na=False)]

    # ---- 핵심 지표 ----
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 카페 수", f"{len(df):,} 개")
    c2.metric("필터 결과", f"{len(fdf):,} 개")
    c3.metric("법정동 수", f"{fdf['법정동명'].nunique():,} 개")

    st.divider()

    # ---- 분석 차트 ----
    st.subheader("📊 카페 분포 분석")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**시군구별 카페 수**")
        st.bar_chart(fdf["시군구명"].value_counts())

    with col_b:
        st.markdown("**법정동별 카페 수 (상위 15)**")
        st.bar_chart(fdf["법정동명"].value_counts().head(15))

    st.divider()

    # ---- 지도 ----
    st.subheader("🗺️ 카페 위치 지도")
    st.caption("마커에 **마우스를 올리면** 법정동명이, 마커를 **클릭**하면 상호명과 도로명주소가 표시됩니다. (클릭 시 법정동명 툴팁은 사라집니다)")

    MAX_MARKERS = 3000
    map_df = fdf
    if len(fdf) > MAX_MARKERS:
        st.info(f"마커가 많아 {MAX_MARKERS:,}개까지만 표시합니다.")
        map_df = fdf.head(MAX_MARKERS)

    if len(map_df) == 0:
        st.warning("조건에 맞는 카페가 없습니다.")
    else:
        fmap = build_map(map_df)
        st_folium(fmap, width=None, height=600, returned_objects=[])

    st.divider()

    # ---- 원본 데이터 ----
    with st.expander("📋 데이터 표 보기"):
        st.dataframe(
            fdf[["상호명", "시군구명", "행정동명", "법정동명", "도로명주소", "위도", "경도"]]
            .reset_index(drop=True),
            width="stretch",
        )


if __name__ == "__main__":
    main()
