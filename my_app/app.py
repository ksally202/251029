# -*- coding: utf-8 -*-
import io
import math
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import os
from streamlit_js_eval import get_geolocation

# ------------------------------------------------------------
# 🌐 다국어 리소스
# ------------------------------------------------------------
LANGS = {
    "ko": "한국어",
    "en": "English",
    "fr": "Français",
    "zh": "中文",
}

I18N = {
    "title": {
        "ko": "🚑 임산부 응급 병원 찾기 (CSV + GPS)",
        "en": "🚑 Emergency Hospitals for Pregnant Users (CSV + GPS)",
        "fr": "🚑 Urgences pour femmes enceintes (CSV + GPS)",
        "zh": "🚑 孕妇急诊医院查询（CSV + GPS）",
    },
    "banner": {
        "ko": "🚨 긴급 상황 시, 가장 가까운 '받아줄' 병원을 한눈에!",
        "en": "🚨 In emergencies, see the nearest hospital likely to accept you!",
        "fr": "🚨 En urgence, trouvez l’hôpital le plus proche susceptible de vous accueillir !",
        "zh": "🚨 紧急时，一眼查看最可能接收的最近医院！",
    },
    "due_input": {
        "ko": "👶 예상 출산일을 선택하세요 (사전 대비 알림)",
        "en": "👶 Select your due date (preparation reminder)",
        "fr": "👶 Sélectionnez votre date d’accouchement prévue (rappel de préparation)",
        "zh": "👶 请选择预产期（事前准备提醒）",
    },
    "due_warn": {
        "ko": "⏰ 출산 D-{d}! 가까운 응급 병원 등록, 완료하셨나요?",
        "en": "⏰ D-{d} to delivery! Have you saved nearby emergency hospitals?",
        "fr": "⏰ J-{d} avant l’accouchement ! Avez-vous enregistré les hôpitaux d’urgence à proximité ?",
        "zh": "⏰ 距离分娩还有 D-{d} 天！是否已保存附近的急诊医院？",
    },
    "due_info": {
        "ko": "📅 출산까지 {d}일 남았어요. 미리 병원 위치를 확인해두면 마음이 한결 편해요 💕",
        "en": "📅 {d} days left. Check hospital locations in advance for peace of mind 💕",
        "fr": "📅 Il reste {d} jours avant l’accouchement. Vérifiez les hôpitaux à l’avance pour être sereine 💕",
        "zh": "📅 距离分娩还有 {d} 天。提前确认医院位置更安心 💕",
    },
    "calm": {
        "ko": "💗 심호흡 한 번, 괜찮아요. 가까운 병원을 차분히 안내해드릴게요.",
        "en": "💗 Take a breath—you’re okay. We’ll calmly guide you to nearby hospitals.",
        "fr": "💗 Respirez, tout va bien. Nous vous guidons calmement vers un hôpital proche.",
        "zh": "💗 深呼吸，没事的。我们会冷静地引导您前往附近医院。",
    },
    "gps_btn": {
        "ko": "현재 위치 가져오기 (브라우저 GPS)",
        "en": "Get my location (browser GPS)",
        "fr": "Obtenir ma position (GPS du navigateur)",
        "zh": "获取我的位置（浏览器GPS）",
    },
    "lat": {"ko": "위도", "en": "Latitude", "fr": "Latitude", "zh": "纬度"},
    "lon": {"ko": "경도", "en": "Longitude", "fr": "Longitude", "zh": "经度"},
    "radius": {
        "ko": "탐색 반경(km)",
        "en": "Search radius (km)",
        "fr": "Rayon de recherche (km)",
        "zh": "搜索半径（公里）",
    },
    "filter_birth": {
        "ko": "👶 분만 가능한 병원만 보기",
        "en": "👶 Show only hospitals with delivery service",
        "fr": "👶 Voir uniquement les hôpitaux avec service d’accouchement",
        "zh": "👶 仅显示可分娩的医院",
    },
    "register_btn": {
        "ko": "📍 나의 응급 병원 등록하기",
        "en": "📍 Save my emergency hospital",
        "fr": "📍 Enregistrer mon hôpital d’urgence",
        "zh": "📍 保存我的急诊医院",
    },
    "registered_ok": {
        "ko": "🎉 등록 완료! 훌륭해요 👏 언제든 확인할 수 있어요.",
        "en": "🎉 Saved! Great job 👏 You can check anytime.",
        "fr": "🎉 Enregistré ! Bravo 👏 Vous pouvez vérifier à tout moment.",
        "zh": "🎉 已保存！做得好 👏 随时可查看。",
    },
    "progress_text": {"ko": "준비 정도", "en": "Readiness", "fr": "Préparation", "zh": "准备程度"},
    "footer_119": {
        "ko": "📞 응급 상황이 의심되면 즉시 119로 연락하세요.",
        "en": "📞 If an emergency is suspected, call local emergency services immediately.",
        "fr": "📞 En cas d’urgence, appelez immédiatement les services d’urgence.",
        "zh": "📞 如遇紧急情况，请立即拨打当地急救电话。",
    },
}

