import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="민원 통계 분석기", layout="wide")

# 흰색 바탕의 깔끔한 디자인 적용
st.markdown("""
    <style>
    .main { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ 민원 데이터 전수 분석 시스템 (V3)")
st.write("Plotly를 사용하여 한글 깨짐 없이 전수 조사를 수행합니다.")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # 데이터 자동 분리 (콤마 대응)
    if len(df.columns) == 1 and ',' in str(df.columns[0]):
        col_names = str(df.columns[0]).split(',')
        df = df[df.columns[0]].str.split(',', expand=True)
        df.columns = col_names[:len(df.columns)]

    st.sidebar.header("📊 분석 설정")
    target_column = st.sidebar.selectbox("분석할 항목 선택", df.columns)

    if target_column:
        all_counts = df[target_column].value_counts().reset_index()
        all_counts.columns = [target_column, '건수']
        
        # 상위 10개 시각화용
        plot_data = all_counts.head(10)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"### 📈 {target_column} 시각화 (상위 10개)")
            # Plotly 막대 그래프 (한글 안 깨짐!)
            fig_bar = px.bar(plot_data, x=target_column, y='건수', 
                             color_discrete_sequence=['#4A90E2'],
                             template='plotly_white')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.write("### 🔢 전수 조사 통계 (전체)")
            # 200개든 뭐든 표로 깔끔하게 출력
            st.dataframe(all_counts, use_container_width=True, height=400, hide_index=True)

        st.divider()

        col3, col4 = st.columns(2)
        
        with col3:
            st.write(f"### 🍕 {target_column} 비율")
            # Plotly 파이 차트 (항목 이름 아주 잘 나옴!)
            fig_pie = px.pie(plot_data, names=target_column, values='건수',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col4:
            st.write(f"### 📉 {target_column} 변화 추이")
            # Plotly 꺾은선 그래프
            fig_line = px.line(all_counts.sort_values(by=target_column), 
                               x=target_column, y='건수', markers=True,
                               template='plotly_white')
            st.plotly_chart(fig_line, use_container_width=True)

        st.success(f"✅ 총 {len(df)}건의 데이터를 누락 없이 분석 완료했습니다.")