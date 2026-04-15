Lee님, 아까 복사하실 때 첫 줄이 조금 겹친 것 같아요! 그대로 붙여넣으셔도 되지만, 더 확실하게 작동하도록 제가 줄 바꿈을 깔끔하게 정리해 드릴게요.

아래 상자 안에 있는 내용을 전부 복사해서 app.py에 붙여넣으시면 됩니다.

💻 app.py에 넣을 최종 코드 (정리된 버전)
Python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# 폰트 설정 (더 확실하게!)
def set_korean_font():
    system_os = platform.system()
    if system_os == "Windows":
        plt.rc('font', family='Malgun Gothic')
    elif system_os == "Darwin":
        plt.rc('font', family='AppleGothic')
    else:
        plt.rc('font', family='NanumGothic')
    plt.rc('axes', unicode_minus=False)

set_korean_font()

st.set_page_config(page_title="깔끔한 민원 분석기", layout="wide")
st.title("✨ 깔끔한 민원 데이터 분석 도구")

uploaded_file = st.file_uploader("분석할 엑셀 파일을 올려주세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # 1. 데이터 정리: 컬럼명에 공백이 있으면 제거
    df.columns = [str(c).strip() for c in df.columns]
    
    st.sidebar.header("📊 분석 설정")
    target_column = st.sidebar.selectbox("딱 하나의 항목만 선택하세요", df.columns)

    if target_column:
        # 데이터가 너무 많으면 상위 15개만 추출 (지저분함 방지)
        counts = df[target_column].value_counts()
        if len(counts) > 15:
            st.warning(f"⚠️ 항목이 너무 많아 상위 15개만 표시합니다. (전체 {len(counts)}개)")
            counts = counts.head(15)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"### 📈 {target_column} TOP 15")
            fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
            counts.plot(kind='bar', ax=ax_bar, color='#4A90E2', edgecolor='white')
            plt.xticks(rotation=45, ha='right') # 글자를 대각선으로 눕혀서 안 겹치게!
            st.pyplot(fig_bar)

        with col2:
            st.write(f"### 🍕 {target_column} 비율")
            fig_pie, ax_pie = plt.subplots(figsize=(10, 6))
            counts.plot(kind='pie', ax=ax_pie, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax_pie.set_ylabel("")
            st.pyplot(fig_pie)

        # 3. 꺾은선 그래프
        st.write(f"### 📉 {target_column} 변화 추이")
        fig_line, ax_line = plt.subplots(figsize=(12, 4))
        counts.sort_index().plot(kind='line', ax=ax_line, marker='o', color='#F5A623', linewidth=3)
        ax_line.grid(True, linestyle=':', alpha=0.6)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig_line)