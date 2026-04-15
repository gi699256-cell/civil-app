import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

# 한글 폰트 및 디자인 설정
def set_design():
    system_os = platform.system()
    if system_os == "Windows":
        plt.rc('font', family='Malgun Gothic')
    elif system_os == "Darwin":
        plt.rc('font', family='AppleGothic')
    else:
        plt.rc('font', family='NanumGothic')
    
    # 그래프 바탕색 흰색으로 깔끔하게 고정
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rc('axes', unicode_minus=False)

set_design()

st.set_page_config(page_title="민원 통계 분석기", layout="wide")
st.markdown("""
    <style>
    .main { background-color: white; }
    .stDataFrame { border: 1px solid #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ 민원 데이터 전수 분석 시스템")
st.write("모든 데이터를 분석하되, 시각화는 핵심 위주로 깔끔하게 출력합니다.")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # 데이터 자동 분리 (콤마 대응)
    if len(df.columns) == 1 and ',' in str(df.columns[0]):
        col_names = str(df.columns[0]).split(',')
        df = df[df.columns[0]].str.split(',', expand=True)
        df.columns = col_names[:len(df.columns)]

    st.sidebar.header("📊 분석 설정")
    target_column = st.sidebar.selectbox("분석할 항목 선택 (예: 민원유형, 처리상태)", df.columns)

    if target_column:
        # 전체 데이터 집계
        all_counts = df[target_column].value_counts()
        
        # 시각화용 데이터 (너무 많으면 상위 10개만, 적으면 전부)
        plot_counts = all_counts.head(10)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"### 📈 {target_column} 시각화 (상위 10개)")
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # 테두리 없애고 세련된 색상(SteelBlue) 사용
            plot_counts.plot(kind='bar', ax=ax, color='#4A90E2', width=0.7)
            
            # 격자선 제거 및 깔끔한 테두리 설정
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

        with col2:
            st.write("### 🔢 전수 조사 통계 (전체)")
            # 전체 데이터를 표로 보여줌 (200개든 뭐든 여기서 다 확인 가능)
            stat_df = all_counts.reset_index()
            stat_df.columns = [target_column, '건수']
            st.dataframe(stat_df, use_container_width=True, height=400)

        st.divider()

        col3, col4 = st.columns(2)
        
        with col3:
            st.write("### 🍕 항목별 비율 (Top 10)")
            fig_pie, ax_pie = plt.subplots()
            # 파이 차트 디자인 개선
            plot_counts.plot(kind='pie', ax=ax_pie, autopct='%1.1f%%', startangle=90, 
                             colors=plt.cm.Pastel1.colors, wedgeprops={'edgecolor': 'white'})
            ax_pie.set_ylabel("")
            st.pyplot(fig_pie)

        with col4:
            st.write("### 📉 변화 추이")
            fig_line, ax_line = plt.subplots()
            all_counts.sort_index().plot(kind='line', ax=ax_line, marker='o', color='#E67E22', linewidth=2)
            ax_line.grid(True, linestyle=':', alpha=0.5)
            st.pyplot(fig_line)

        st.success(f"✅ 총 {len(df)}건의 데이터를 누락 없이 분석하였습니다.")