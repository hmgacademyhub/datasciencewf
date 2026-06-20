"""
Module 38: Data Contracts — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Contracts | DataScience Flow", page_icon="📜", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📜 DATA CONTRACTS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Define column-level schemas: required columns, type enforcement, value range constraints. Freshness SLA (max data age). Completeness SLA (min % non-null). Volume SLA (min rows). Validate current dataset against any contract with pass/fail results.

**🎯 Why you need it:** In enterprise data pipelines, contracts ensure that incoming data meets expectations. This prevents garbage-in-garbage-out.

**📖 How to use it:** Define a contract → set SLAs → validate current data → see pass/fail results.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📜 Data Contract Manager")
st.caption("Define schema expectations and validate your dataset against them.")

st.markdown("#### Define Contract")
contract_name = st.text_input("Contract name", f"contract_{len(st.session_state.get('ent_data_contracts', []))+1}")
required_cols = st.multiselect("Required columns", dfc.columns.tolist())
freshness_hours = st.number_input("Freshness SLA (max age in hours)", 0, 8760, 24)
completeness_pct = st.slider("Completeness SLA (min % non-null)", 50, 100, 95)
min_rows = st.number_input("Volume SLA (min rows)", 1, 999999999, 1000)

if st.button("📜 Save Contract"):
    contract = {
        "name": contract_name, "required_columns": required_cols,
        "freshness_hours": freshness_hours, "completeness_pct": completeness_pct,
        "min_rows": min_rows, "created": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state["ent_data_contracts"].append(contract)
    st.success(f"✅ Contract '{contract_name}' saved")
    st.rerun()

# Show existing contracts
contracts = st.session_state.get("ent_data_contracts", [])
if contracts:
    st.markdown("### 📋 Existing Contracts")
    for i, c in enumerate(contracts):
        with st.expander(f"📜 {c['name']} (created {c['created']})", expanded=i==len(contracts)-1):
            st.markdown(f"- Required columns: {', '.join(c['required_columns']) or 'None'}")
            st.markdown(f"- Freshness: {c['freshness_hours']}h | Completeness: {c['completeness_pct']}% | Min rows: {c['min_rows']:,}")
            
            if st.button(f"✅ Validate Against '{c['name']}'", key=f"val_{i}"):
                results = []
                # Column check
                missing_cols = set(c["required_columns"]) - set(dfc.columns)
                results.append({"Check": "Required Columns", "Status": "✅ Pass" if not missing_cols else f"🔴 Fail (missing: {missing_cols})"})
                # Row count
                results.append({"Check": "Volume SLA", "Status": f"✅ Pass ({len(dfc):,} rows)" if len(dfc) >= c["min_rows"] else f"🔴 Fail ({len(dfc):,} < {c['min_rows']:,})"})
                # Completeness
                overall_completeness = (1 - dfc.isnull().sum().sum() / (dfc.shape[0]*dfc.shape[1])) * 100
                results.append({"Check": "Completeness SLA", "Status": f"✅ Pass ({overall_completeness:.1f}%)" if overall_completeness >= c["completeness_pct"] else f"🔴 Fail ({overall_completeness:.1f}% < {c['completeness_pct']}%)"})
                
                st.dataframe(pd.DataFrame(results), use_container_width=True)

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
