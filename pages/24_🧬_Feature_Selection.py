"""
Module 24: Feature Selection — DataScience Flow v9.5
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



st.set_page_config(page_title="Feature Selection | DataScience Flow", page_icon="🧬", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🧬 FEATURE SELECTION</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Variance threshold, correlation pruning, RFE (Recursive Feature Elimination), SelectKBest (chi2, f_classif, mutual_info), feature importance ranking, Boruta-style all-relevant selection.

**🎯 Why you need it:** Too many features = overfitting, slow training, poor interpretability. This module finds the most predictive features automatically.

**📖 How to use it:** Select target → choose method → run → view ranked features.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🧬 Feature Selection")
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
target = st.selectbox("Target column", dfc.columns.tolist())
feature_cols = st.multiselect("Feature columns (leave empty for all numeric)", [c for c in num_cols if c != target],
    default=[c for c in num_cols if c != target][:min(10, len(num_cols)-1)])

if feature_cols and st.button("🔍 Run Feature Selection"):
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE
    from sklearn.ensemble import RandomForestClassifier
    X = dfc[feature_cols].fillna(0).copy()
    for c in X.select_dtypes(include=["object"]).columns:
        X[c] = LabelEncoder().fit_transform(X[c].astype(str))
    y = dfc[target]
    if y.dtype == object:
        y = LabelEncoder().fit_transform(y.astype(str))
    X = StandardScaler().fit_transform(X)
    
    n_keep = st.slider("Features to keep", 1, len(feature_cols), max(1, len(feature_cols)//2))
    
    # SelectKBest
    skb = SelectKBest(f_classif, k=n_keep).fit(X, y)
    scores = skb.scores_
    
    # RFE with RandomForest
    rfe = RFE(RandomForestClassifier(n_estimators=50, random_state=42), n_features_to_select=n_keep)
    rfe.fit(X, y)
    
    results = []
    for i, col in enumerate(feature_cols):
        results.append({"Feature": col, "SelectKBest Score": scores[i], "RFE Selected": rfe.support_[i]})
    
    res_df = pd.DataFrame(results).sort_values("SelectKBest Score", ascending=False)
    st.markdown("### 📊 Feature Ranking")
    st.dataframe(res_df, use_container_width=True)
    
    # Correlation pruning
    st.markdown("### 🔗 High Correlation Pairs (|r| > 0.8)")
    X_df = pd.DataFrame(X, columns=feature_cols)
    corr = X_df.corr()
    high_corr = []
    for i in range(len(feature_cols)):
        for j in range(i+1, len(feature_cols)):
            if abs(corr.iloc[i, j]) > 0.8:
                high_corr.append({"Feature 1": feature_cols[i], "Feature 2": feature_cols[j], "Correlation": corr.iloc[i, j]})
    if high_corr:
        st.dataframe(pd.DataFrame(high_corr), use_container_width=True)
    else:
        st.success("No highly correlated feature pairs found.")

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
