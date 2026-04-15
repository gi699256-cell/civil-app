# Excel 업로드 → 막대그래프 (Streamlit)

엑셀 파일(`.xlsx`, `.xls`)을 업로드하면 시트/컬럼을 선택해서 **막대그래프**를 그려주는 간단한 웹 앱입니다.

## 실행 방법 (Windows / PowerShell)

```powershell
cd "C:\Users\USER\OneDrive\Desktop\Exel_App"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## 사용 방법

- 엑셀 파일 업로드
- 시트 선택
- 막대그래프에 사용할 **X 컬럼(범주)**, **Y 컬럼(숫자)** 선택
- 필요하면 집계 방식(합계/평균/개수) 선택
- 막대 정렬/상위 N개/가로·세로 방향 설정

