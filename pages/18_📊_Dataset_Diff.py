"""
Module 18: Dataset Diff — DataScience Flow v9.5
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



st.set_page_config(page_title="Dataset Diff | DataScience Flow", page_icon="📊", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 DATASET DIFF</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Side-by-side original vs cleaned comparison. Column-level statistical changes. Drift detection. Box/violin/histogram overlay.

**🎯 Why you need it:** Verify that your cleaning and transformations didn't accidentally distort your data. Critical for audit trails.

**📖 How to use it:** Compare original (loaded) data with current (cleaned) data → see what changed → identify unexpected shifts.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📊 Original vs Cleaned Comparison")
orig = st.session_state.get("df")
curr = st.session_state["df_cleaned"]

if orig is None or curr is None:
    st.warning("Need both original and cleaned data.")
    st.stop()

st.markdown(f"**Original:** {orig.shape[0]:,} rows × {orig.shape[1]} cols | **Current:** {curr.shape[0]:,} rows × {curr.shape[1]} cols")

# Column-level comparison
common_cols = [c for c in curr.columns if c in orig.columns]
if common_cols:
    comp_data = []
    for col in common_cols[:20]:
        orig_miss = orig[col].isna().sum()
        curr_miss = curr[col].isna().sum()
        if pd.api.types.is_numeric_dtype(curr[col]) and pd.api.types.is_numeric_dtype(orig[col]):
            orig_mean = orig[col].mean()
            curr_mean = curr[col].mean()
            drift = abs(curr_mean - orig_mean) / (abs(orig_mean) + 0.001) * 100
            comp_data.append({
                "Column": col, "Orig Missing": orig_miss, "Curr Missing": curr_miss,
                "Orig Mean": round(orig_mean, 4), "Curr Mean": round(curr_mean, 4),
                "Drift %": round(drift, 2),
                "Status": "⚠️" if drift > 10 else "✅"
            })
        else:
            comp_data.append({"Column": col, "Orig Missing": orig_miss, "Curr Missing": curr_miss,
                "Orig Mean": "N/A", "Curr Mean": "N/A", "Drift %": 0, "Status": "✅"})
    
    comp_df = pd.DataFrame(comp_data)
    st.dataframe(comp_df, use_container_width=True)
    
    # Select column for visual comparison
    num_cols = [c for c in common_cols if pd.api.types.is_numeric_dtype(curr[c]) and pd.api.types.is_numeric_dtype(orig[c])]
    if num_cols:
        viz_col = st.selectbox("Column for visual comparison", num_cols)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=orig[viz_col].dropna(), name="Original", opacity=0.6, marker_color="#4f8ef7"))
        fig.add_trace(go.Histogram(x=curr[viz_col].dropna(), name="Cleaned", opacity=0.6, marker_color="#00d9a7"))
        fig.update_layout(barmode="overlay", template="plotly_dark", title=f"Distribution Comparison — {viz_col}",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

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
