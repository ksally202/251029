# -*- coding: utf-8 -*-
import io
import math
import datetime
import pandas as pd
import streamlit as st
import pydeck as pdk
from streamlit_js_eval import get_geolocation

# ------------------------------------------------------------
# 다국어 리소스
# ------------------------------------------------------------
LANGS = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh": "中文",
    "fr": "Français",
    "vi": "Tiếng Việt",
}

I18N = {
    "title": {
        "ko": "🚑 임산부 응급 병원 찾기 (CSV + GPS)",
        "en": "🚑 Emergency Hospitals for Pregnant Users (CSV + GPS)",
        "ja": "🚑 妊婦のための救急病院検索（CSV + GPS）",
        "zh": "🚑 孕妇急诊医院查询（CSV + GPS）",
        "fr": "🚑 Urgences pour femmes enceintes (CSV + GPS)",
        "vi": "🚑 Bệnh viện cấp cứu cho bà bầu (CSV + GPS)",
    },
    "banner": {
        "ko": "🚨 긴급 상황 시, 가장 가까운 '받아줄' 병원을 한눈에!",
        "en": "🚨 In emergencies, see the nearest hospital likely to accept you!",
        "ja": "🚨 緊急時、受け入れ可能性の高い最寄り病院をすぐ確認！",
        "zh": "🚨 紧急时，一眼查看最可能接收的最近医院！",
        "fr": "🚨 En urgence, trouvez l’hôpital le plus proche susceptible de vous accueillir !",
        "vi": "🚨 Khẩn cấp: xem ngay bệnh viện gần nhất có khả năng tiếp nhận!",
    },
    "due_input": {
        "ko": "👶 예상 출산일을 선택하세요 (사전 대비 알림)",
        "en": "👶 Select your due date (preparation reminder)",
        "ja": "👶 出産予定日を選択（事前準備リマインダー）",
        "zh": "👶 请选择预产期（事前准备提醒）",
        "fr": "👶 Sélectionnez la date prévue d’accouchement (rappel de préparation)",
        "vi": "👶 Chọn ngày dự sinh (nhắc nhở chuẩn bị)",
    },
    "due_warn": {
        "ko": "⏰ 출산 D-{d}! 가까운 응급 병원 등록, 완료하셨나요?",
        "en": "⏰ D-{d} to delivery! Have you saved nearby emergency hospitals?",
        "ja": "⏰ 出産までD-{d}！近くの救急病院を登録しましたか？",
        "zh": "⏰ 距离分娩还有 D-{d}！是否已保存附近的急诊医院？",
        "fr": "⏰ J-{d} avant l’accouchement ! Avez-vous enregistré les hôpitaux d’urgence à proximité ?",
        "vi": "⏰ Còn D-{d} đến ngày sinh! Bạn đã lưu bệnh viện cấp cứu gần chưa?",
    },
    "due_info": {
        "ko": "📅 출산까지 {d}일 남았어요. 미리 병원 위치를 확인해두면 마음이 한결 편해요 💕",
        "en": "📅 {d} days left. Check hospital locations in advance for peace of mind 💕",
        "ja": "📅 出産まであと {d} 日。事前に病院位置を確認しておくと安心です 💕",
        "zh": "📅 距离分娩还有 {d} 天。提前确认医院位置更安心 💕",
        "fr": "📅 Il reste {d} jours. Vérifiez les hôpitaux à l’avance pour être serein 💕",
        "vi": "📅 Còn {d} ngày. Kiểm tra sẵn vị trí bệnh viện để yên tâm hơn 💕",
    },
    "calm": {
        "ko": "💗 심호흡 한 번, 괜찮아요. 가까운 병원을 차분히 안내해드릴게요.",
        "en": "💗 Take a breath—you’re okay. We’ll calmly guide you to nearby hospitals.",
        "ja": "💗 深呼吸して、大丈夫。近くの病院へ落ち着いてご案内します。",
        "zh": "💗 深呼吸，没事的。我们会冷静地引导您前往附近医院。",
        "fr": "💗 Respirez, tout va bien. Nous vous guidons calmement vers l’hôpital proche.",
        "vi": "💗 Hít thở sâu, ổn cả. Ứng dụng sẽ hướng dẫn bạn đến bệnh viện gần nhất.",
    },
    "uploader": {
        "ko": "📂 응급실/병원 위치 CSV 업로드 (위도/경도 또는 병원위도/병원경도 포함)",
        "en": "📂 Upload hospitals CSV (must contain lat/lon or hospital-lat/hospital-lon columns)",
        "ja": "📂 病院CSVをアップロード（緯度/経度または病院緯度/病院経度が必要）",
        "zh": "📂 上传医院CSV（需包含纬度/经度或医院纬度/医院经度）",
        "fr": "📂 Importer un CSV d’hôpitaux (colonnes lat/lon nécessaires)",
        "vi": "📂 Tải CSV bệnh viện (cần có cột vĩ độ/kinh độ)",
    },
    "need_csv": {
        "ko": "CSV를 업로드하면 병원 목록을 보여드릴게요. (lat/lon 또는 위도/경도/병원위도/병원경도 컬럼 필수)",
        "en": "Upload a CSV to see hospitals. (lat/lon or Korean columns required)",
        "ja": "CSVをアップロードすると病院一覧を表示します（緯度/経度の列が必須）",
        "zh": "上传CSV以查看医院列表（需要经纬度列）",
        "fr": "Importez un CSV pour afficher les hôpitaux (lat/lon requis).",
        "vi": "Tải CSV để xem danh sách bệnh viện (cần cột vĩ/kinh độ).",
    },
    "encoding_ok": {
        "ko": "✅ CSV 인코딩 자동 감지 성공: {enc}",
        "en": "✅ CSV encoding detected: {enc}",
        "ja": "✅ CSVエンコーディングを検出: {enc}",
        "zh": "✅ 检测到CSV编码：{enc}",
        "fr": "✅ Encodage CSV détecté : {enc}",
        "vi": "✅ Đã nhận diện mã hóa CSV: {enc}",
    },
    "encoding_fail": {
        "ko": "❌ CSV 인코딩을 읽지 못했습니다. (UTF-8/CP949/EUC-KR/LATIN1 시도 실패)",
        "en": "❌ Failed to read CSV encoding (tried UTF-8/CP949/EUC-KR/LATIN1).",
        "ja": "❌ CSVの文字コードを読み取れませんでした。",
        "zh": "❌ 无法识别CSV编码。",
        "fr": "❌ Impossible de lire l’encodage du CSV.",
        "vi": "❌ Không đọc được mã hóa CSV.",
    },
    "loaded": {
        "ko": "✅ 병원 데이터 불러오기 성공!",
        "en": "✅ Hospitals data loaded successfully!",
        "ja": "✅ 病院データを読み込みました！",
        "zh": "✅ 医院数据载入成功！",
        "fr": "✅ Données des hôpitaux chargées !",
        "vi": "✅ Đã tải dữ liệu bệnh viện!",
    },
    "need_latlon": {
        "ko": "위도/경도 컬럼을 찾지 못했습니다. CSV에 'lat/lon' 또는 '위도/경도' 혹은 '병원위도/병원경도' 컬럼이 필요해요.",
        "en": "Latitude/longitude columns not found. CSV must have 'lat/lon' or equivalent.",
        "ja": "緯度/経度の列が見つかりません。CSVにlat/lon等が必要です。",
        "zh": "未找到经纬度列。CSV需包含'lat/lon'或等效列。",
        "fr": "Colonnes latitude/longitude introuvables dans le CSV.",
        "vi": "Thiếu cột vĩ độ/kinh độ trong CSV.",
    },
    "gps_btn": {
        "ko": "현재 위치 가져오기 (브라우저 GPS)",
        "en": "Get my location (browser GPS)",
        "ja": "現在地取得（ブラウザGPS）",
        "zh": "获取我的位置（浏览器GPS）",
        "fr": "Obtenir ma position (GPS du navigateur)",
        "vi": "Lấy vị trí của tôi (GPS trình duyệt)",
    },
    "lat": {"ko": "위도", "en": "Latitude", "ja": "緯度", "zh": "纬度", "fr": "Latitude", "vi": "Vĩ độ"},
    "lon": {"ko": "경도", "en": "Longitude", "ja": "経度", "zh": "经度", "fr": "Longitude", "vi": "Kinh độ"},
    "radius": {
        "ko": "탐색 반경(km)",
        "en": "Search radius (km)",
        "ja": "検索半径（km）",
        "zh": "搜索半径（公里）",
        "fr": "Rayon de recherche (km)",
        "vi": "Bán kính tìm kiếm (km)",
    },
    "register_btn": {
        "ko": "📍 나의 응급 병원 등록하기",
        "en": "📍 Save my emergency hospital",
        "ja": "📍 マイ救急病院を登録",
        "zh": "📍 保存我的急诊医院",
        "fr": "📍 Enregistrer mon hôpital d’urgence",
        "vi": "📍 Lưu bệnh viện khẩn cấp của tôi",
    },
    "registered_ok": {
        "ko": "🎉 등록 완료! 훌륭해요 👏 언제든 확인할 수 있어요.",
        "en": "🎉 Saved! Great job 👏 You can check anytime.",
        "ja": "🎉 登録完了！素晴らしい 👏 いつでも確認できます。",
        "zh": "🎉 已保存！做得好 👏 随时可查看。",
        "fr": "🎉 Enregistré ! Bravo 👏 Vous pouvez vérifier à tout moment.",
        "vi": "🎉 Đã lưu! Tuyệt vời 👏 Bạn có thể xem bất cứ lúc nào.",
    },
    "progress_text": {
        "ko": "준비 정도",
        "en": "Readiness",
        "ja": "準備度",
        "zh": "准备程度",
        "fr": "Préparation",
        "vi": "Mức sẵn sàng",
    },
    "table_title": {
        "ko": "🏥 가까운 병원 목록 (가까운 순)",
        "en": "🏥 Nearby hospitals (sorted by distance)",
        "ja": "🏥 近くの病院（距離順）",
        "zh": "🏥 附近医院（按距离排序）",
        "fr": "🏥 Hôpitaux proches (tri par distance)",
        "vi": "🏥 Bệnh viện gần (theo khoảng cách)",
    },
    "map_title": {
        "ko": "🗺️ 지도 보기",
        "en": "🗺️ Map",
        "ja": "🗺️ 地図",
        "zh": "🗺️ 地图",
        "fr": "🗺️ Carte",
        "vi": "🗺️ Bản đồ",
    },
    "tel": {"ko": "전화", "en": "Call", "ja": "電話", "zh": "电话", "fr": "Appeler", "vi": "Gọi"},
    "route": {"ko": "길찾기", "en": "Directions", "ja": "経路", "zh": "路线", "fr": "Itinéraire", "vi": "Chỉ đường"},
    "footer_119": {
        "ko": "📞 응급 상황이 의심되면 즉시 119로 연락하세요.",
        "en": "📞 If an emergency is suspected, call local emergency services immediately.",
        "ja": "📞 緊急が疑われる場合は、直ちに緊急通報してください。",
        "zh": "📞 如遇紧急情况，请立即拨打当地急救电话。",
        "fr": "📞 En cas d’urgence, appelez immédiatement les services d’urgence.",
        "vi": "📞 Nghi ngờ khẩn cấp, hãy gọi ngay số cấp cứu địa phương.",
    },
}

