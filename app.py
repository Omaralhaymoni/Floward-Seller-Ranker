import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO, StringIO

st.set_page_config(page_title="Best Seller Ranker", layout="wide")
st.markdown("""
<style>
:root{
  --bg: #00313C;            /* deep teal background */
  --text: #F0E9E0;          /* soft golden beige font */
  --muted: #e6d5cc;
  --border: rgba(241,203,182,.25);
  --card: #012a33;
  --accent: #F0E9E0;        /* same golden beige for accents */
  --shadow: 0 8px 24px rgba(0,0,0,.25);
  --radius: 16px;
}

/* Backgrounds */
html, body, [data-testid="stAppViewContainer"]{
  background:var(--bg)!important;
  color:var(--text)!important;
}
section[data-testid="stSidebar"]{
  background:var(--bg)!important; color:var(--text)!important;
  border-right:1px solid var(--border);
}
section[data-testid="stSidebar"] *{ color:var(--text)!important; }

/* Inputs */
.stTextInput input, .stDateInput input, .stNumberInput input, .stTextArea textarea {
  background: var(--card)!important;
  color: var(--text)!important;
  border: 1px solid var(--border)!important;
  border-radius: 12px;
}

/* Dropdowns closed */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
  background: var(--accent) !important;   
  color: var(--bg) !important;              
  border-radius: 12px;
  font-weight: 600;
}
.stSelectbox div[data-baseweb="select"] *,
.stMultiSelect div[data-baseweb="select"] * {
  color: var(--bg) !important;
  fill: var(--bg) !important;
}

/* Typing field */
.stSelectbox input, .stMultiSelect input { color: var(--bg) !important; }

/* Dropdown menu open */
[data-baseweb="popover"] [role="listbox"]{
  background: var(--bg) !important;   
  color: var(--text) !important;    
  border: 1px solid var(--border) !important;
}
[data-baseweb="popover"] [role="option"]{ color: var(--text) !important; }
[data-baseweb="popover"] [role="option"][aria-selected="true"]{
  background: rgba(241,203,182,.15) !important;
  color: var(--text) !important;
}

/* Multiselect chips */
[data-baseweb="tag"]{
  background: transparent !important;
  border: 1px solid var(--bg) !important;
  color: var(--bg) !important;
}
[data-baseweb="tag"] svg { fill: var(--bg) !important; }

/* Radio buttons */
.stRadio [role="radio"]{
  border:2px solid var(--accent)!important;
  background:transparent!important;
}
.stRadio [aria-checked="true"]{
  background: var(--accent)!important;
  border-color: var(--accent)!important;
  color:var(--bg)!important;
}
.stRadio label{ color:var(--text)!important; }

/* Slider */
.stSlider [role="slider"]{
  background: var(--accent)!important;
  border:2px solid var(--accent)!important;
}
.stSlider [data-testid="stThumbValue"]{
  color: var(--text)!important;
  background: var(--bg)!important;
  border:1px solid var(--accent)!important;
}
.stSlider [data-testid="stTickBar"] > div{
  background: var(--accent)!important;
}

/* Buttons */
.stButton>button{
  background: var(--accent)!important;
  color: var(--bg)!important;
  border:0; border-radius:999px;
  padding:10px 16px; font-weight:700;
  box-shadow: var(--shadow);
}
.stButton>button:hover{ filter:brightness(1.05); }
</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
hero = st.container()
with hero:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    col_logo, col_text = st.columns([1, 6], gap="large")
    with col_logo:
        # Optional: show logo only if present
        try:
            st.image("logo.png", width=84)
        except Exception:
            pass
    with col_text:
        st.markdown(
            """
            <h1 style="margin:0; font-size:clamp(22px,4vw,36px); color: var(--text);">
              Best Seller Ranker
            </h1>
            <div class="chip" style="margin-top:10px;">Private Dashboard</div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- CONSTANTS ----------
DIMENSIONS = ["brand_name", "mc0", "mc1", "mc2", "mc3", "mc4"]
METRIC_MAP = {
    "Sales": "product_sales",
    "Cost": "product_cost",
    "Price": "product_price",
    "Margin": "margin",
}
ALL_COLUMNS = [
    "date", "product_type_description", "brand_name", "mc0", "mc1", "mc2",
    "mc3", "mc4", "margin", "product_price", "product_cost", "product_sales"
]

# ---------- DATA LOADERS ----------
@st.cache_data(show_spinner=False)
def load_csv_like(file_or_path) -> pd.DataFrame:
    """
    Tries to read a CSV using pandas with automatic delimiter inference.
    Works with file-like objects and paths.
    """
    encodings = ["utf-8", "latin1", "cp1252"]
    for enc in encodings:
        try:
            df = pd.read_csv(file_or_path, sep=None, engine="python", encoding=enc)
            return df
        except Exception:
            if isinstance(file_or_path, (BytesIO, StringIO)):
                file_or_path.seek(0)
            continue
    # final fallback, raise original error
    if isinstance(file_or_path, (BytesIO, StringIO)):
        file_or_path.seek(0)
    return pd.read_csv(file_or_path, encoding="utf-8")
@st.cache_data(show_spinner=False)
def load_excel(file_or_bytes) -> pd.DataFrame:
    """
    Read the first sheet of an Excel file. Accepts upload file or bytes.
    """
    return pd.read_excel(file_or_bytes)  # first sheet by default

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize columns, parse dates & numerics, warn on missing expected cols.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df.columns = [c.strip() for c in df.columns]

    # soft warning for missing columns (not fatal)
    missing = [c for c in ALL_COLUMNS if c not in df.columns]
    if missing:
        st.warning(f"Missing columns in file: {missing}")

    # date → datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # ensure metrics numeric
    for m in METRIC_MAP.values():
        if m in df.columns:
            df[m] = pd.to_numeric(df[m], errors="coerce")

    return df

def load_any(uploaded_file) -> pd.DataFrame:
    """
    Decide how to load based on the uploaded file extension / MIME.
    """
    if uploaded_file is None:
        return pd.DataFrame()

    name = uploaded_file.name.lower()
    if name.endswith(".csv") or name.endswith(".txt"):
        df = load_csv_like(uploaded_file)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = load_excel(uploaded_file)
    else:
        # Try CSV first, then Excel
        try:
            df = load_csv_like(uploaded_file)
        except Exception:
            uploaded_file.seek(0)
            df = load_excel(uploaded_file)
    return normalize_dataframe(df)

@st.cache_data(show_spinner=False)
def load_local_fallback(path: str) -> pd.DataFrame:
    try:
        df = load_csv_like(path)
        return normalize_dataframe(df)
    except Exception:
        return pd.DataFrame()

# ---------- SIDEBAR: UPLOAD + OPTIONS ----------
with st.sidebar:
    st.header("Dataset")
    uploaded = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls", "txt"],
        help="Include columns like date, product_type_description, brand_name, mc0–mc4, margin, product_price, product_cost, product_sales (as available)."
    )

