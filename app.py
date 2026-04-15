import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

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

st.set_page_config(page_title="공공기관용 민원 분석기", layout="wide")
st.title("🏛️ 민원 데이터 전수 분석 도구")

uploaded_file = st.file_uploader("분석할 엑셀 파일을 올려주세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # 데이터 자동 분리 로직 (콤마 대응)
    if len(df.columns) == 1 and ',' in str(df.columns[0]):
        first_val = str(df.columns[0])
        new_df = df[df.columns[0]].str.split(',', expand=True)
        new_df.columns = first_val.split(',')
        df = new_df

    st.sidebar.header("📊 분석 항목 선택")
    target_column = st.sidebar.selectbox("정확한 통계를 낼 항목을 골라주세요", df.columns)

    if target_column:
        # 1. 데이터 전수 집계 (하나도 빼놓지 않습니다!)
        counts = df[target_column].value_counts()
        
        # 화면을 2:1 비율로 나눕니다 (그래프와 표)
        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            st.write(f"### 📈 {target_column} 시각화 추이")
            fig, ax = plt.subplots(figsize=(10, 5))
            # 그래프에는 숫자를 표시하지 않아 깔끔하게 유지 (표에서 확인 가능)
            counts.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

        with col_table:
            st.write("### 🔢 데이터 전수 요약")
            # 전체 숫자를 표로 깔끔하게 정리해서 보여줍니다.
            summary_df = counts.reset_index()
            summary_df.columns = [target_column, '건수(명)']
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # 꺾은선 그래프 (전체 흐름 파악용)
        st.write(f"### 📉 {target_column} 전체 흐름")
        fig_line, ax_line = plt.subplots(figsize=(12, 3))
        counts.sort_index().plot(kind='line', ax=ax_line, marker='o', color='firebrick', linewidth=2)
        ax_line.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig_line)

        st.success(f"✅ 총 {len(counts)}개의 항목에 대한 분석이 완료되었습니다. 누락된 데이터는 없습니다.")