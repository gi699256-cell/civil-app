import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# 한글 폰트 설정 (Streamlit Cloud 환경 대응)
system_os = platform.system()
if system_os == "Windows":
    plt.rc('font', family='Malgun Gothic')
elif system_os == "Darwin":
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)

st.title("📊 민원 데이터 분석 통합 도구")
st.write("막대, 파이 차트에 이어 **꺾은선 그래프** 기능이 추가되었습니다!")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("### 📋 데이터 미리보기", df.head())

    columns = df.columns.tolist()
    target_column = st.sidebar.selectbox("분석할 컬럼을 선택하세요", columns)

    if target_column:
        counts = df[target_column].value_counts().sort_index()

        # 1. 막대 그래프
        st.write(f"### 📈 {target_column} 항목별 막대 그래프")
        fig_bar, ax_bar = plt.subplots()
        counts.plot(kind='bar', ax=ax_bar, color='skyblue', edgecolor='black')
        plt.xticks(rotation=45)
        st.pyplot(fig_bar)

        # 2. 파이 차트
        st.write(f"### 🍕 {target_column} 항목별 비율")
        fig_pie, ax_pie = plt.subplots()
        counts.plot(kind='pie', ax=ax_pie, autopct='%1.1f%%', startangle=90)
        ax_pie.set_ylabel("")
        st.pyplot(fig_pie)

        # 3. 꺾은선 그래프 (신규 추가!)
        st.write(f"### 📉 {target_column} 변화 추이 (꺾은선 그래프)")
        fig_line, ax_line = plt.subplots()
        counts.plot(kind='line', ax=ax_line, marker='o', color='green', linewidth=2)
        ax_line.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig_line)

        st.success("✅ 모든 그래프가 생성되었습니다! 이제 변화 추이도 확인해보세요.")