from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Excel → Bar Chart",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


_BASE_CSS = """
<style>
  :root {
    --bg: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e5e7eb;
    --card: #ffffff;
    --shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    --radius: 14px;
  }

  .stApp {
    background: var(--bg);
    color: var(--text);
  }

  /* Make default containers feel like clean cards */
  div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    background: var(--card);
  }

  /* Headings spacing */
  h1, h2, h3 {
    letter-spacing: -0.02em;
  }

  /* Sidebar cleanliness */
  section[data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
  }

  /* Subtle helper text */
  .hint {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.35rem;
  }
</style>
"""

st.markdown(_BASE_CSS, unsafe_allow_html=True)


@dataclass(frozen=True)
class ChartConfig:
    x_col: str
    y_col: Optional[str]
    agg: str  # "sum" | "mean" | "count"
    chart_type: str  # "bar" | "pie"
    orientation: str  # "v" | "h"
    sort: str  # "none" | "asc" | "desc"
    top_n: int
    title: str


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def _safe_read_excel(uploaded: "st.runtime.uploaded_file_manager.UploadedFile") -> tuple[list[str], dict[str, pd.DataFrame]]:
    # Streamlit UploadedFile behaves like a BytesIO but can be read only once reliably.
    raw = uploaded.getvalue()
    bio = io.BytesIO(raw)
    xl = pd.ExcelFile(bio)
    sheets = xl.sheet_names
    frames: dict[str, pd.DataFrame] = {}
    for name in sheets:
        frames[name] = xl.parse(name)
    return sheets, frames


def _aggregate(df: pd.DataFrame, cfg: ChartConfig) -> pd.DataFrame:
    x = cfg.x_col
    if cfg.agg == "count" or not cfg.y_col:
        out = df.groupby(x, dropna=False).size().reset_index(name="value")
        out.rename(columns={x: "label"}, inplace=True)
        out["metric"] = "Count"
        return out

    y = cfg.y_col
    if cfg.agg == "sum":
        s = df.groupby(x, dropna=False)[y].sum(min_count=1)
        metric = f"Sum of {y}"
    else:
        s = df.groupby(x, dropna=False)[y].mean()
        metric = f"Mean of {y}"

    out = s.reset_index(name="value")
    out.rename(columns={x: "label"}, inplace=True)
    out["metric"] = metric
    return out


def _apply_sort_topn(df: pd.DataFrame, cfg: ChartConfig) -> pd.DataFrame:
    out = df.copy()
    if cfg.sort == "asc":
        out = out.sort_values("value", ascending=True, kind="mergesort")
    elif cfg.sort == "desc":
        out = out.sort_values("value", ascending=False, kind="mergesort")

    if cfg.top_n > 0 and len(out) > cfg.top_n:
        out = out.head(cfg.top_n) if cfg.sort != "asc" else out.tail(cfg.top_n)
    return out


def _format_value_labels(series: pd.Series) -> pd.Series:
    def _fmt(v: float) -> str:
        if pd.isna(v):
            return ""
        # Keep integer-like values clean, use 2 decimals only when needed.
        if abs(v - round(v)) < 1e-9:
            return f"{int(round(v)):,}"
        return f"{v:,.2f}"

    return series.apply(_fmt)


