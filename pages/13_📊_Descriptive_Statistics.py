"""
Module 13: Descriptive Statistics — DataScience Flow v9.5
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




st.set_page_config(page_title="Descriptive Statistics | DataScience Flow", page_icon="📊", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📊 DESCRIPTIVE STATISTICS</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** Computes comprehensive descriptive statistics for every numeric column — mean, std, median, IQR, min/max, skewness, kurtosis, confidence intervals, normality tests (Shapiro-Wilk & Anderson-Darling), and Q-Q plots.

**🎯 Why you need it:** Before any advanced analysis, you need to understand your data's central tendency, spread, and distribution shape. This module answers: is my data normally distributed? How spread out is it? Where do 95% of values fall?

**📖 How to use it:** Select a column → view full statistics → check normality tests → examine Q-Q plots → export stats as CSV.
""")

if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded. Please upload a file from the Home page sidebar.")
    st.stop()

dfc = st.session_state["df_cleaned"]
st.session_state.get("steps_done", set()).add("stats")


# Quick numeric summary
numeric_cols = dfc.select_dtypes(include=np.number).columns.tolist()
if not numeric_cols:
    st.warning("No numeric columns found.")
    st.stop()

st.markdown("### 📊 All Numeric Columns Summary")
desc = dfc[numeric_cols].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
st.dataframe(desc.round(4), use_container_width=True)

st.markdown("### 🔬 Individual Column Deep-Dive")
target = st.selectbox("Select a numeric column", numeric_cols)
from scipy import stats as scipy_stats
s = dfc[target].dropna()

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Count", f"{len(s):,}")
c2.metric("Mean", f"{s.mean():.4f}")
c3.metric("Std Dev", f"{s.std():.4f}")
c4.metric("Median", f"{s.median():.4f}")
c5.metric("Skewness", f"{s.skew():.4f}")
c6.metric("Kurtosis", f"{s.kurtosis():.4f}")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Min", f"{s.min():.4f}")
c2.metric("25% (Q1)", f"{s.quantile(0.25):.4f}")
c3.metric("75% (Q3)", f"{s.quantile(0.75):.4f}")
c4.metric("Max", f"{s.max():.4f}")

st.markdown("### 📈 Distribution & Normality")
try:
    ci = scipy_stats.norm.interval(0.95, loc=s.mean(), scale=s.std()/np.sqrt(len(s)))
    st.markdown(f"**95% Confidence Interval:** [{ci[0]:.4f}, {ci[1]:.4f}]")
except: pass

col1, col2 = st.columns(2)
with col1:
    # Histogram + KDE
    fig = px.histogram(s, nbins=40, template="plotly_dark", color_discrete_sequence=["#00d9a7"],
        title=f"Distribution of {target}", marginal="box")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    # Q-Q plot
    qq = scipy_stats.probplot(s, dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qq[0][0], y=qq[0][1], mode='markers', marker=dict(color="#00d9a7", size=6)))
    fig.add_trace(go.Scatter(x=qq[0][0], y=qq[1][0]*qq[0][0] + qq[1][1], mode='lines',
        line=dict(color="#f85149", dash="dash")))
    fig.update_layout(title=f"Q-Q Plot — {target}", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# Normality tests
st.markdown("### 🧪 Normality Tests")
st.caption("Lower p-value → less likely to be normally distributed (p < 0.05 typically means non-normal).")
try:
    if len(s) <= 5000:
        shapiro_stat, shapiro_p = scipy_stats.shapiro(s.sample(min(5000, len(s)), random_state=42))
        st.markdown(f"**Shapiro-Wilk:** statistic={shapiro_stat:.4f}, p={shapiro_p:.6f} " +
            ("✅ Normal" if shapiro_p > 0.05 else "⚠️ Non-normal"))
    ad_stat, crit, sig = scipy_stats.anderson(s, dist='norm')
    st.markdown(f"**Anderson-Darling:** statistic={ad_stat:.4f} (critical values: {crit}, sig levels: {sig})")
except Exception as e:
    st.warning(f"Normality test error: {e}")

# Download
st.download_button("⬇️ Download Stats (CSV)", desc.to_csv().encode(), f"descriptive_stats.csv", "text/csv")

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
