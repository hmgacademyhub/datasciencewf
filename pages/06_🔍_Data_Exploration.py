"""
Module 6: Data Exploration — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription

from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)


st.set_page_config(page_title="Data Exploration | DataScience Flow | HMG Academy", page_icon="🔍", layout="wide")


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
## 🔍 Data Exploration — Module 6

> **What is Data Exploration?** The first step after loading data — understanding its shape, types, distributions, and issues before any cleaning or modelling.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| Shape | Rows × Columns | Determines your approach |
| Data Types | Numeric, Categorical, DateTime | Determines valid operations |
| Missing Values | Null/NaN cells | Can break models |
| Distributions | How values spread | Reveals skewness & outliers |
| Anomalies | Unexpected values | Data entry errors or rare events |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Rows", f"{df.shape[0]:,}")
c2.metric("📐 Columns", f"{df.shape[1]}")
c3.metric("🕳️ Missing", f"{df.isnull().sum().sum():,}")
c4.metric("♻️ Duplicates", f"{df.duplicated().sum():,}")

tab_overview, tab_head, tab_types, tab_filter, tab_crosstab, tab_sample = st.tabs([
    "📊 Overview", "📋 Head/Tail", "🔢 Column Types", "🔍 Multi-Filter", "📊 Cross-Tab", "🎲 Sample"
])

with tab_overview:
    st.dataframe(df.describe(include='all').transpose(), use_container_width=True)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    missing_df = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values("Missing %", ascending=False)
    if len(missing_df) > 0:
        st.markdown("#### Missing Values per Column")
        st.dataframe(missing_df, use_container_width=True)
        st.bar_chart(missing_df["Missing %"])
    else:
        st.success("✅ No missing values!")

with tab_head:
    n = st.slider("Rows to display", 5, 50, 10)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Head")
        st.dataframe(df.head(n), use_container_width=True)
    with c2:
        st.markdown("#### Tail")
        st.dataframe(df.tail(n), use_container_width=True)

with tab_types:
    type_info = []
    for col in df.columns:
        type_info.append({
            "Column": col, "Type": str(df[col].dtype),
            "Non-Null": int(df[col].notna().sum()),
            "Null %": f"{df[col].isna().mean()*100:.1f}%",
            "Unique": int(df[col].nunique()),
            "Memory (KB)": f"{df[col].memory_usage(deep=True)/1024:.1f}",
        })
    st.dataframe(pd.DataFrame(type_info), use_container_width=True)

with tab_filter:
    filter_cols = st.multiselect("Columns to filter", df.columns.tolist())
    filtered_df = df.copy()
    for col in filter_cols:
        if df[col].dtype in ["object", "string", "category"]:
            vals = df[col].dropna().unique().tolist()
            sel = st.multiselect(f"'{col}'", vals, default=vals, key=f"f_{col}")
            filtered_df = filtered_df[filtered_df[col].isin(sel)]
        elif pd.api.types.is_numeric_dtype(df[col]):
            mn, mx = float(df[col].min()), float(df[col].max())
            rng = st.slider(f"'{col}'", mn, mx, (mn, mx), key=f"f_{col}")
            filtered_df = filtered_df[(filtered_df[col] >= rng[0]) & (filtered_df[col] <= rng[1])]
    st.metric("Filtered", f"{len(filtered_df):,} / {len(df):,}")
    st.dataframe(filtered_df, use_container_width=True)

with tab_crosstab:
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    if len(cat_cols) >= 2:
        row_col = st.selectbox("Row variable", cat_cols, key="ct_r")
        col_col = st.selectbox("Column variable", [c for c in cat_cols if c != row_col], key="ct_c")
        st.dataframe(pd.crosstab(df[row_col], df[col_col], margins=True), use_container_width=True)
    else:
        st.warning("Need ≥2 categorical columns.")

with tab_sample:
    n_s = st.slider("Sample size", 1, min(100, len(df)), min(10, len(df)))
    seed = st.number_input("Seed", value=42)
    st.dataframe(df.sample(n=n_s, random_state=seed), use_container_width=True)

st.markdown("---")
st.markdown("💡 **Next:** Module 6 (Missing Values) → Module 6 (Duplicates) → Module 6 (Outliers)")
st.markdown("*DataScience Flow v9.5 — Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts*")

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
