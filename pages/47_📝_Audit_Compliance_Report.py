"""
Module 47: Audit & Compliance Rpt — DataScience Flow v9.5
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



st.set_page_config(page_title="Audit & Compliance Report | DataScience Flow", page_icon="📝", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📝 AUDIT & COMPLIANCE REPORT</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Auto-detects findings across all modules with severity (Critical/Major/Minor). GDPR/NDPR/SOC 2 framework mapping. Evidence collection bundle export. Comprehensive audit report with recommendations.

**🎯 Why you need it:** For formal audits, regulatory reviews, and internal governance. Generate a complete, evidence-backed audit report in one click.

**📖 How to use it:** Click "Generate Full Audit" → review findings → map to frameworks → download evidence bundle.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📝 Comprehensive Audit & Compliance Report")

if st.button("🔍 Generate Full Audit Report"):
    findings = []
    
    # Check data quality
    missing_pct = dfc.isnull().sum().sum() / (dfc.shape[0]*dfc.shape[1]) * 100
    if missing_pct > 10:
        findings.append({"Finding": "High missing data rate", "Severity": "🔴 Critical", "Detail": f"{missing_pct:.1f}% missing", "Framework": "GDPR Art 5(1)(d) / NDPR"})
    elif missing_pct > 5:
        findings.append({"Finding": "Moderate missing data", "Severity": "🟡 Minor", "Detail": f"{missing_pct:.1f}% missing", "Framework": "GDPR Art 5(1)(d)"})
    
    dups = dfc.duplicated().sum()
    if dups > 0:
        findings.append({"Finding": "Duplicate records exist", "Severity": "🟡 Minor", "Detail": f"{dups} duplicates", "Framework": "GDPR Art 5(1)(d)"})
    
    # Privacy
    if not st.session_state.get("masked_columns"):
        findings.append({"Finding": "No data masking applied", "Severity": "🟠 Major", "Detail": "PII may not be protected", "Framework": "NDPR Part 3 / GDPR Art 32"})
    
    # Contracts
    if not st.session_state.get("ent_data_contracts"):
        findings.append({"Finding": "No data contracts defined", "Severity": "🟠 Major", "Detail": "Schema not validated", "Framework": "SOC 2 / GDPR Art 25"})
    
    # Compliance
    if not st.session_state.get("compliance_status"):
        findings.append({"Finding": "Compliance assessment not started", "Severity": "🟠 Major", "Detail": "GDPR/NDPR checklist incomplete", "Framework": "GDPR / NDPR"})
    
    if not findings:
        findings.append({"Finding": "No critical issues found", "Severity": "✅ Pass", "Detail": "All checks passed", "Framework": "N/A"})
    
    findings_df = pd.DataFrame(findings)
    st.markdown(f"### {len(findings)} Findings")
    st.dataframe(findings_df, use_container_width=True)
    
    # Framework mapping
    st.markdown("### 📊 Framework Coverage")
    st.markdown("- **GDPR (General Data Protection Regulation)** — EU Data Protection")
    st.markdown("- **NDPR (Nigeria Data Protection Regulation)** — Nigerian Implementation")
    st.markdown("- **SOC 2** — Service Organization Controls")
    
    # Evidence bundle
    st.markdown("### 📦 Evidence Collection Bundle")
    if st.button("📦 Generate Evidence Bundle"):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("audit_findings.csv", findings_df.to_csv(index=False))
            zf.writestr("audit_log.csv", pd.DataFrame(st.session_state.get("ent_audit_log", [])).to_csv(index=False))
            zf.writestr("data_lineage.csv", pd.DataFrame(st.session_state.get("lineage", [])).to_csv(index=False))
            zf.writestr("data_dictionary.csv", pd.DataFrame([{"Column":k, **v} for k,v in st.session_state.get("data_dictionary", {}).items()]).to_csv(index=False) if st.session_state.get("data_dictionary") else "")
        st.download_button("⬇️ Download Evidence Bundle (.zip)", buf.getvalue(), "audit_evidence_bundle.zip", "application/zip")

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
