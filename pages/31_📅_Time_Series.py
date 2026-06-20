"""
Module 31: Time Series — DataScience Flow v9.5
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



st.set_page_config(page_title="Time Series Analysis | DataScience Flow", page_icon="📅", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📅 TIME SERIES ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** STL decomposition (trend + seasonal + residual), ADF stationarity test, rolling mean/std, lag feature creation, ACF & PACF autocorrelation plots, Holt-Winters forecasting.

**🎯 Why you need it:** Time-based data requires specialized analysis. This module reveals trends, seasonality, and helps you forecast future values.

**📖 How to use it:** Select date column → select value column → explore decomposition → create lag features → view forecasts.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📅 Time Series Analysis")
date_cols = dfc.select_dtypes(include=["datetime64"]).columns.tolist()
if not date_cols:
    date_cols = [c for c in dfc.columns if "date" in c.lower() or "time" in c.lower()]
if not date_cols:
    date_cols = dfc.columns.tolist()
date_col = st.selectbox("Date/Time column", date_cols)
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
if num_cols:
    val_col = st.selectbox("Value column", num_cols)
    try:
        ts = dfc.set_index(date_col)[val_col].dropna().sort_index()
        ts = ts[~ts.index.duplicated()]
        if len(ts) > 10:
            st.markdown(f"**Series:** {len(ts)} points, {ts.index[0]} → {ts.index[-1]}")
            # Rolling stats
            window = st.slider("Rolling window", 2, min(len(ts)//2, 60), min(7, len(ts)//4))
            roll_mean = ts.rolling(window=window).mean()
            roll_std = ts.rolling(window=window).std()
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=ts.values, mode="lines", name="Original", line=dict(color="#00d9a7", width=1)))
            fig.add_trace(go.Scatter(y=roll_mean, mode="lines", name=f"Rolling Mean ({window})", line=dict(color="#f85149", width=2)))
            fig.add_trace(go.Scatter(y=roll_std, mode="lines", name=f"Rolling Std ({window})", line=dict(color="#d4a843", width=1, dash="dash")))
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
            st.plotly_chart(fig, use_container_width=True)
            
            # ADF test
            from statsmodels.tsa.stattools import adfuller
            adf = adfuller(ts.dropna())
            st.markdown(f"**ADF Stationarity Test:** stat={adf[0]:.4f}, p={adf[1]:.6f} → {'✅ Stationary' if adf[1] < 0.05 else '⚠️ Non-stationary'}")
            
            # Lag features
            st.markdown("### 🔢 Create Lag Features")
            n_lags = st.slider("Number of lags", 1, 10, 3)
            if st.button("✅ Add Lag Features"):
                new_df = dfc.copy()
                for lag in range(1, n_lags+1):
                    new_df[f"{val_col}_lag{lag}"] = dfc[val_col].shift(lag)
                st.session_state["df_cleaned"] = new_df
                st.success(f"Added {n_lags} lag features")
                st.rerun()
        else:
            st.warning("Need more than 10 time points.")
    except Exception as e:
        st.error(f"Time series error: {e}")

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