def t(key, lang, **kwargs):
    s = I18N[key][lang]
    return s.format(**kwargs) if kwargs else s

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="Emergency Hospitals", layout="wide")

# ------------------------------------------------------------
# 🌐 언어 선택 버튼 (가로 6버튼)
# ------------------------------------------------------------
st.markdown("### 🌐 Language")
if "lang" not in st.session_state:
    st.session_state["lang"] = "ko"

col1, col2, col3, col4, col5, col6 = st.columns(6)
if col1.button("🇰🇷 한국어"):
    st.session_state["lang"] = "ko"
if col2.button("🇺🇸 English"):
    st.session_state["lang"] = "en"
if col3.button("🇯🇵 日本語"):
    st.session_state["lang"] = "ja"
if col4.button("🇨🇳 中文"):
    st.session_state["lang"] = "zh"
if col5.button("🇫🇷 Français"):
    st.session_state["lang"] = "fr"
if col6.button("🇻🇳 Tiếng Việt"):
    st.session_state["lang"] = "vi"

lang = st.session_state["lang"]

# ------------------------------------------------------------
# 타이틀/배너
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
# D-30 안내 + 심리 안정
# ------------------------------------------------------------
with st.container():
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
# 유틸 함수
# ------------------------------------------------------------
def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def coerce_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "").str.strip(), errors="coerce")

