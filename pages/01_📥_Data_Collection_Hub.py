"""
Module 01: Data Collection Hub — DataScience Flow v9.5
Multi-source data ingestion: CSV, Excel, JSON, Parquet, manual entry, sample datasets
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

st.set_page_config(page_title="Data Collection Hub | DataScience Flow", page_icon="📥", layout="wide")

from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription
from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)

# ═══ Security & Session Verification ═══
init_secure_session()
if not st.session_state.get("sub_authenticated"):
    st.warning("⚠️ Subscription required. Start your free trial from the Home page.")
    st.stop()
if not verify_subscription_integrity():
    st.error("🔒 Session integrity check failed. Please re-authenticate.")
    st.stop()
if check_session_timeout():
    st.warning("⏰ Session expired. Please re-authenticate.")
    st.stop()
check_rate_limit()

st.markdown("""
## 📥 Data Collection Hub — Module 01

> **What is Data Collection?** Data collection is the systematic process of gathering information 
> from various sources to build a dataset for analysis. It's the critical first step in any data 
> science project — the quality of your analysis depends entirely on the quality of your data.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| Data Ingestion | Bringing data into your analysis environment | All analysis starts here |
| Format Diversity | CSV, Excel, JSON, Parquet, SQL, API | Real data comes in many forms |
| Data Validation | Checking data integrity on load | Catch problems early before they propagate |
| Sampling | Taking a representative subset | Large datasets need efficient handling |
| Metadata | Describing your data's structure | Critical for reproducibility |