def _bar_figure(df: pd.DataFrame, cfg: ChartConfig):
    plot_df = df.copy()
    plot_df["value_label"] = _format_value_labels(plot_df["value"])
    bar_count = len(plot_df)
    dynamic_bargap = 0.25 if bar_count <= 20 else 0.45
    max_value = float(plot_df["value"].max()) if bar_count > 0 else 0.0
    min_value = float(plot_df["value"].min()) if bar_count > 0 else 0.0

    # Clean, professional Plotly defaults
    if cfg.orientation == "h":
        fig = px.bar(plot_df, x="value", y="label", orientation="h", title=cfg.title, text="value_label")
        margin = dict(l=16, r=110, t=60, b=16)
        chart_height = min(1600, max(460, 120 + bar_count * 32))
        x_axis_range = [min(0.0, min_value) * 1.1, max_value * 1.25 if max_value > 0 else 1.0]
        y_axis_range = None
    else:
        fig = px.bar(plot_df, x="label", y="value", title=cfg.title, text="value_label")
        margin = dict(l=16, r=24, t=95, b=22)
        chart_height = min(1100, max(500, 320 + bar_count * 10))
        x_axis_range = None
        y_axis_range = [min(0.0, min_value) * 1.1, max_value * 1.25 if max_value > 0 else 1.0]

    # Hide built-in text and draw our own annotations so labels are always visible.
    fig.update_traces(marker_color="#2563eb", text=None, cliponaxis=False)
    fig.update_layout(
        template="plotly_white",
        title=dict(x=0, xanchor="left", font=dict(size=20)),
        margin=margin,
        height=chart_height,
        bargap=dynamic_bargap,
        xaxis=dict(title=None, showgrid=True, gridcolor="#eef2f7", automargin=True),
        yaxis=dict(title=None, showgrid=False, automargin=True),
        font=dict(color="#0f172a"),
        hoverlabel=dict(bgcolor="white"),
        uniformtext_mode=False,
    )
    if x_axis_range is not None:
        fig.update_xaxes(range=x_axis_range)
    if y_axis_range is not None:
        fig.update_yaxes(range=y_axis_range)

    # Force black labels outside bars; use orientation-specific sizes for balance.
    label_font_h = dict(size=11, color="#000000", family="Arial, sans-serif")
    label_font_v = dict(size=20, color="#000000", family="Arial Black, Arial, sans-serif")
    if cfg.orientation == "h":
        span = max_value - min(0.0, min_value)
        offset = (span * 0.03) if span > 0 else 0.5
        for row in plot_df.itertuples(index=False):
            val = float(row.value)
            label_x = val + offset if val >= 0 else val - offset
            x_anchor = "left" if val >= 0 else "right"
            fig.add_annotation(
                x=label_x,
                y=row.label,
                text=row.value_label,
                showarrow=False,
                xanchor=x_anchor,
                yanchor="middle",
                font=label_font_h,
                align="left",
            )
    else:
        span = max_value - min(0.0, min_value)
        offset = (span * 0.04) if span > 0 else 0.5
        for row in plot_df.itertuples(index=False):
            val = float(row.value)
            label_y = val + offset if val >= 0 else val - offset
            y_anchor = "bottom" if val >= 0 else "top"
            fig.add_annotation(
                x=row.label,
                y=label_y,
                text=row.value_label,
                showarrow=False,
                xanchor="center",
                yanchor=y_anchor,
                font=label_font_v,
                align="center",
            )
    return fig


def _pie_figure(df: pd.DataFrame, cfg: ChartConfig):
    fig = px.pie(
        df,
        names="label",
        values="value",
        title=cfg.title,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont=dict(size=13, color="#0f172a", family="Arial, sans-serif"),
        marker=dict(line=dict(color="#ffffff", width=1.5)),
        sort=False,
    )
    fig.update_layout(
        template="plotly_white",
        title=dict(x=0, xanchor="left", font=dict(size=20)),
        margin=dict(l=20, r=20, t=60, b=20),
        height=620,
        showlegend=False,
        font=dict(color="#0f172a"),
        uniformtext_minsize=11,
        uniformtext_mode="hide",
    )
    return fig


def _download_buttons(source_df: pd.DataFrame, agg_df: pd.DataFrame):
    col_a, col_b = st.columns(2)
    with col_a:
        csv = source_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("원본 데이터 CSV 다운로드", data=csv, file_name="data.csv", mime="text/csv")
    with col_b:
        csv2 = agg_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("집계 결과 CSV 다운로드", data=csv2, file_name="chart_data.csv", mime="text/csv")


