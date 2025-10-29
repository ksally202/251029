import streamlit as st

st.title("은채의 첫번째 앱!")
st.write("배부르당")
st.write('https://naver.com')
st.link_button("네이버 바로가기", 'https://naver.com')

name = st.text_input('이름을 입력해주세요: ')
if st.button('환영인사'):
     st.write(name+'님 안녕하세요!')
    


st.error('오류!')
st.info('안녕!')
