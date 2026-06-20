"""
Module 7: Missing Values — DataScience Flow v9.5
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


st.set_page_config(page_title="Missing Values | DataScience Flow | HMG Academy", page_icon="🕳️", layout="wide")


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
## 🕳️ Missing Values — Module 7

> **What are Missing Values?** NaN/None/null cells where data was not collected or is unavailable.

### Types of Missing Data
| Type | Abbreviation | Description |
|------|-------------|-------------|
| Missing Completely at Random | MCAR | No relationship to any data |
| Missing at Random | MAR | Related to observed data |
| Missing Not at Random | MNAR | Related to the missing value itself |

### Imputation Strategies
| Strategy | When to Use | Pros | Cons |
|----------|------------|------|------|
| Drop rows | Very few missing (<5%) | Simple | Loses data |
| Mean/Median | MCAR, numeric | Easy | Reduces variance |
| Mode | Categorical, MCAR | Preserves common | Ignores patterns |
| Forward/Backward Fill | Time series | Temporal pattern | Assumes continuity |
| KNN | MAR, moderate missing | Uses similar records | Expensive |
| Group-based | MAR, with grouping column | Context-aware | Needs grouping logic |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
missing = df.isnull().sum()
missing_cols = missing[missing > 0].sort_values(ascending=False)

if len(missing_cols) == 0:
    st.success("✅ No missing values!")
    st.stop()

st.dataframe(pd.DataFrame({
    "Column": missing_cols.index, "Missing": missing_cols.values,
    "Missing %": (missing_cols.values / len(df) * 100).round(1)
}), use_container_width=True)

target_col = st.selectbox("Column to impute", missing_cols.index.tolist())
strategy = st.selectbox("Strategy", [
    "Drop rows", "Fill with Mean", "Fill with Median", "Fill with Mode",
    "Forward Fill", "Backward Fill", "KNN Imputation", "Group-based Imputation", "Constant Value"
])

imputed = df.copy()
if strategy == "Drop rows":
    imputed = df.dropna(subset=[target_col])
elif strategy == "Fill with Mean":
    if pd.api.types.is_numeric_dtype(df[target_col]):
        imputed[target_col] = df[target_col].fillna(df[target_col].mean())
elif strategy == "Fill with Median":
    if pd.api.types.is_numeric_dtype(df[target_col]):
        imputed[target_col] = df[target_col].fillna(df[target_col].median())
elif strategy == "Fill with Mode":
    mode = df[target_col].mode()
    if len(mode) > 0: imputed[target_col] = df[target_col].fillna(mode[0])
elif strategy == "Forward Fill":
    imputed[target_col] = df[target_col].ffill()
elif strategy == "Backward Fill":
    imputed[target_col] = df[target_col].bfill()
elif strategy == "KNN Imputation":
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if target_col in num_cols and len(num_cols) >= 2:
        from sklearn.impute import KNNImputer
        k = st.slider("K neighbors", 1, 20, 5)
        imp = KNNImputer(n_neighbors=k)
        imputed[num_cols] = imp.fit_transform(df[num_cols])
elif strategy == "Group-based Imputation":
    group_col = st.selectbox("Group by", [c for c in df.columns if c != target_col])
    fill_m = st.selectbox("Fill method", ["Mean", "Median", "Mode"])
    if fill_m == "Mean":
        imputed[target_col] = df.groupby(group_col)[target_col].transform(lambda x: x.fillna(x.mean()))
    elif fill_m == "Median":
        imputed[target_col] = df.groupby(group_col)[target_col].transform(lambda x: x.fillna(x.median()))
    else:
        imputed[target_col] = df.groupby(group_col)[target_col].transform(lambda x: x.fillna(x.mode().iloc[0] if len(x.mode()) > 0 else x))
elif strategy == "Constant Value":
    const = st.text_input("Value", "0")
    try:
        imputed[target_col] = df[target_col].fillna(float(const) if pd.api.types.is_numeric_dtype(df[target_col]) else const)
    except: st.error("Invalid value")

if st.button("✅ Apply Imputation"):
    st.session_state["df_cleaned"] = imputed
    st.success("Applied!")
    st.rerun()

st.markdown("---")
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