st.title("Excel 업로드 → 막대그래프")
st.markdown('<div class="hint">엑셀 파일을 업로드하고, 시트와 컬럼을 선택하면 바로 막대그래프를 생성합니다.</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "xls"])

if not uploaded:
    st.info("왼쪽에서 엑셀 파일을 업로드하세요.")
    st.stop()

try:
    sheet_names, frames_by_sheet = _safe_read_excel(uploaded)
except Exception as e:
    st.error("엑셀 파일을 읽는 중 오류가 발생했습니다. 파일이 손상되었거나 암호화되어 있을 수 있습니다.")
    st.exception(e)
    st.stop()

with st.sidebar:
    st.subheader("설정")
    sheet = st.selectbox("시트", options=sheet_names, index=0)

df0 = frames_by_sheet[sheet].copy()

if df0.empty:
    st.warning("선택한 시트에 데이터가 없습니다.")
    st.stop()

# Basic cleanup: keep column names as strings
df0.columns = [str(c) for c in df0.columns]

all_cols = list(df0.columns)
non_empty_cols = [c for c in all_cols if df0[c].notna().any()]
if not non_empty_cols:
    st.warning("데이터가 모두 비어있어 그래프를 만들 수 없습니다.")
    st.stop()

numeric_cols = [c for c in non_empty_cols if _is_numeric(df0[c])]
categorical_cols = [c for c in non_empty_cols if c not in numeric_cols]

default_x = (categorical_cols[0] if categorical_cols else non_empty_cols[0])
default_y = (numeric_cols[0] if numeric_cols else None)

with st.sidebar:
    x_col = st.selectbox("X (범주)", options=non_empty_cols, index=non_empty_cols.index(default_x))
    chart_type_ui = st.selectbox("그래프 종류", options=["막대그래프", "파이 차트"], index=0)

    agg = st.selectbox(
        "집계 방식",
        options=["합계", "평균", "개수"],
        index=0 if default_y else 2,
        help="X 컬럼 기준으로 Y를 집계합니다. Y가 없거나 숫자가 아니면 '개수'를 추천합니다.",
    )

    if agg == "개수":
        y_col = None
    else:
        y_choices = numeric_cols if numeric_cols else []
        if not y_choices:
            st.warning("숫자형 컬럼이 없어 '개수'로 전환합니다.")
            y_col = None
            agg = "개수"
        else:
            y_col = st.selectbox("Y (숫자)", options=y_choices, index=0 if default_y is None else y_choices.index(default_y))

    orientation = "세로"
    if chart_type_ui == "막대그래프":
        orientation = st.radio("방향", options=["세로", "가로"], horizontal=True, index=0)
    sort = st.selectbox("정렬", options=["없음", "값 큰 순", "값 작은 순"], index=1)
    top_n = st.slider("표시 개수 (Top N)", min_value=0, max_value=200, value=30, help="0이면 전체를 표시합니다.")
    title_default = "Bar Chart" if chart_type_ui == "막대그래프" else "Pie Chart"
    title = st.text_input("그래프 제목", value=title_default)

agg_key = {"합계": "sum", "평균": "mean", "개수": "count"}[agg]
chart_type_key = "bar" if chart_type_ui == "막대그래프" else "pie"
orientation_key = "v" if orientation == "세로" else "h"
sort_key = {"없음": "none", "값 큰 순": "desc", "값 작은 순": "asc"}[sort]

cfg = ChartConfig(
    x_col=x_col,
    y_col=y_col,
    agg=agg_key,
    chart_type=chart_type_key,
    orientation=orientation_key,
    sort=sort_key,
    top_n=int(top_n),
    title=title.strip() or ("Bar Chart" if chart_type_key == "bar" else "Pie Chart"),
)

# Validate selected columns
if cfg.x_col not in df0.columns:
    st.error("X 컬럼이 존재하지 않습니다. 다시 선택해 주세요.")
    st.stop()
if cfg.y_col and cfg.y_col not in df0.columns:
    st.error("Y 컬럼이 존재하지 않습니다. 다시 선택해 주세요.")
    st.stop()

# Prepare data
work = df0[[c for c in [cfg.x_col, cfg.y_col] if c is not None]].copy()
work[cfg.x_col] = work[cfg.x_col].astype("string").fillna("NA")
if cfg.y_col:
    work[cfg.y_col] = pd.to_numeric(work[cfg.y_col], errors="coerce")

agg_df = _aggregate(work, cfg)
agg_df = _apply_sort_topn(agg_df, cfg)

left, right = st.columns([1.55, 1], gap="large")

with left:
    if cfg.chart_type == "pie":
        st.subheader("파이 차트")
        pie_df = agg_df[agg_df["value"].notna() & (agg_df["value"] > 0)].copy()
        if pie_df.empty:
            st.warning("파이 차트는 0보다 큰 값이 필요합니다. 현재 조건으로는 표시할 데이터가 없습니다.")
        else:
            fig = _pie_figure(pie_df, cfg)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("막대그래프")
        fig = _bar_figure(agg_df, cfg)
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("미리보기")
    st.markdown('<div class="hint">원본 일부와 집계 결과를 확인할 수 있습니다.</div>', unsafe_allow_html=True)
    st.write("원본 (상위 50행)")
    st.dataframe(df0.head(50), use_container_width=True, height=240)
    st.write("그래프 데이터")
    st.dataframe(agg_df, use_container_width=True, height=240)
    _download_buttons(df0, agg_df)

