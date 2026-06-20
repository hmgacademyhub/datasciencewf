"""
Module 39: Compliance Center — DataScience Flow v9.5
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



st.set_page_config(page_title="Compliance Center | DataScience Flow", page_icon="⚖️", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">⚖️ COMPLIANCE CENTER</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 12-point GDPR/NDPR compliance checklist with compliant/partial/non-compliant tracking. DPIA (Data Protection Impact Assessment) template generator. Consent management log. Compliance score history with trend chart.

**🎯 Why you need it:** For organizations handling personal data in Nigeria (NDPR) or EU (GDPR). Document your compliance journey systematically.

**📖 How to use it:** Go through the checklist → mark status → generate DPIA → track compliance score over time.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### ⚖️ GDPR / NDPR Compliance Center")
st.caption("Track your data protection compliance. NDPR = Nigeria Data Protection Regulation.")

checklist_items = [
    "Data inventory documented",
    "Lawful basis for processing identified",
    "Privacy notice published",
    "Data subject rights process in place",
    "Consent management system operational",
    "Data retention policy defined",
    "Data Protection Impact Assessment (DPIA) completed",
    "Data breach response plan ready",
    "Data Processor agreements signed",
    "Cross-border transfer safeguards",
    "Data Protection Officer appointed",
    "Staff data protection training completed",
]

st.markdown("### ✅ Compliance Checklist")
if "compliance_status" not in st.session_state:
    st.session_state["compliance_status"] = {item: "Not Assessed" for item in checklist_items}

for item in checklist_items:
    current = st.session_state["compliance_status"].get(item, "Not Assessed")
    status = st.radio(item, ["✅ Compliant", "🟡 Partial", "🔴 Non-Compliant", "⚪ Not Assessed"],
        horizontal=True, index=["✅ Compliant", "🟡 Partial", "🔴 Non-Compliant", "⚪ Not Assessed"].index(current), key=f"comp_{item[:20]}")
    st.session_state["compliance_status"][item] = status

# Score
compliant = sum(1 for v in st.session_state["compliance_status"].values() if v == "✅ Compliant")
partial = sum(1 for v in st.session_state["compliance_status"].values() if v == "🟡 Partial")
total = len(checklist_items)
score = (compliant + partial * 0.5) / total * 100
st.metric("Compliance Score", f"{score:.0f}%", f"{compliant} compliant, {partial} partial")

# DPIA Generator
st.markdown("### 📋 DPIA Template Generator")
if st.button("📝 Generate DPIA Template"):
    dpia = f"""# Data Protection Impact Assessment (DPIA)
Generated: {pd.Timestamp.now().strftime("%Y-%m-%d")}
Platform: DataScience Flow Suite | HMG Concepts

## 1. Description of Processing
- Dataset: {st.session_state.get('filename', 'N/A')}
- Rows: {dfc.shape[0]:,} | Columns: {dfc.shape[1]}
- Purpose: [To be completed by Data Protection Officer]

## 2. Necessity & Proportionality
- Is processing necessary? [Yes/No — explain]
- Less intrusive alternatives considered? [Yes/No]

## 3. Risks to Data Subjects
- Data types involved: {', '.join(dfc.columns[:10].tolist())}
- Special category data: [Identify any]
- Potential impact: [Describe]

## 4. Mitigation Measures
- Pseudonymization: {'Applied' if st.session_state.get('masked_columns') else 'Not applied'}
- Encryption: [Specify]
- Access controls: Role-based (8 roles configured)

## 5. Conclusion
- Overall risk level: [Low/Medium/High]
- Recommended actions: [List]
- DPO sign-off: __________________ Date: _________
"""
    st.download_button("⬇️ Download DPIA Template", dpia.encode(), "dpia_template.md", "text/markdown")

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
