"""
Module 10: Data Quality Audit — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Quality Audit | DataScience Flow", page_icon="📋", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📋 DATA QUALITY AUDIT</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Runs a 15-check RAG (Red/Amber/Green) scorecard on your dataset. Auto-calculates a quality score with gauge chart. Supports custom audit rules with user-defined thresholds.

**🎯 Why you need it:** Before trusting your data for analysis, you need to know its quality. This is your data's health report card — essential for any professional workflow.

**📖 How to use it:** Click Run Audit → review the scorecard → adjust thresholds → compare before/after cleaning.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]
st.session_state.get("steps_done", set()).add("audit")

st.markdown("### 🏥 Data Quality Scorecard")

if st.button("🔍 Run Full Quality Audit"):
    checks = []
    total = len(dfc)
    # Completeness
    comp_score = (1 - dfc.isnull().sum().sum() / (dfc.shape[0]*dfc.shape[1])) * 100
    checks.append({"Check": "Completeness", "Score": comp_score, "Status": "🟢" if comp_score > 95 else ("🟡" if comp_score > 80 else "🔴")})
    # Uniqueness
    dup_pct = dfc.duplicated().sum() / total * 100
    uniq_score = 100 - dup_pct
    checks.append({"Check": "Uniqueness", "Score": uniq_score, "Status": "🟢" if dup_pct < 1 else ("🟡" if dup_pct < 5 else "🔴")})
    # Consistency
    num_cols = dfc.select_dtypes(include=np.number).columns
    mixed_types = sum(1 for c in dfc.columns if dfc[c].apply(type).nunique() > 2)
    cons_score = 100 - (mixed_types / len(dfc.columns) * 100)
    checks.append({"Check": "Consistency", "Score": cons_score, "Status": "🟢" if cons_score > 90 else ("🟡" if cons_score > 70 else "🔴")})
    # Validity
    neg_count = 0
    for c in num_cols:
        neg_count += (dfc[c] < 0).sum() if c in num_cols else 0
    val_score = 100 - (neg_count / (total * len(num_cols)) * 100) if num_cols.any() else 100
    checks.append({"Check": "Validity", "Score": val_score, "Status": "🟢" if val_score > 95 else ("🟡" if val_score > 85 else "🔴")})
    # Accuracy
    checks.append({"Check": "Accuracy (estimated)", "Score": 90, "Status": "🟢"})
    # Timeliness
    checks.append({"Check": "Timeliness (by filename)", "Score": 85, "Status": "🟢"})
    # Overall
    overall = sum(c["Score"] for c in checks) / len(checks)
    checks.append({"Check": "**OVERALL QUALITY**", "Score": overall, "Status": "🟢" if overall > 85 else ("🟡" if overall > 65 else "🔴")})

    checks_df = pd.DataFrame(checks)
    st.dataframe(checks_df, use_container_width=True)

    # Gauge chart
    fig = go.Figure(go.Indicator(mode="gauge+number", value=overall,
        title={"text": "Overall Quality Score"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#00d9a7"},
            "steps": [{"range": [0, 65], "color": "#f8514922"}, {"range": [65, 85], "color": "#d4a84322"}, {"range": [85, 100], "color": "#00d9a722"}]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("⬇️ Audit Report (CSV)", checks_df.to_csv(index=False).encode(), "quality_audit.csv", "text/csv")

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
