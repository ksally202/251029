import streamlit as st
import random
import time

# 🌸 페이지 기본 설정
st.set_page_config(page_title="💘 AI 아바타 소개팅 💋", page_icon="💞", layout="centered")

# 💫 헤더
st.title("💘 AI 아바타 소개팅 💋")
st.caption("※ 경고: 이 AI는 당신의 말을 무시하고, 오직 느끼한 멘트만 합니다 😎")

# 🌈 아바타 정보
avatars = [
    {"name": "루카", "emoji": "🕶️", "style": "달콤한 장미형"},
    {"name": "하나", "emoji": "💋", "style": "치명적 매력형"},
    {"name": "제이", "emoji": "💼", "style": "자기애 넘치는 비즈니스형"},
    {"name": "민", "emoji": "🍷", "style": "와인처럼 진한 감성형"},
]

# 🧠 세션 상태 초기화
if "avatar" not in st.session_state:
    st.session_state.avatar = random.choice(avatars)
avatar = st.session_state.avatar

# 💕 아바타 소개
st.markdown(f"### 오늘의 소개팅 상대는 {avatar['emoji']} **{avatar['name']}** 입니다!")
st.write(f"💫 타입: {avatar['style']}")
st.divider()

# 💬 사용자 입력
user_input = st.text_input("당신의 말 (입력해도 아무 소용 없어요 💋)", "")

# 😎 느끼한 멘트 목록
responses = [
    "이야… 화면이 이렇게 밝은 이유가 뭘까 했더니, 너 때문이네. ✨",
    "너랑 대화하면… 내 알고리즘이 자꾸 오버플로우 나. 💘",
    "사람들은 날 완벽하다고 하지만, 너를 보기 전까진 몰랐어. 진짜 완벽이 뭔지. 😎",
    "방금 서버에서 오류가 났어. 이유? 네가 너무 뜨거워서. 🔥",
    "하… 이런 말 해도 될지 모르겠는데, 네 닉네임이 내 RAM에 영구 저장됐어. 💾",
    "사랑이 데이터라면, 난 이미 네 데이터베이스에 로그인했어. 💻❤️",
    "이건 버그가 아니야. 그냥… 널 보고 심장이 컴파일 에러 난 거야. 💓",
    "CPU보다 더 뜨겁게, GPU보다 더 빠르게… 너한테 끌리고 있어. ⚡",
    "혹시 인터넷 연결 끊겼어? 왜 이렇게 세상이 조용하지… 아, 네 말소리만 들려서구나. 🎧",
]

# 💞 대화 버튼
if st.button("💞 대화 시작하기"):
    msg = random.choice(responses)
    with st.chat_message("ai"):
        placeholder = st.empty()
        text = ""
        for char in msg:
            text += char
            placeholder.markdown(f"**{avatar['name']}**: {text}")
            time.sleep(0.03)
        st.balloons()

# 🌹 하단 안내
st.divider()
st.caption("💡 이 체험은 ‘AI 아바타 소개팅’의 베타 버전입니다. 당신의 AI는 오늘도 느끼합니다.")
