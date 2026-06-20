"""
Module 45: Data Storytelling — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Storytelling | DataScience Flow", page_icon="📊", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 DATA STORYTELLING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Auto-generates a complete narrative report — key statistics, distribution insights, correlation highlights, quality warnings. 100% rule-based, no AI API.

**🎯 Why you need it:** Turn raw numbers into a readable story for stakeholders. This module bridges the gap between analysis and communication.

**📖 How to use it:** Click "Generate Story" → review the narrative → export as text or copy for your report.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📖 Auto-Generated Data Story")
if st.button("📝 Generate Data Story"):
    num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
    cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()
    
    story = []
    story.append(f"# Data Story: {st.session_state.get('filename', 'Your Dataset')}
")
    story.append(f"## Overview
")
    story.append(f"This dataset contains **{dfc.shape[0]:,} rows** and **{dfc.shape[1]} columns**.
")
    
    missing_total = dfc.isnull().sum().sum()
    story.append(f"**Data quality:** {missing_total} missing values across all columns ")
    story.append(f"({missing_total/(dfc.shape[0]*dfc.shape[1])*100:.1f}% of all cells).
")
    dup_count = dfc.duplicated().sum()
    story.append(f"There are {dup_count} duplicate rows.

")
    
    story.append(f"## Key Statistics
")
    if num_cols:
        top_cols = num_cols[:min(5, len(num_cols))]
        for col in top_cols:
            story.append(f"- **{col}**: min={dfc[col].min():.2f}, max={dfc[col].max():.2f}, mean={dfc[col].mean():.2f}, median={dfc[col].median():.2f}
")
    
    if cat_cols:
        story.append(f"
## Category Breakdown
")
        for col in cat_cols[:3]:
            top_val = dfc[col].value_counts().index[0] if not dfc[col].value_counts().empty else "N/A"
            story.append(f"- **{col}**: {dfc[col].nunique()} unique values, most common: '{top_val}'
")
    
    if len(num_cols) >= 2:
        corr = dfc[num_cols].corr()
        high_corr = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                if abs(corr.iloc[i, j]) > 0.5:
                    high_corr.append((num_cols[i], num_cols[j], corr.iloc[i, j]))
        if high_corr:
            story.append(f"
## Notable Correlations
")
            for c1, c2, v in sorted(high_corr, key=lambda x: abs(x[2]), reverse=True)[:5]:
                story.append(f"- {c1} ↔ {c2}: r = {v:.3f}
")
    
    story_text = "".join(story)
    st.markdown(story_text)
    st.download_button("⬇️ Download Story (TXT)", story_text.encode(), "data_story.txt", "text/plain")

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
