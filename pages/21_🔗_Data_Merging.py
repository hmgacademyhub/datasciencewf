"""
Module 21: Data Merging — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

if not verify_subscription_integrity():
    st.error("🔒 Session integrity check failed. Please re-authenticate.")
    st.stop()
if check_session_timeout():
    st.warning("⏰ Session expired. Please re-authenticate.")
    st.stop()
check_rate_limit()



st.set_page_config(page_title="Data Merging | DataScience Flow", page_icon="🔗", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔗 DATA MERGING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 4 join types (inner, left, right, outer), row append, melt/pivot reshape, and interactive pivot table builder.

**🎯 Why you need it:** Real-world analysis often requires combining multiple datasets. This module gives you SQL-like join capabilities without writing code.

**📖 How to use it:** Upload a second dataset → choose join type → select key columns → execute the merge.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔗 Merge with Another Dataset")
uploaded2 = st.file_uploader("Upload second dataset", type=["csv", "xlsx"], key="merge_upload")
if uploaded2:
    try:
        if uploaded2.name.endswith(".csv"):
            df2 = pd.read_csv(uploaded2)
        else:
            df2 = pd.read_excel(uploaded2)
        st.markdown(f"**Second dataset:** {df2.shape[0]:,} rows × {df2.shape[1]} cols")
        st.dataframe(df2.head(5), use_container_width=True)

        join_type = st.selectbox("Join type", ["inner", "left", "right", "outer"])
        common_cols = [c for c in dfc.columns if c in df2.columns]
        if common_cols:
            key = st.selectbox("Join key column", common_cols)
            if st.button("🔗 Execute Merge"):
                merged = dfc.merge(df2, on=key, how=join_type, suffixes=("_left", "_right"))
                st.session_state["df_cleaned"] = merged
                st.success(f"✅ Merged: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
                st.dataframe(merged.head(10), use_container_width=True)
                st.rerun()
        else:
            st.warning("No common columns found between datasets.")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.markdown("### 📊 Pivot Table Builder")
if st.button("Create Pivot Table"):
    all_cols = dfc.columns.tolist()
    idx = st.selectbox("Rows (Index)", all_cols, key="pivot_idx")
    piv_cols = st.selectbox("Columns", all_cols, key="pivot_cols")
    vals = st.selectbox("Values", dfc.select_dtypes(include=np.number).columns.tolist(), key="pivot_vals")
    agg = st.selectbox("Aggregation", ["mean", "sum", "count", "min", "max", "std"])
    try:
        pivot = pd.pivot_table(dfc, index=idx, columns=piv_cols, values=vals, aggfunc=agg)
        st.dataframe(pivot, use_container_width=True)
    except Exception as e:
        st.error(f"Pivot error: {e}")

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
