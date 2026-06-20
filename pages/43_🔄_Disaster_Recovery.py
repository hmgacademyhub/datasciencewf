"""
Module 43: Disaster Recovery — DataScience Flow v9.5
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



st.set_page_config(page_title="Disaster Recovery | DataScience Flow", page_icon="🔄", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔄 DISASTER RECOVERY</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** DR plan builder with RPO (Recovery Point Objective) and RTO (Recovery Time Objective). Backup bundle generator with DR metadata. 5-phase auto-generated DR runbook. DR test scheduler with history.

**🎯 Why you need it:** Every enterprise needs a disaster recovery plan. This module helps you build, document, and test yours — specifically for data assets.

**📖 How to use it:** Define RPO/RTO → generate DR runbook → create backup bundle → schedule DR tests.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔄 Disaster Recovery Plan Builder")
st.caption("Define Recovery Point Objective (RPO) and Recovery Time Objective (RTO).")

rpo_hours = st.number_input("RPO — Recovery Point Objective (max data loss in hours)", 1, 168, 24)
rto_hours = st.number_input("RTO — Recovery Time Objective (max recovery time in hours)", 1, 168, 48)
dr_owner = st.text_input("DR Plan Owner", st.session_state.get("sub_auth_email", "admin"))
backup_freq = st.selectbox("Backup frequency", ["Daily", "Weekly", "Monthly"])

if st.button("🔄 Generate DR Plan"):
    dr_plan = {
        "rpo_hours": rpo_hours, "rto_hours": rto_hours,
        "owner": dr_owner, "backup_frequency": backup_freq,
        "dataset": st.session_state.get("filename", "Unknown"),
        "rows": dfc.shape[0], "cols": dfc.shape[1],
        "created": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state["ent_disaster_recovery"].append(dr_plan)
    st.success("✅ DR plan saved")
    st.rerun()

# Show DR plans
dr_plans = st.session_state.get("ent_disaster_recovery", [])
if dr_plans:
    st.markdown("### 📋 DR Plans")
    latest = dr_plans[-1]
    c1,c2,c3 = st.columns(3)
    c1.metric("RPO (hours)", latest['rpo_hours'])
    c2.metric("RTO (hours)", latest['rto_hours'])
    c3.metric("Backup Frequency", latest['backup_frequency'])
    
    # 5-phase DR runbook
    st.markdown("### 📖 5-Phase DR Runbook")
    runbook = [
        ("🔍 Phase 1: Detection", "Identify incident → Assess scope → Log in audit trail → Notify DR owner"),
        ("📊 Phase 2: Assessment", f"Data loss assessment → RPO: {latest['rpo_hours']}h → Check last backup → Identify affected {latest['rows']:,} rows"),
        ("🔄 Phase 3: Recovery", f"Restore from backup → Validate {latest['cols']} columns → Verify row count → Check data integrity"),
        ("✅ Phase 4: Verification", "Run data quality audit → Compare with pre-incident snapshot → Validate business continuity"),
        ("📝 Phase 5: Post-Mortem", "Document root cause → Update DR plan → Schedule next DR test → File compliance evidence"),
    ]
    for phase, desc in runbook:
        st.markdown(f"**{phase}:** {desc}")
    
    # Backup bundle
    if st.button("📦 Generate Backup Bundle"):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("dr_plan.json", str(latest))
            zf.writestr("data_backup.csv", dfc.to_csv(index=False))
            zf.writestr("audit_log.csv", pd.DataFrame(st.session_state.get("ent_audit_log", [])).to_csv(index=False))
        st.download_button("⬇️ Download DR Backup Bundle", buf.getvalue(), "dr_backup_bundle.zip", "application/zip")
    
    # DR test scheduler
    st.markdown("### 🧪 DR Test Scheduler")
    test_date = st.date_input("Next DR test date")
    if st.button("📅 Schedule DR Test"):
        st.success(f"✅ DR test scheduled for {test_date}")

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