# Load data: prefer upload; otherwise try local fallback; otherwise stop
df = load_any(uploaded)
if df.empty:
    # optional fallback to a local sample file if present
    SAMPLE_PATH = "sales_data.csv"
    sample_df = load_local_fallback(SAMPLE_PATH)
    if not sample_df.empty:
        st.info("No file uploaded — using bundled sample: sales_data.csv")
        df = sample_df
    else:
        st.error("No data loaded. Please upload a CSV/Excel with your sales data.")
        st.stop()

# ---------- MAIN UI ----------
st.title("Best Seller Ranker")

with st.sidebar:
    st.header("Filters")

    # Date range (optional)
    if "date" in df.columns and df["date"].notna().any():
        min_ts, max_ts = df["date"].min(), df["date"].max()
        start_d, end_d = st.date_input(
            "Date range",
            value=(min_ts.date(), max_ts.date()),
            min_value=min_ts.date(),
            max_value=max_ts.date(),
        )
        start_ts = pd.Timestamp(start_d)
        end_ts_excl = pd.Timestamp(end_d) + pd.Timedelta(days=1)
        mask_date = (df["date"] >= start_ts) & (df["date"] < end_ts_excl)
    else:
        mask_date = np.ones(len(df), dtype=bool)

    filtered = df[mask_date].copy()

    # Optional: product_type_description filter
    if "product_type_description" in filtered.columns:
        ptypes = ["(All)"] + sorted(map(str, filtered["product_type_description"].dropna().unique()))
        sel_ptype = st.selectbox("product_type_description", ptypes, index=0)
        if sel_ptype != "(All)":
            filtered = filtered[filtered["product_type_description"].astype(str) == sel_ptype]

    # Dependent dropdowns for the dimensions (only existing values)
    chosen_filters = {}
    dims_available = [d for d in DIMENSIONS if d in filtered.columns]
    for col in dims_available:
        opts = ["(All)"] + sorted(map(str, filtered[col].dropna().unique()))
        sel = st.selectbox(col, opts, index=0)
        if sel != "(All)":
            chosen_filters[col] = sel
            filtered = filtered[filtered[col].astype(str) == sel]

st.caption(f"{len(filtered):,} rows after filters")

metrics_available = {k: v for k, v in METRIC_MAP.items() if v in df.columns}
if not metrics_available:
    st.error(f"No metric columns found. Expected one of {list(METRIC_MAP.values())}, but got {df.columns.tolist()}")
    st.stop()

left, right = st.columns([2, 1])

with left:
    st.subheader("Ranking")
    dims_available = [d for d in DIMENSIONS if d in filtered.columns]  # refresh after filtering
    group_by = st.multiselect(
        "Group by (choose one or a combination)",
        dims_available,
        default=[dims_available[0]] if dims_available else []
    )

with right:
    metric_label = st.radio("Metric", list(metrics_available.keys()), index=0)
    metric_col = metrics_available[metric_label]
    top_n = st.slider("Top N", 1, 50, 10)

if not group_by:
    st.info("Pick at least one column to rank by.")
    st.stop()

# Decide how to aggregate:
if metric_col == "margin":
    aggfunc = "mean"   # average margin
else:
    aggfunc = "sum"    # sum for sales, cost, price

calc = (
    filtered
    .groupby(group_by, dropna=False)[metric_col]
    .agg(aggfunc)
    .reset_index()
    .sort_values(metric_col, ascending=False)
    .head(top_n)
)

# Show results
st.subheader("Results")
st.dataframe(calc.rename(columns={metric_col: metric_label}), use_container_width=True)

# Chart
plot_df = calc.copy()
if len(group_by) == 1:
    plot_df = plot_df.set_index(group_by[0])
else:
    plot_df["__label__"] = plot_df[group_by].astype(str).agg(" | ".join, axis=1)
    plot_df = plot_df.set_index("__label__")
st.bar_chart(plot_df[metric_col])

st.download_button(
    "Download Top N (CSV)",
    calc.to_csv(index=False).encode("utf-8"),
    "ranking.csv",
    "text/csv",
)