def guess_columns(df: pd.DataFrame) -> dict:
    def pick(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None
    return {
        "lat":  pick(["lat", "위도", "병원위도", "Latitude", "latitude", "Y", "y"]),
        "lon":  pick(["lon", "경도", "병원경도", "Longitude", "longitude", "X", "x"]),
        "name": pick(["name", "병원명", "기관명", "기관名", "기관명(국문)", "요양기관명"]),
        "tel":  pick(["tel", "전화", "전화번호", "대표전화", "代表電話", "응급전화", "응급실전화"]),
        "addr": pick(["addr", "주소", "도로명주소", "지번주소", "住所"]),
    }

def add_badge(row) -> str:
    name = str(row.get("name", ""))
    if ("응급실" in name) or ("종합병원" in name) or ("Emergency" in name) or ("Hospital" in name):
        return "🏅"
    if float(row.get("distance_km", 999)) < 3:
        return "⭐"
    return ""

def naver_maps_link(lat, lon, name, lang_code) -> str:
    label = I18N["route"][lang_code]
    safe_name = str(name).replace(" ", "")
    return f"[{label}](https://map.naver.com/v5/directions/-/-/{lon},{lat},{safe_name})"

# ------------------------------------------------------------
# CSV 업로더 (인코딩 자동 감지)
# ------------------------------------------------------------
uploaded_file = st.file_uploader(I18N["uploader"][lang], type=["csv"])
if not uploaded_file:
    st.info(I18N["need_csv"][lang])
    st.stop()

file_bytes = uploaded_file.read()
hospitals = None
for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"):
    try:
        hospitals = pd.read_csv(io.BytesIO(file_bytes), encoding=enc)
        st.caption(I18N["encoding_ok"][lang].format(enc=enc))
        break
    except UnicodeDecodeError:
        continue
if hospitals is None:
    st.error(I18N["encoding_fail"][lang])
    st.stop()

st.success(I18N["loaded"][lang])
st.dataframe(hospitals.head(), use_container_width=True)

# ------------------------------------------------------------
# 컬럼 자동 인식 + 좌표 정리
# ------------------------------------------------------------
colmap = guess_columns(hospitals)
if not colmap["lat"] or not colmap["lon"]:
    st.error(I18N["need_latlon"][lang])
    st.stop()

hospitals = hospitals.rename(columns={
    colmap["lat"]: "lat",
    colmap["lon"]: "lon",
    **({colmap["name"]: "name"} if colmap["name"] else {}),
    **({colmap["tel"]: "tel"} if colmap["tel"] else {}),
    **({colmap["addr"]: "addr"} if colmap["addr"] else {}),
})
hospitals["lat"] = coerce_float(hospitals["lat"])
hospitals["lon"] = coerce_float(hospitals["lon"])
hospitals = hospitals.dropna(subset=["lat", "lon"]).reset_index(drop=True)

# ------------------------------------------------------------
# 현재 위치 (GPS + 수동 입력)
# ------------------------------------------------------------
st.markdown("### 🌍")
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

cols = st.columns(4)
if cols[0].button(I18N["gps_btn"][lang]):
    loc = get_geolocation()      # HTTPS + 권한 필요, 첫 호출에서 None 가능
    if loc and isinstance(loc, dict) and "coords" in loc:
        st.session_state.user_lat = float(loc["coords"]["latitude"])
        st.session_state.user_lon = float(loc["coords"]["longitude"])

st.session_state.user_lat = cols[1].number_input(
    I18N["lat"][lang], value=st.session_state.user_lat if st.session_state.user_lat else 37.5665, format="%.6f"
)
st.session_state.user_lon = cols[2].number_input(
    I18N["lon"][lang], value=st.session_state.user_lon if st.session_state.user_lon else 126.9780, format="%.6f"
)
radius_km = cols[3].slider(I18N["radius"][lang], 2, 30, 10)

user_lat = float(st.session_state.user_lat)
user_lon = float(st.session_state.user_lon)

# ------------------------------------------------------------
# 거리 계산 + 반경 필터 + 링크/뱃지
# ------------------------------------------------------------
hospitals["distance_km"] = hospitals.apply(
    lambda r: calc_distance(user_lat, user_lon, float(r["lat"]), float(r["lon"])),
    axis=1
)

result = hospitals[hospitals["distance_km"] <= radius_km].copy()
# 다국어 링크 라벨
call_label = I18N["tel"][lang]
route_label = I18N["route"][lang]

if "tel" in result.columns:
    result[call_label] = result["tel"].apply(
        lambda x: f"[{call_label}](tel:{str(x).strip()})" if pd.notna(x) and str(x).strip() else ""
    )
else:
    result[call_label] = ""

result[route_label] = result.apply(lambda r: naver_maps_link(r["lat"], r["lon"], str(r.get("name", "Hospital")), lang), axis=1)
result["badge"] = result.apply(add_badge, axis=1)
result["display_name"] = result["badge"] + " " + result.get("name", "").astype(str)
result = result.sort_values(["distance_km"]).reset_index(drop=True)

# ------------------------------------------------------------
# 게임화: 나의 응급 병원 등록
# ------------------------------------------------------------
colA, colB = st.columns([1,3])
if colA.button(I18N["register_btn"][lang]):
    st.session_state["registered"] = True
    st.balloons()
    st.success(I18N["registered_ok"][lang])
st.progress(100 if st.session_state.get("registered") else 40, text=I18N["progress_text"][lang])

# ------------------------------------------------------------
# 결과 표
# ------------------------------------------------------------
st.markdown(f"### {I18N['table_title'][lang]}")
base_cols = ["display_name","addr","tel","distance_km","lat","lon"]
show_cols = [c for c in base_cols if c in result.columns]
for extra in [call_label, route_label]:
    if extra in result.columns and extra not in show_cols:
        show_cols.insert(2, extra)
st.dataframe(result[show_cols].head(100), use_container_width=True)

# ------------------------------------------------------------
# 지도 (pydeck)
# ------------------------------------------------------------
st.markdown(f"### {I18N['map_title'][lang]}")
layers = []

hospital_layer = pdk.Layer(
    "ScatterplotLayer",
    data=result,
    get_position="[lon, lat]",      # [longitude, latitude]
    get_radius=80,
    pickable=True,
    radius_min_pixels=4,
    radius_max_pixels=24,
    auto_highlight=True,
)
text_layer = pdk.Layer(
    "TextLayer",
    data=result.head(30),
    get_position="[lon, lat]",
    get_text="display_name" if "display_name" in result.columns else ("name" if "name" in result.columns else "'Hospital'"),
    get_size=12,
    get_alignment_baseline="'bottom'",
)
me_df = pd.DataFrame([{"lon": user_lon, "lat": user_lat, "name": "Me"}])
me_dot = pdk.Layer("ScatterplotLayer", data=me_df, get_position="[lon, lat]", get_radius=120, pickable=False,
                   radius_min_pixels=6, radius_max_pixels=20)
me_halo = pdk.Layer("ScatterplotLayer", data=me_df, get_position="[lon, lat]", get_radius=300, pickable=False,
                    opacity=0.15, radius_min_pixels=12, radius_max_pixels=60)
layers += [hospital_layer, text_layer, me_dot, me_halo]

view_state = pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=12)
tooltip = {"html": "<b>{display_name}</b><br/>{addr}<br/>dist: {distance_km} km<br/>{tel}",
           "style": {"backgroundColor": "white", "color": "black"}}
st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip=tooltip, map_style=None),
                use_container_width=True)

# 하단 안내
st.markdown(
    f"""
    <div style='text-align:center; color:#444; font-size:16px; margin-top:10px;'>
        {I18N["footer_119"][lang]} &nbsp;&nbsp; <a href="tel:119">[119]</a>
    </div>
    """,
    unsafe_allow_html=True
)
