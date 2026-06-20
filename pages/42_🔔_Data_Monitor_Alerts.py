"""
Module 42: Data Monitor & Alerts — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Monitor & Alerts | DataScience Flow", page_icon="🔔", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔔 DATA MONITOR & ALERTS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 10 rule types: missing threshold, value range, duplicate %, valid values enum, row count, mean range, unique count, negative checks, outlier %, custom SQL. Pass/fail/warn dashboard with health gauge.

**🎯 Why you need it:** Set automated quality rules to detect data issues before they affect your analysis. Like a smoke detector for your data pipeline.

**📖 How to use it:** Define rules → run all checks → review pass/fail/warn results → export alert report.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔔 Data Quality Monitoring Rules")
st.caption("Define rules to automatically check your data quality.")

if st.button("➕ Add New Rule"):
    st.session_state["show_rule_form"] = True

if st.session_state.get("show_rule_form"):
    rule_type = st.selectbox("Rule type", [
        "missing_threshold", "value_range", "duplicate_pct", "valid_values",
        "row_count", "mean_range", "unique_count", "negative_check", "outlier_pct", "custom_sql"
    ])
    name = st.text_input("Rule name", f"rule_{len(st.session_state.get('monitored_rules', []))+1}")
    severity = st.selectbox("Severity", ["Critical", "Major", "Warning"])
    col = st.selectbox("Target column", dfc.columns.tolist())
    
    params = {}
    if rule_type == "missing_threshold":
        params["threshold_pct"] = st.number_input("Max missing %", 0.0, 100.0, 10.0)
    elif rule_type == "value_range":
        params["min_val"] = st.number_input("Min value", value=0.0)
        params["max_val"] = st.number_input("Max value", value=100.0)
    elif rule_type == "duplicate_pct":
        params["threshold_pct"] = st.number_input("Max duplicate %", 0.0, 100.0, 5.0)
    elif rule_type == "valid_values":
        params["values"] = st.text_input("Valid values (comma-separated)", "")
    elif rule_type == "row_count":
        params["min_rows"] = st.number_input("Minimum rows", 0, 999999999, 1)
    elif rule_type == "mean_range":
        params["min_mean"] = st.number_input("Min mean", value=0.0)
        params["max_mean"] = st.number_input("Max mean", value=100.0)
    elif rule_type == "unique_count":
        params["min_unique"] = st.number_input("Min unique values", 1, 999999, 2)
    
    if st.button("✅ Save Rule"):
        st.session_state["monitored_rules"].append({"name": name, "type": rule_type, "column": col, "severity": severity, "params": params})
        st.session_state["show_rule_form"] = False
        st.success(f"✅ Rule '{name}' saved")
        st.rerun()

# Show existing rules
rules = st.session_state.get("monitored_rules", [])
if rules:
    st.markdown(f"### 📋 {len(rules)} Active Rules")
    
    if st.button("🔍 Run All Checks"):
        results = []
        for rule in rules:
            col = rule["column"]
            tp = rule["type"]
            status = "✅ Pass"
            detail = ""
            
            try:
                if tp == "missing_threshold":
                    miss = dfc[col].isna().mean() * 100
                    if miss > rule["params"]["threshold_pct"]:
                        status = "🔴 Fail"
                    detail = f"Missing: {miss:.1f}% (threshold: {rule['params']['threshold_pct']}%)"
                elif tp == "value_range":
                    out_of_range = ((dfc[col] < rule["params"]["min_val"]) | (dfc[col] > rule["params"]["max_val"])).sum()
                    if out_of_range > 0:
                        status = "🔴 Fail"
                    detail = f"{out_of_range} values outside [{rule['params']['min_val']}, {rule['params']['max_val']}]"
                elif tp == "duplicate_pct":
                    dup = dfc[col].duplicated().sum() / len(dfc) * 100
                    if dup > rule["params"]["threshold_pct"]:
                        status = "🟡 Warn" if dup < rule["params"]["threshold_pct"] * 2 else "🔴 Fail"
                    detail = f"Duplicates: {dup:.1f}% (threshold: {rule['params']['threshold_pct']}%)"
                elif tp == "row_count":
                    if len(dfc) < rule["params"]["min_rows"]:
                        status = "🔴 Fail"
                    detail = f"Rows: {len(dfc):,} (min: {rule['params']['min_rows']:,})"
                elif tp == "mean_range":
                    m = dfc[col].mean()
                    if m < rule["params"]["min_mean"] or m > rule["params"]["max_mean"]:
                        status = "🔴 Fail"
                    detail = f"Mean: {m:.2f} (range: [{rule['params']['min_mean']}, {rule['params']['max_mean']}])"
                else:
                    status = "⚪ N/A"
                    detail = "Rule type validation not implemented in this view"
            except Exception as e:
                status = "⚠️ Error"
                detail = str(e)
            
            results.append({**rule, "status": status, "detail": detail})
        
        res_df = pd.DataFrame(results)
        st.dataframe(res_df, use_container_width=True)
        
        fails = sum(1 for r in results if "Fail" in r["status"])
        warns = sum(1 for r in results if "Warn" in r["status"])
        passes = sum(1 for r in results if "Pass" in r["status"])
        
        c1,c2,c3 = st.columns(3)
        c1.metric("✅ Passes", passes)
        c2.metric("🟡 Warnings", warns)
        c3.metric("🔴 Failures", fails)
        
        st.download_button("⬇️ Alert Report (CSV)", res_df.to_csv(index=False).encode(), "monitor_alerts.csv", "text/csv")

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