### 📐 Choosing the Right Format
| Format | Best For | Max Size | Features |
|--------|----------|----------|----------|
| CSV | Tabular data, universal | ~100MB | Simple, universal, text-based |
| Excel (.xlsx) | Business data, reports | ~50MB | Multiple sheets, formatting |
| JSON | Nested/hierarchical data | ~50MB | Flexible schema, web APIs |
| Parquet | Large datasets, analytics | ~10GB | Columnar, compressed, fast |
| Manual Entry | Small test datasets | <1K rows | Quick prototyping, testing |
""")

st.markdown("### 📥 Upload Your Data")

tab_upload, tab_sample, tab_manual, tab_paste = st.tabs([
    "📁 File Upload", "📊 Sample Datasets", "✏️ Manual Entry", "📋 Paste Data"
])

with tab_upload:
    st.markdown("""**How to upload:** Click "Browse files" or drag and drop. Supported formats: CSV, Excel (.xlsx), JSON, Parquet, TSV.""")
    
    uploaded = st.file_uploader(
        "Choose a data file",
        type=["csv", "xlsx", "xls", "json", "parquet", "tsv"],
        help="Supported: CSV, Excel, JSON, Parquet, TSV",
        key="file_uploader"
    )
    
    if uploaded:
        try:
            # Validate upload
            is_valid, msg = validate_upload(uploaded.name, uploaded.size)
            if not is_valid:
                st.error(f"❌ {msg}")
            else:
                ext = uploaded.name.split('.')[-1].lower()
                if ext == 'csv':
                    enc = st.selectbox("Encoding", ["utf-8", "latin-1", "cp1252", "iso-8859-1"], key="csv_enc")
                    sep = st.selectbox("Delimiter", [",", ";", "\t", "|"], key="csv_sep")
                    df = pd.read_csv(uploaded, encoding=enc, sep=sep)
                elif ext in ('xlsx', 'xls'):
                    xl = pd.ExcelFile(uploaded)
                    if len(xl.sheet_names) > 1:
                        sheet = st.selectbox("Sheet", xl.sheet_names, key="sheet_sel")
                    else:
                        sheet = xl.sheet_names[0]
                    df = pd.read_excel(uploaded, sheet_name=sheet)
                elif ext == 'json':
                    df = pd.read_json(uploaded)
                elif ext == 'parquet':
                    df = pd.read_parquet(uploaded)
                elif ext == 'tsv':
                    df = pd.read_csv(uploaded, sep='\t')
                else:
                    st.error(f"Unsupported format: {ext}")
                    st.stop()
                
                st.session_state["df"] = df
                st.session_state["df_cleaned"] = df.copy()
                st.session_state["original_df"] = df.copy()
                
                log_action("data_upload", f"{uploaded.name}, {df.shape}")
                
                st.success(f"✅ **{uploaded.name}** loaded — {df.shape[0]:,} rows × {df.shape[1]} columns")
                
                with st.expander("📋 Data Preview"):
                    st.dataframe(df.head(20), use_container_width=True)
                
                with st.expander("📊 Data Dictionary"):
                    dict_data = {
                        "Column": df.columns.tolist(),
                        "Type": [str(df[c].dtype) for c in df.columns],
                        "Non-Null": [df[c].notna().sum() for c in df.columns],
                        "Missing": [df[c].isna().sum() for c in df.columns],
                        "Missing %": [f"{df[c].isna().sum()/len(df)*100:.1f}%" for c in df.columns],
                        "Unique": [df[c].nunique() for c in df.columns],
                        "Sample": [str(df[c].iloc[0]) if len(df) > 0 else "—" for c in df.columns],
                    }
                    st.dataframe(pd.DataFrame(dict_data), use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

with tab_sample:
    st.markdown("### 📊 Built-in Sample Datasets")
    st.caption("Perfect for learning and testing — no upload needed!")
    
    sample_options = {
        "🏠 Iris (Classification)": "iris",
        "🍷 Wine Quality (Regression)": "wine",
        "📊 Tips (Regression/Categorical)": "tips",
        "🎯 Breast Cancer (Binary Classification)": "cancer",
        "📝 Digits (Multiclass/Image)": "digits",
        "🏠 California Housing (Large Regression)": "housing",
        "📈 Boston Housing (Classic Regression)": "boston",
        "🛒 Superstore Sales (Business Analytics)": "superstore",
        "🧬 Diabetes (Health Classification)": "diabetes",
        "📱 Titanic (Survival Classification)": "titanic",
    }
    
    sample_choice = st.selectbox("Choose a dataset", list(sample_options.keys()), key="sample_choice")
    
    if st.button("📥 Load Dataset", key="load_sample"):
        from sklearn import datasets as sk_d
        choice = sample_options[sample_choice]
        
        try:
            if choice == "iris":
                data = sk_d.load_iris(as_frame=True)
                df = data.frame.rename(columns={data.target_names[i]: f"target_{i}" for i in range(3)} if False else {})
                df = data.frame
                df.columns = [c.replace(' (cm)', '').replace(' ', '_') for c in df.columns]
                df['species'] = data.target_names[data.target]
            elif choice == "wine":
                data = sk_d.load_wine(as_frame=True)
                df = data.frame
                df['target'] = data.target
            elif choice == "tips":
                df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv")
            elif choice == "cancer":
                data = sk_d.load_breast_cancer(as_frame=True)
                df = data.frame
                df['target'] = data.target_names[data.target]
            elif choice == "digits":
                data = sk_d.load_digits(as_frame=True)
                df = data.frame
                df['target'] = data.target
            elif choice == "housing":
                data = sk_d.fetch_california_housing(as_frame=True)
                df = data.frame
                df['MedHouseVal'] = data.target
            elif choice == "diabetes":
                data = sk_d.load_diabetes(as_frame=True)
                df = data.frame
                df['target'] = data.target
            elif choice == "boston":
                st.info("Boston dataset deprecated in sklearn. Loading California Housing instead.")
                data = sk_d.fetch_california_housing(as_frame=True)
                df = data.frame
                df['MedHouseVal'] = data.target
            elif choice == "superstore":
                st.info("Generating sample superstore data...")
                np.random.seed(42)
                n = 1000
                df = pd.DataFrame({
                    'Order_ID': [f'ORD-{i:05d}' for i in range(n)],
                    'Category': np.random.choice(['Technology', 'Furniture', 'Office Supplies'], n),
                    'Sales': np.random.exponential(200, n).round(2),
                    'Quantity': np.random.randint(1, 20, n),
                    'Discount': np.random.choice([0, 0.1, 0.2, 0.3, 0.5], n),
                    'Profit': np.random.normal(30, 80, n).round(2),
                    'Region': np.random.choice(['West', 'East', 'Central', 'South'], n),
                    'Ship_Mode': np.random.choice(['Standard', 'Second Class', 'First Class', 'Same Day'], n),
                })
            elif choice == "titanic":
                df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
            
            st.session_state["df"] = df
            st.session_state["df_cleaned"] = df.copy()
            st.session_state["original_df"] = df.copy()
            log_action("load_sample", choice)
            st.success(f"✅ **{sample_choice}** loaded — {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Error loading sample: {e}")

with tab_manual:
    st.markdown("### ✏️ Create Dataset Manually")
    st.caption("Build a small dataset from scratch for testing or learning.")
    
    col_names = st.text_input("Column names (comma-separated)", "Name,Age,City,Score", key="manual_cols")
    n_rows = st.number_input("Number of rows", min_value=1, max_value=100, value=5, key="manual_rows")
    
    if st.button("Create Empty Template", key="create_template"):
        cols = [c.strip() for c in col_names.split(',')]
        df = pd.DataFrame(columns=cols, index=range(n_rows))
        st.session_state["df"] = df
        st.session_state["df_cleaned"] = df.copy()
        st.session_state["original_df"] = df.copy()
        st.success("✅ Template created! Edit below or download and re-upload.")
        st.data_editor(df, num_rows="dynamic", key="manual_editor", use_container_width=True)

with tab_paste:
    st.markdown("### 📋 Paste Data from Clipboard")
    st.caption("Copy data from Excel/Google Sheets and paste directly.")
    
    pasted = st.text_area(
        "Paste your data here (tab or comma separated)",
        height=200,
        placeholder="Name\tAge\tCity\nAlice\t30\tLagos\nBob\t25\tAbuja"
    )
    
    sep_choice = st.radio("Separator", ["Tab", "Comma", "Semicolon"], horizontal=True, key="paste_sep")
    sep_map = {"Tab": "\t", "Comma": ",", "Semicolon": ";"}
    
    if st.button("Parse & Load", key="parse_paste") and pasted:
        try:
            df = pd.read_csv(io.StringIO(pasted), sep=sep_map[sep_choice])
            st.session_state["df"] = df
            st.session_state["df_cleaned"] = df.copy()
            st.session_state["original_df"] = df.copy()
            st.success(f"✅ Parsed — {df.shape[0]:,} rows × {df.shape[1]} columns")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Parse error: {e}")

# Current data info
if st.session_state.get("df") is not None:
    st.markdown("---")
    st.markdown("### 📊 Currently Loaded Dataset")
    dfc = st.session_state["df_cleaned"]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📋 Rows", f"{dfc.shape[0]:,}")
    c2.metric("📐 Columns", f"{dfc.shape[1]}")
    c3.metric("🕳️ Missing %", f"{dfc.isnull().sum().sum()/(dfc.shape[0]*dfc.shape[1])*100:.1f}%")
    c4.metric("♻️ Duplicates", f"{dfc.duplicated().sum()}")
    c5.metric("💾 Memory", f"{dfc.memory_usage(deep=True).sum()/1024/1024:.1f} MB")
    
    with st.expander("📋 Quick Data Dictionary"):
        dict_data = {
            "Column": dfc.columns.tolist(),
            "Type": [str(dfc[c].dtype) for c in dfc.columns],
            "Non-Null": [dfc[c].notna().sum() for c in dfc.columns],
            "Missing": [dfc[c].isna().sum() for c in dfc.columns],
            "Unique": [dfc[c].nunique() for c in dfc.columns],
        }
        st.dataframe(pd.DataFrame(dict_data), use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Data collection is where everything begins. Always validate your data on load — 
check for encoding issues, missing values, and type mismatches. A clean load saves hours of debugging later.

📚 **Next Steps:** After loading data, proceed to Module 06 (Data Exploration) to understand your dataset's structure.
""")

# ═══════════════════════════════════════════════════════════════
# BRAND FOOTER — DataScience Flow v9.5 | HMG Academy
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; font-size:0.82rem; color:#A0A8B8;">
<b>DataScience Flow</b> v9.5 — Part of <b>HMG Academy</b> Ecosystem — Subsidiary of <b>HMG Concepts</b> (est. 2015)<br>
Built by <b>Adewale Samson Adeagbo</b> | 🔒 Secured Platform | 🏗️ HMG Academy · HMG Technologies · HMG Media · HMG Gospel<br>
<a href="https://hmgacademy.pages.dev" style="color:#6C63FF;">hmgacademy.pages.dev</a> ·
<a href="https://hmgconcepts.pages.dev" style="color:#6C63FF;">hmgconcepts.pages.dev</a> ·
<a href="https://cssadewale.pages.dev" style="color:#6C63FF;">cssadewale.pages.dev</a>
</div>
""", unsafe_allow_html=True)
