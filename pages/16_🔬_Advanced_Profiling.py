"""
Module 16: Advanced Profiling — DataScience Flow v9.5
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



st.set_page_config(page_title="Advanced Profiling | DataScience Flow", page_icon="🔬", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔬 ADVANCED PROFILING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Distribution fitting (Normal, Lognormal, Exponential, Uniform, Gamma). Correlation relationship maps. Composite anomaly scoring. Cardinality & type quality analysis. Advanced statistical profiling.

**🎯 Why you need it:** Go beyond basic stats. Fit theoretical distributions, understand complex relationships, and score anomalies with composite metrics.

**📖 How to use it:** Select advanced analysis → column → review distribution fits → correlation maps → composite scores.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔬 Advanced Statistical Profiling")
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
if not num_cols:
    st.warning("No numeric columns.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Distribution Fitting", "🗺️ Correlation Map", "🎯 Composite Anomaly Score"])

with tab1:
    col = st.selectbox("Column for distribution fitting", num_cols)
    from scipy import stats as scipy_stats
    s = dfc[col].dropna()
    
    distributions = {
        "Normal": scipy_stats.norm, "Lognormal": scipy_stats.lognorm,
        "Exponential": scipy_stats.expon, "Uniform": scipy_stats.uniform,
        "Gamma": scipy_stats.gamma
    }
    
    if st.button("📊 Fit Distributions"):
        results = []
        x = np.linspace(s.min(), s.max(), 100)
        for name, dist in distributions.items():
            try:
                params = dist.fit(s)
                ks_stat, ks_p = scipy_stats.kstest(s, dist.name, args=params)
                results.append({"Distribution": name, "KS Statistic": ks_stat, "p-value": ks_p, "Best Fit?": ""})
            except:
                results.append({"Distribution": name, "KS Statistic": 1, "p-value": 0, "Best Fit?": "Error"})
        
        res_df = pd.DataFrame(results).sort_values("KS Statistic")
        best = res_df.iloc[0]
        best_idx = res_df.index[0]
        st.markdown(f"**Best fit: {best['Distribution']}** (KS stat: {best['KS Statistic']:.4f})")
        st.dataframe(res_df, use_container_width=True)
        
        # Plot best fit
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=s, nbinsx=40, histnorm="probability density", name="Data",
            marker_color="#00d9a7", opacity=0.6))
        best_dist = list(distributions.values())[best_idx]
        best_params = best_dist.fit(s)
        y_fit = best_dist.pdf(x, *best_params)
        fig.add_trace(go.Scatter(x=x, y=y_fit, mode="lines", name=f"Best Fit: {best['Distribution']}",
            line=dict(color="#f85149", width=2)))
        fig.update_layout(template="plotly_dark", title=f"Distribution Fit — {col}",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🗺️ Correlation Relationship Map")
    if len(num_cols) >= 2:
        corr = dfc[num_cols].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1, text=corr.values.round(2), texttemplate="%{text}"))
        fig.update_layout(title="Correlation Map", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=max(400, min(800, 25*len(num_cols))))
        st.plotly_chart(fig, use_container_width=True)
        
        # Top correlations
        pairs = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                pairs.append((num_cols[i], num_cols[j], corr.iloc[i,j]))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        st.markdown("### Top Correlations")
        for c1, c2, r in pairs[:5]:
            st.markdown(f"- {c1} ↔ {c2}: r = {r:.3f}")

with tab3:
    st.markdown("### 🎯 Composite Anomaly Scoring")
    st.caption("Scores each row by combining multiple anomaly indicators.")
    
    if len(num_cols) >= 2:
        selected = st.multiselect("Columns for composite score", num_cols, default=num_cols[:min(5, len(num_cols))])
        if selected and st.button("🎯 Compute Composite Score"):
            from scipy import stats as scipy_stats
            scores = pd.DataFrame(index=dfc.index)
            scores["composite"] = 0
            
            for col in selected:
                s = dfc[col].fillna(dfc[col].median())
                z = np.abs(scipy_stats.zscore(s))
                z = np.clip(z, 0, 5)
                scores[col + "_z"] = z
                scores["composite"] += z
            
            scores["composite"] = scores["composite"] / len(selected)
            scores["level"] = pd.cut(scores["composite"], bins=[0, 1, 2, 3, 10],
                labels=["Normal", "Mild", "Moderate", "Severe"])
            
            st.markdown(f"**Anomaly Distribution:**")
            dist = scores["level"].value_counts()
            st.bar_chart(dist)
            
            top_anomalies = scores.nlargest(20, "composite")
            st.dataframe(top_anomalies[["composite", "level"]], use_container_width=True)

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
