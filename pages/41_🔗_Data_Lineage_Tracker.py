"""
Module 41: Data Lineage Tracker — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Lineage Tracker | DataScience Flow", page_icon="🔗", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔗 DATA LINEAGE TRACKER</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Visualize every transformation applied to your data — from upload to final export. Complete provenance tracking with timestamps, operations, and row/column counts.

**🎯 Why you need it:** For regulatory compliance (GDPR/NDPR), debugging, and team handoffs. Know exactly what happened to your data at every step.

**📖 How to use it:** View the auto-generated lineage → filter by phase → export as CSV → use for audit evidence.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔗 Data Transformation Lineage")
lineage = st.session_state.get("lineage", [])
if not lineage:
    st.info("No transformations yet. Lineage is auto-tracked as you use modules.")
else:
    ldf = pd.DataFrame(lineage)
    st.markdown(f"**{len(ldf)} transformation steps**")
    
    # Visual timeline
    fig = go.Figure()
    for i, row in ldf.iterrows():
        fig.add_trace(go.Scatter(x=[i], y=[row['rows']], mode='markers+text',
            text=[row['step']], textposition="top center",
            marker=dict(size=max(10, row['rows']/100), color="#00d9a7"),
            name=row['step']))
    fig.update_layout(title="Data Volume Over Transformations", template="plotly_dark",
        xaxis_title="Step", yaxis_title="Rows", showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(ldf, use_container_width=True)
    st.download_button("⬇️ Download Lineage (CSV)", ldf.to_csv(index=False).encode(), "data_lineage.csv", "text/csv")

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
