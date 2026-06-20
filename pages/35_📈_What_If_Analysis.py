"""
Module 35: What-If Analysis — DataScience Flow v9.5
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



st.set_page_config(page_title="What-If Analysis | DataScience Flow", page_icon="📈", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📈 WHAT-IF ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Business scenario simulator. Adjust columns by % change, absolute value, fixed value, multiplier, or std deviations. Sensitivity analysis with tornado charts. Monte Carlo simulation. Scenario history.

**🎯 Why you need it:** Before making business decisions, test scenarios. "What if sales drop 10%?" "What if costs double?" This module models those outcomes.

**📖 How to use it:** Select columns → define scenarios → run simulation → compare outcomes → save scenarios.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📈 What-If Scenario Simulator")
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
if not num_cols:
    st.warning("Need numeric columns.")
    st.stop()

col = st.selectbox("Column to simulate", num_cols)
adj_type = st.selectbox("Adjustment type", ["Percentage change (%)", "Absolute change (+/-)", "Set to fixed value", "Multiply by factor", "Change by N std deviations"])
adjustment = st.number_input("Value", value=0.0)

if st.button("📊 Run Simulation"):
    original_stats = {"Mean": dfc[col].mean(), "Median": dfc[col].median(), "Std": dfc[col].std(), "Min": dfc[col].min(), "Max": dfc[col].max()}
    sim = dfc[col].copy()
    if adj_type == "Percentage change (%)":
        sim = sim * (1 + adjustment / 100)
    elif adj_type == "Absolute change (+/-)":
        sim = sim + adjustment
    elif adj_type == "Set to fixed value":
        sim = pd.Series(adjustment, index=sim.index)
    elif adj_type == "Multiply by factor":
        sim = sim * adjustment
    elif adj_type == "Change by N std deviations":
        sim = sim + adjustment * dfc[col].std()
    
    new_stats = {"Mean": sim.mean(), "Median": sim.median(), "Std": sim.std(), "Min": sim.min(), "Max": sim.max()}
    
    comp = pd.DataFrame({"Original": original_stats, "Simulated": new_stats})
    comp["Change"] = comp["Simulated"] - comp["Original"]
    comp["Change %"] = ((comp["Simulated"] / comp["Original"] - 1) * 100).round(2)
    st.markdown(f"### Scenario: {adj_type} ({adjustment}) on {col}")
    st.dataframe(comp.round(4), use_container_width=True)
    
    # Tornado effect
    st.markdown("### 🌪️ Sensitivity Analysis")
    pcts = [-20, -10, -5, 0, 5, 10, 20]
    sens = []
    for p in pcts:
        sv = dfc[col] * (1 + p/100)
        sens.append({"Change %": f"{p:+d}%", "Result Mean": sv.mean(), "Result Median": sv.median()})
    sens_df = pd.DataFrame(sens)
    fig = px.bar(sens_df, x="Change %", y="Result Mean", template="plotly_dark",
        color_discrete_sequence=["#00d9a7"], title=f"Sensitivity — {col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Save scenario
    st.session_state["whatif_scenarios"].append({"col": col, "type": adj_type, "value": adjustment, "time": pd.Timestamp.now().strftime("%H:%M")})

if st.session_state.get("whatif_scenarios"):
    st.markdown("### 📋 Scenario History")
    st.dataframe(pd.DataFrame(st.session_state["whatif_scenarios"]), use_container_width=True)

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
