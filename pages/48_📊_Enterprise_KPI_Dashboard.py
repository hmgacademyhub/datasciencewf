"""
Module 48: Enterprise KPI Dashboard — DataScience Flow v9.5
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



st.set_page_config(page_title="Enterprise KPI Dashboard | DataScience Flow", page_icon="📊", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 ENTERPRISE KPI DASHBOARD</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 6 executive KPI cards: Data Freshness, Quality Score, Compliance, Contracts, Active Rules, Audit Events. Dual gauge charts (Quality + Compliance). 8-category operations radar chart. Executive summary report generator.

**🎯 Why you need it:** Executives need a quick, visual overview of data operations health. This is your C-suite dashboard.

**📖 How to use it:** Review KPIs → check gauges → explore radar chart → generate executive summary.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📊 Executive KPI Dashboard")
st.caption("Enterprise-grade overview of your data operations.")

# Compute KPIs
quality_score = 100 - (dfc.isnull().sum().sum() / (dfc.shape[0]*dfc.shape[1]) * 100)

compliance_status = st.session_state.get("compliance_status", {})
compliant_count = sum(1 for v in compliance_status.values() if v == "✅ Compliant")
compliance_score = (compliant_count / max(len(compliance_status), 1)) * 100 if compliance_status else 0

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("📊 Data Freshness", "Live", "Session Data")
c2.metric("✅ Quality Score", f"{quality_score:.1f}%", f"{'🟢' if quality_score>90 else '🟡'}")
c3.metric("⚖️ Compliance", f"{compliance_score:.0f}%", f"{compliant_count} compliant")
c4.metric("📜 Contracts", str(len(st.session_state.get("ent_data_contracts", []))))
c5.metric("🔔 Active Rules", str(len(st.session_state.get("monitored_rules", []))))
c6.metric("🔍 Audit Events", str(len(st.session_state.get("ent_audit_log", []))))

# Gauges
st.markdown("### 📈 Quality & Compliance Gauges")
g1,g2 = st.columns(2)
with g1:
    fig = go.Figure(go.Indicator(mode="gauge+number", value=quality_score,
        title={"text": "Data Quality"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#00d9a7"},
            "steps": [{"range": [0,70], "color":"#f8514922"}, {"range":[70,90],"color":"#d4a84322"}, {"range":[90,100],"color":"#00d9a722"}]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280)
    st.plotly_chart(fig, use_container_width=True)

with g2:
    fig = go.Figure(go.Indicator(mode="gauge+number", value=compliance_score,
        title={"text": "Compliance"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#8b5cf6"},
            "steps": [{"range": [0,60], "color":"#f8514922"}, {"range":[60,85],"color":"#d4a84322"}, {"range":[85,100],"color":"#8b5cf622"}]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280)
    st.plotly_chart(fig, use_container_width=True)

# Radar chart
st.markdown("### 🎯 Operations Radar")
categories = ["Data Quality", "Compliance", "Security", "Monitoring", "Recovery", "Collaboration", "Documentation", "Governance"]
values = [quality_score, compliance_score, 80 if st.session_state.get("masked_columns") else 30,
    70 if st.session_state.get("monitored_rules") else 20, 60 if st.session_state.get("ent_disaster_recovery") else 10,
    50 if st.session_state.get("ent_collab_notes") else 10, 70 if st.session_state.get("data_dictionary") else 20,
    60 if st.session_state.get("ent_data_contracts") else 10]
fig = go.Figure(data=go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill="toself",
    marker=dict(color="#00d9a7"), line=dict(color="#00d9a7", width=2)))
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
st.plotly_chart(fig, use_container_width=True)

# Executive summary
if st.button("📝 Generate Executive Summary"):
    summary = f"""# Executive Summary — Data Operations
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## Key Metrics
- Data Quality: {quality_score:.1f}%
- Compliance: {compliance_score:.0f}%
- Dataset: {dfc.shape[0]:,} rows × {dfc.shape[1]} cols
- Audit Events: {len(st.session_state.get('ent_audit_log',[]))}

## Risk Assessment
- {'⚠️' if quality_score<80 else '✅'} Data Quality: {'Needs attention' if quality_score<80 else 'Acceptable'}
- {'⚠️' if compliance_score<60 else '✅'} Compliance: {'Gaps identified' if compliance_score<60 else 'On track'}

## Recommendations
1. {'Run data quality audit' if quality_score<90 else 'Continue monitoring'}
2. {'Complete compliance checklist' if compliance_score<80 else 'Maintain compliance'}
3. {'Set up monitoring rules' if not st.session_state.get('monitored_rules') else 'Review active rules'}

---
Generated by DataScience Flow Suite v7.0 | HMG Concepts | Adewale Samson Adeagbo
"""
    st.download_button("⬇️ Download Executive Summary", summary.encode(), "executive_summary.md", "text/markdown")

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
