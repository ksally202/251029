import os, time, requests, pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

load_dotenv()
NEMC_API_KEY = os.getenv("NEMC_API_KEY")    # data.go.kr 발급키
HIRA_API_KEY = os.getenv("HIRA_API_KEY")    # HIRA 발급키
KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY")# Kakao Developers REST KEY

st.set_page_config(page_title="임산부 병원 실시간 찾기", layout="wide")
st.title("임산부 병원 실시간 위치·수용여부 확인")

# ----- 검색/필터 -----
col1, col2, col3 = st.columns([2,1,1])
with col1:
    keyword = st.text_input("지역/병원명 검색", value="강남구")
with col2:
    radius_km = st.slider("반경 (km)", 1, 30, 10)
with col3:
    only_obgyn = st.checkbox("산부인과 보유만 보기", value=True)

# ----- 유틸: 주소→좌표 (Kakao Local) -----
def geocode(addr: str):
    if not addr or not KAKAO_REST_KEY:
        return None
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    r = requests.get(url, headers=headers, params={"query": addr}, timeout=5)
    if r.ok and r.json().get("documents"):
        d = r.json()["documents"][0]
        return float(d["y"]), float(d["x"])  # lat, lon
    return None

# ----- 실시간 응급의료기관 (NEMC/E-Gen) -----
@st.cache_data(ttl=60)  # 60초 캐시
def fetch_emergency_now(sido=None, sigungu=None, keyword=None):
    # 실제 문서 예: serviceKey, pageNo, numOfRows, HPID(병원키), STAGE1(시도), STAGE2(시군구) ...
    url = "https://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"  # 예시
    params = {
        "serviceKey": NEMC_API_KEY,
        "Q0": sido or "",    # 시도
        "Q1": sigungu or "", # 시군구
        "QD": keyword or "", # 병원명/키워드
        "numOfRows": 1000,
        "pageNo": 1,
        "_type": "json",
    }
    r = requests.get(url, params=params, timeout=7)
    r.raise_for_status()
    items = r.json()["response"]["body"]["items"]["item"]
    df = pd.DataFrame(items)
    # 기대 필드 예시: hpid, dutyName(병원명), dutyTel3(응급실), wgs84Lon, wgs84Lat, 
    #                 hvec(응급실가용), hvoc(수술실가용), hvcc(중환자실가용) 등
    # 문서에 맞게 필드명을 확인 후 조정하세요.
    return df

# ----- HIRA 병원정보 (정적: 산부인과 보유 추정) -----
@st.cache_data(ttl=3600*24*7)  # 7일 캐시
def fetch_hira_obgyn():
    # HIRA 오픈API 문서대로 호출 (병원기본정보 + 진료과목코드)
    # 여기서는 데모용으로 최소 칼럼만 구성
    # 실전: 요양기관번호↔HPID 매칭 전략 수립 필요(주소·전화·상호명 매칭 fallback)
    return pd.DataFrame(columns=["name","tel","addr","obgyn_flag"])

# ----- 데이터 결합 -----
def merge_logic(df_em, df_hira):
    # 병원명·전화·주소 기반 fuzzy match 가능 (MVP는 병원명 포함 여부 우선)
    if df_em is None or df_em.empty:
        return pd.DataFrame()
    df_em["obgyn_flag"] = False
    if df_hira is not None and not df_hira.empty:
        em_names = df_em["dutyName"].astype(str)
        hira_names = set(map(str, df_hira.loc[df_hira["obgyn_flag"]==True, "name"]))
        df_em["obgyn_flag"] = em_names.apply(lambda x: any(h in x for h in hira_names))
    return df_em

# ----- 실행 -----
with st.spinner("실시간 데이터를 불러오는 중..."):
    # 간단 파싱: 입력 키워드에서 시/구 추정 (MVP는 시도/시군구 직접 입력 UI로 대체해도 OK)
    sido_guess = None
    sigungu_guess = keyword
    em_df = fetch_emergency_now(sido=sido_guess, sigungu=sigungu_guess, keyword=keyword)
    hira_df = fetch_hira_obgyn()
    df = merge_logic(em_df, hira_df)

    if only_obgyn:
        df = df[df["obgyn_flag"]==True]

    # 좌표 보정(없는 경우 지오코딩)
    lat_col, lon_col = "wgs84Lat", "wgs84Lon"
    if lat_col not in df.columns or lon_col not in df.columns:
        df[lat_col], df[lon_col] = None, None
    for i, row in df.iterrows():
        if pd.isna(row.get(lat_col)) or pd.isna(row.get(lon_col)):
            loc = geocode(row.get("dutyAddr"))
            if loc:
                df.at[i, lat_col], df.at[i, lon_col] = loc[0], loc[1]

# ----- 지도 -----
st.subheader("지도로 보기")
center = [37.5665, 126.9780]  # 서울시청 기본
if not df.empty and df[lat_col].notna().any():
    center = [df[lat_col].astype(float).mean(), df[lon_col].astype(float).mean()]

m = folium.Map(location=center, zoom_start=12)
def status_color(row):
    # 실시간 가용/혼잡 지표에 따라 색상 지정 (예: hvec/hvoc/hvcc)
    hv = str(row.get("hvec", ""))  # 예: 'Y'/'N'/'A'(정보없음)
    return {"Y":"green","N":"red"}.get(hv, "orange")

for _, r in df.iterrows():
    lat, lon = r.get(lat_col), r.get(lon_col)
    if pd.isna(lat) or pd.isna(lon):
        continue
    popup = folium.Popup(f"""
        <b>{r.get('dutyName','')}</b><br>
        주소: {r.get('dutyAddr','')}<br>
        응급실: {r.get('dutyTel3','-')}<br>
        가용여부(예): {r.get('hvec','-')} / 수술실: {r.get('hvoc','-')} / 중환자실: {r.get('hvcc','-')}<br>
        <a href="tel:{r.get('dutyTel3','')}" target="_blank">전화하기</a>
    """, max_width=350)
    folium.CircleMarker(
        location=[float(lat), float(lon)],
        radius=8,
        color=status_color(r),
        fill=True,
        fill_opacity=0.8,
        tooltip=r.get('dutyName','')
    ).add_child(popup).add_to(m)

st_folium(m, height=550)

# ----- 표 -----
st.subheader("목록")
show_cols = ["dutyName","dutyAddr","dutyTel3","hvec","hvoc","hvcc","obgyn_flag"]
st.dataframe(df[show_cols] if not df.empty else pd.DataFrame(columns=show_cols))

st.info("※ 분만 가능 여부는 산부인과 보유 여부를 기반으로 한 **추정**입니다. 실제 수용 가능 여부는 반드시 전화로 확인하세요. 응급상황은 119를 이용하십시오.")
