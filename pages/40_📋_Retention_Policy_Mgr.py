"""
Module 40: Retention Policy Mgr — DataScience Flow v9.5
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



st.set_page_config(page_title="Retention Policy Mgr | DataScience Flow", page_icon="📋", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📋 RETENTION POLICY MANAGER</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Time-based retention rules (review, archive, purge days). Legal-hold override to prevent deletion. Retention timeline simulator. Auto-generated retention audit reports.

**🎯 Why you need it:** Data protection laws require you to define how long you keep data. This module helps you define, simulate, and document retention policies.

**📖 How to use it:** Set retention periods → review timeline → add legal holds → generate audit report.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📋 Retention Policy Manager")
st.caption("Define how long data is retained before review, archiving, or deletion.")

st.markdown("#### Define Retention Periods")
review_days = st.number_input("Review after (days)", 1, 3650, 90)
archive_days = st.number_input("Archive after (days)", 1, 3650, 365)
purge_days = st.number_input("Purge after (days)", 1, 3650, 730)
legal_hold = st.checkbox("🔒 Legal Hold (prevent automatic deletion)")

if st.button("📋 Save Retention Policy"):
    policy = {
        "review_days": review_days, "archive_days": archive_days,
        "purge_days": purge_days, "legal_hold": legal_hold,
        "created": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        "dataset": st.session_state.get("filename", "Unknown")
    }
    st.session_state["ent_retention_rules"].append(policy)
    st.success("✅ Retention policy saved")
    st.rerun()

# Show policies
policies = st.session_state.get("ent_retention_rules", [])
if policies:
    st.markdown("### 📋 Current Retention Policies")
    for i, p in enumerate(policies):
        with st.expander(f"Policy {i+1}: {p['dataset']} ({p['created']})", expanded=i==len(policies)-1):
            st.markdown(f"- Review: {p['review_days']} days")
            st.markdown(f"- Archive: {p['archive_days']} days")
            st.markdown(f"- Purge: {p['purge_days']} days")
            st.markdown(f"- Legal Hold: {'🔒 YES' if p['legal_hold'] else '❌ No'}")
    
    # Timeline simulator
    st.markdown("### ⏳ Retention Timeline Simulator")
    latest = policies[-1]
    timeline = []
    today = pd.Timestamp.now()
    for label, days in [("Created", 0), ("Review Due", latest['review_days']),
        ("Archive Due", latest['archive_days']), ("Purge Due", latest['purge_days'])]:
        timeline.append({"Milestone": label, "Date": (today + pd.Timedelta(days=days)).strftime("%Y-%m-%d"), "Days from Now": days})
    st.dataframe(pd.DataFrame(timeline), use_container_width=True)
    
    # Audit report
    if st.button("📝 Generate Retention Audit Report"):
        report = f"""# Retention Policy Audit Report
Generated: {today.strftime('%Y-%m-%d %H:%M')}
Platform: DataScience Flow Suite | HMG Concepts

## Policy Summary
- Review: {latest['review_days']} days
- Archive: {latest['archive_days']} days  
- Purge: {latest['purge_days']} days
- Legal Hold: {'ACTIVE' if latest['legal_hold'] else 'None'}

## Timeline
- Review by: {timeline[1]['Date']}
- Archive by: {timeline[2]['Date']}
- Purge by: {timeline[3]['Date']}

## Dataset
- File: {latest['dataset']}
- Rows: {dfc.shape[0]:,}
- Columns: {dfc.shape[1]}

## Auditor Notes
[To be completed]
"""
        st.download_button("⬇️ Download Audit Report", report.encode(), "retention_audit_report.md", "text/markdown")

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
