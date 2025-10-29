import streamlit as st
import random

# 🌈 페이지 설정
st.set_page_config(page_title="💞 아바타 소개팅 💞", page_icon="💘", layout="centered")

# 🎨 스타일 (CSS)
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #FFD6EC, #B5EAEA);
    font-family: 'Apple SD Gothic Neo', sans-serif;
    animation: bgmove 10s ease infinite;
    background-size: 300% 300%;
}
@keyframes bgmove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.title {
    text-align: center;
    font-size: 38px;
    color: #FF4D6D;
    text-shadow: 0 0 10px #fff;
    animation: fadeInDown 1.5s ease;
}

@keyframes fadeInDown {
    from {opacity: 0; transform: translateY(-30px);}
    to {opacity: 1; transform: translateY(0);}
}

.card {
    background: rgba(255, 255, 255, 0.4);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    margin: 15px;
    font-size: 20px;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# 💘 타이틀
st.markdown("<h1 class='title'>💞 아바타 소개팅 체험 💞</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>AI 아바타와 대화하며 나에게 맞는 인연을 찾아보세요 🌸</p>", unsafe_allow_html=True)

# 🧍‍♀️ 사용자 아바타 설정
st.markdown("<div class='card'>✨ 나의 아바타 설정 ✨</div>", unsafe_allow_html=True)
name = st.text_input("당신의 이름을 입력하세요", placeholder="예: 소연")
avatar = st.selectbox("아바타를 선택하세요", ["🐰 귀여운 토끼", "🐯 카리스마 호랑이", "🐼 순둥이 판다", "🦊 재치 있는 여우"])

# 💫 매칭 버튼
if st.button("💌 소개팅 시작하기 💌"):
    partner = random.choice(["🐶 다정한 강아지", "🐱 도도한 고양이", "🐻 듬직한 곰", "🦉 지적인 부엉이", "🐥 귀여운 병아리"])
    st.session_state["partner"] = partner
    st.session_state["chat_history"] = []
    st.success(f"매칭 성공! 🎉 당신의 소개팅 상대는 **{partner}** 입니다 💞")

# 💬 대화창
if "partner" in st.session_state:
    st.markdown(f"<div class='card'>💬 지금 대화 중인 상대: {st.session_state['partner']}</div>", unsafe_allow_html=True)
    partner_name = st.session_state["partner"]

    # 대화 기록 출력
    for role, message in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(message)

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력해보세요 💬"):
        st.session_state["chat_history"].append(("user", f"**{name if name else '나'} ({avatar})**: {prompt}"))
        st.chat_message("user").markdown(f"**{name if name else '나'} ({avatar})**: {prompt}")

        # 랜덤한 AI 반응 생성
        responses = [
            "ㅎㅎ 너 진짜 재밌다 😆",
            "그거 나도 좋아해!",
            "오늘 너 목소리(글)가 기분 좋게 들리네 ☺️",
            "혹시 주말에 뭐해? 😏",
            "너랑 얘기하니까 시간 가는 줄 모르겠다 💖"
        ]
        reply = random.choice(responses)
        st.session_state["chat_history"].append(("assistant", f"**{partner_name}**: {reply}"))
        st.chat_message("assistant").markdown(f"**{partner_name}**: {reply}")

# 🩷 푸터
st.markdown("""
<hr>
<p style='text-align:center; color:#666;'>✨ Made with ❤️ by 은채 ✨</p>
""", unsafe_allow_html=True)