def t(key, lang, **kwargs):
    s = I18N[key].get(lang, I18N[key]["en"])
    return s.format(**kwargs) if kwargs else s

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="Emergency Hospitals", layout="wide")

# ------------------------------------------------------------
# 🌐 언어 선택 버튼
# ------------------------------------------------------------
st.markdown("### 🌐 Language Selection")
if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"

col1, col2, col3, col4 = st.columns(4)
if col1.button("🇰🇷 한국어"): st.session_state["lang"] = "ko"
if col2.button("🇺🇸 English"): st.session_state["lang"] = "en"
if col3.button("🇫🇷 Français"): st.session_state["lang"] = "fr"
if col4.button("🇨🇳 中文"): st.session_state["lang"] = "zh"

lang = st.session_state["lang"]

# ------------------------------------------------------------
# 타이틀 + 배너
# ------------------------------------------------------------
st.title(t("title", lang))
st.markdown(
    f"""
    <div style='text-align:center; background-color:#FF4B4B; color:white;
                padding:14px; border-radius:12px; font-size:20px; font-weight:700;'>
        {t("banner", lang)}
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# 출산일 입력 + 심리 안정 메시지
# ------------------------------------------------------------
due_date = st.date_input(t("due_input", lang), datetime.date.today())
days_left = (due_date - datetime.date.today()).days
if days_left <= 30:
    st.warning(t("due_warn", lang, d=max(days_left, 0)))
else:
    st.info(t("due_info", lang, d=days_left))

st.markdown(
    f"""
    <div style='text-align:center; color:#555; font-size:16px; margin-top:6px;'>
        {t("calm", lang)}
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# ------------------------------------------------------------
# CSV 자동 로드
# ------------------------------------------------------------
CSV_PATH = "seoul_emergency_hospitals3.csv"
if os.path.exists(CSV_PATH):
    st.caption("📁 자동으로 CSV 파일을 불러왔어요.")
    hospitals = pd.read_csv(CSV_PATH, encoding="utf-8")
else:
    st.error("⚠️ CSV 파일을 찾을 수 없습니다. data 폴더에 넣어주세요.")
    st.stop()

st.success("✅ 병원 데이터 불러오기 성공!")

# ------------------------------------------------------------
# 거리 계산 함수
# ------------------------------------------------------------
def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ------------------------------------------------------------
# 위치 설정
# ------------------------------------------------------------
st.markdown("### 📍 " + t("gps_btn", lang))
if "user_lat" not in st.session_state:
    st.session_state["user_lat"] = 37.5665
    st.session_state["user_lon"] = 126.9780

col_a, col_b, col_c, col_d = st.columns(4)
if col_a.button(t("gps_btn", lang)):
    loc = get_geolocation()
    if loc and "coords" in loc:
        st.session_state["user_lat"] = loc["coords"]["latitude"]
        st.session_state["user_lon"] = loc["coords"]["longitude"]

st.session_state["user_lat"] = col_b.number_input(t("lat", lang), value=st.session_state["user_lat"], format="%.6f")
st.session_state["user_lon"] = col_c.number_input(t("lon", lang), value=st.session_state["user_lon"], format="%.6f")
radius_km = col_d.slider(t("radius", lang), 2, 30, 10)

user_lat = st.session_state["user_lat"]
user_lon = st.session_state["user_lon"]

# ------------------------------------------------------------
# 가상 병상 데이터 생성
# ------------------------------------------------------------
np.random.seed(42)
hospitals["대기인원"] = np.random.randint(0, 31, size=len(hospitals))
hospitals["입원가능병상"] = np.random.randint(0, 21, size=len(hospitals))
hospitals["분만가능"] = np.random.choice([True, False], size=len(hospitals), p=[0.3, 0.7])

available_hospitals = hospitals[hospitals["입원가능병상"] > 0].copy()
available_hospitals["distance_km"] = available_hospitals.apply(
    lambda r: calc_distance(user_lat, user_lon, float(r["병원위도"]), float(r["병원경도"])), axis=1
)
available_hospitals = available_hospitals.sort_values("distance_km").reset_index(drop=True)

# ------------------------------------------------------------
# ✅ 필터: 분만 가능한 병원만 보기
# ------------------------------------------------------------
only_birth = st.checkbox(t("filter_birth", lang))
if only_birth:
    available_hospitals = available_hospitals[available_hospitals["분만가능"] == True]

# ------------------------------------------------------------
# 지도 색상 (대기인원 기준)
# ------------------------------------------------------------
def wait_color(wait):
    max_wait = 30
    ratio = min(wait / max_wait, 1)
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    return [r, g, 0]

available_hospitals["color"] = available_hospitals["대기인원"].apply(wait_color)

# ------------------------------------------------------------
# 지도 시각화
# ------------------------------------------------------------
hospital_layer = pdk.Layer(
    "ScatterplotLayer",
    data=available_hospitals,
    get_position="[병원경도, 병원위도]",
    get_radius=80,
    get_fill_color="color",
    pickable=True,
)

me_df = pd.DataFrame([{"lon": user_lon, "lat": user_lat, "name": "내 위치"}])
me_layer = pdk.Layer(
    "ScatterplotLayer",
    data=me_df,
    get_position="[lon, lat]",
    get_radius=120,
    get_fill_color=[0, 0, 255],
)

layers = [hospital_layer, me_layer]
tooltip = {
    "html": "<b>{병원명}</b><br/>거리: {distance_km:.2f} km<br/>대기인원: {대기인원}<br/>입원가능병상: {입원가능병상}<br/>분만가능: {분만가능}",
    "style": {"backgroundColor": "white", "color": "black"},
}
st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=12), tooltip=tooltip))

# ------------------------------------------------------------
# 표 출력
# ------------------------------------------------------------
st.markdown("### 🏥 입원 가능 병상 있는 병원 (대기인원 기준)")
view_cols = ["병원명", "distance_km", "대기인원", "입원가능병상", "분만가능"]
st.dataframe(available_hospitals[view_cols].head(50), use_container_width=True)

# ------------------------------------------------------------
# 병원 등록(게임화)
# ------------------------------------------------------------
col1, col2 = st.columns([1, 3])
if col1.button(t("register_btn", lang)):
    st.session_state["registered"] = True
    st.balloons()
    st.success(t("registered_ok", lang))
st.progress(100 if st.session_state.get("registered") else 40, text=t("progress_text", lang))

# ------------------------------------------------------------
# 하단 안내
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style='text-align:center; color:#444; font-size:16px; margin-top:10px;'>
        {t("footer_119", lang)} &nbsp;&nbsp; <a href="tel:119">[119]</a>
    </div>
    """,
    unsafe_allow_html=True
)
