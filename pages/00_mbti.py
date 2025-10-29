import streamlit as st

# 🎨 페이지 설정
st.set_page_config(
    page_title="🌟 MBTI 직업 추천소 🌟",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🌈 제목 영역
st.markdown("""
<h1 style='text-align:center; color:#FF69B4;'>
💫 나의 MBTI로 찾는 인생 직업 💫
</h1>
<p style='text-align:center; font-size:18px; color:#999;'>
🎯 당신의 성격 유형에 맞는 완벽한 직업을 찾아보세요! ✨
</p>
""", unsafe_allow_html=True)

# 🧩 MBTI 선택
mbti_list = [
    "INTJ 🧠", "INTP 🧩", "ENTJ 👑", "ENTP 💥",
    "INFJ 🌙", "INFP 🌸", "ENFJ 🌞", "ENFP 🌈",
    "ISTJ 📋", "ISFJ 🕊️", "ESTJ ⚙️", "ESFJ 💖",
    "ISTP 🧰", "ISFP 🎨", "ESTP 🏎️", "ESFP 🎤"
]

selected_mbti = st.selectbox("👉 당신의 MBTI를 선택하세요!", mbti_list)

# 💼 MBTI별 직업 추천 데이터
jobs = {
    "INTJ 🧠": ["데이터 과학자 📊", "전략 컨설턴트 🧭", "연구원 🔬"],
    "INTP 🧩": ["개발자 💻", "철학자 📚", "AI 엔지니어 🤖"],
    "ENTJ 👑": ["CEO 💼", "기획이사 🧠", "전략가 🎯"],
    "ENTP 💥": ["창업가 🚀", "마케터 📢", "혁신 디자이너 💡"],
    "INFJ 🌙": ["심리상담사 💬", "작가 ✍️", "사회운동가 ✊"],
    "INFP 🌸": ["예술가 🎨", "작사가 🎶", "교사 🍎"],
    "ENFJ 🌞": ["교육자 📖", "HR 전문가 🤝", "리더십 코치 🌟"],
    "ENFP 🌈": ["광고 기획자 📺", "여행 플래너 ✈️", "엔터테이너 🎭"],
    "ISTJ 📋": ["회계사 📚", "공무원 🏛️", "프로젝트 매니저 📅"],
    "ISFJ 🕊️": ["간호사 💉", "교사 🏫", "사회복지사 ❤️"],
    "ESTJ ⚙️": ["관리자 🧱", "경영 컨설턴트 💼", "프로젝트 디렉터 🏗️"],
    "ESFJ 💖": ["이벤트 플래너 🎉", "홍보 담당자 📣", "간호 관리자 🏥"],
    "ISTP 🧰": ["엔지니어 🔧", "파일럿 ✈️", "정비사 ⚙️"],
    "ISFP 🎨": ["패션 디자이너 👗", "사진작가 📷", "요리사 🍳"],
    "ESTP 🏎️": ["세일즈 전문가 💰", "스턴트맨 🎬", "스포츠 코치 ⚽"],
    "ESFP 🎤": ["가수 🎵", "배우 🎬", "유튜버 📹"]
}

# 🎁 결과 표시
if selected_mbti:
    st.markdown("---")
    st.markdown(f"<h2 style='text-align:center; color:#FF8C00;'>✨ {selected_mbti} 에게 어울리는 직업 ✨</h2>", unsafe_allow_html=True)
    
    for job in jobs[selected_mbti]:
        st.markdown(f"<p style='text-align:center; font-size:24px;'>🌟 {job}</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <hr>
    <div style='text-align:center; font-size:18px; color:#888;'>
    💬 자신의 MBTI를 친구들과 공유해보세요! 💞  
    <br>#MBTI #직업추천 #진로찾기 #행복한미래
    </div>
    """, unsafe_allow_html=True)

# 🌸 하단 푸터
st.markdown("""
<hr>
<p style='text-align:center; color:#999; font-size:14px;'>
✨ Made with ❤️ by [Your Name] ✨  
</p>
""", unsafe_allow_html=True)
