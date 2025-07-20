import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quick EDA & KPI", layout="wide")

st.title("📊 Quick EDA & KPI Generator")
st.caption("Upload a CSV (≤ 200 MB). Everything runs locally—your data never leaves the browser session.")

# ---------- File upload ----------
file = st.file_uploader("Choose a CSV file", type="csv")
if not file:
    st.info("⬆️  Drag & drop or browse to a CSV to begin…")
    st.stop()

# ---------- Load data ----------
@st.cache_data(show_spinner="Reading data…")
def load_csv(f):
    return pd.read_csv(f)

df = load_csv(file)

# ---------- Fast KPIs ----------
tot_rows, tot_cols = df.shape
missing_pct = df.isna().mean().mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Rows", f"{tot_rows:,}")
c2.metric("Columns", f"{tot_cols}")
c3.metric("Missing (%)", f"{missing_pct:.2f}%")

st.divider()

# ---------- Data preview ----------
st.subheader("🔍 First 200 rows")
st.dataframe(df.head(200), use_container_width=True, height=350)

# ---------- Summary stats ----------
st.subheader("🧮 Summary statistics")
st.dataframe(df.describe(include="all").T, use_container_width=True)

# ---------- Correlation heat‑map ----------
num_cols = df.select_dtypes("number").columns
if len(num_cols) >= 2:
    st.subheader("📈 Correlation heat‑map")
    fig = px.imshow(df[num_cols].corr(),
                    text_auto=".2f", aspect="auto",
                    title="Correlation matrix")
    st.plotly_chart(fig, use_container_width=True, key="corr")
else:
    st.info("Need at least two numeric columns for a correlation heat‑map.")

# ---------- Custom KPI picker ----------
with st.expander("🎯 Choose a numeric column to summarise"):
    if num_cols.any():
        kpi_col = st.selectbox("Column", num_cols)
        if kpi_col:
            st.metric(f"Total {kpi_col}", f"{df[kpi_col].sum():,.2f}")
            st.metric(f"Average {kpi_col}", f"{df[kpi_col].mean():,.2f}")
            st.metric(f"Median {kpi_col}", f"{df[kpi_col].median():,.2f}")

# ---------- (Optional) full auto‑EDA report ----------
with st.expander("🤖 Auto‑generate full profiling report (ydata‑profiling)"):
    if st.button("Run profiling"):
        from ydata_profiling import ProfileReport
        with st.spinner("Building report… this may take a minute"):
            pr = ProfileReport(df, title="Pandas Profiling Report", explorative=True)
            pr.to_file("report.html")
        st.success("Report created → ▸ **report.html**")
        st.download_button("Download report.html", data=open("report.html", "rb"), file_name="EDA_report.html")
