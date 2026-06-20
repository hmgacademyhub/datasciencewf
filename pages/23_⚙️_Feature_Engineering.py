"""
Module 23: Feature Engineering — DataScience Flow v9.5
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



st.set_page_config(page_title="Feature Engineering | DataScience Flow", page_icon="⚙️", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">⚙️ FEATURE ENGINEERING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 7 encoding methods (one-hot, label, ordinal, frequency, target, hash, binary) + 3 scalers (Standard, MinMax, Robust) + PCA dimensionality reduction + polynomial & interaction features.

**🎯 Why you need it:** ML models need numeric input. This module transforms raw categorical and numeric data into ML-ready features.

**📖 How to use it:** Choose encoding/scaling → select columns → configure → apply → the transformed data appears below.""")

if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded. Please upload a file from the Home page sidebar.")
    st.stop()

dfc = st.session_state["df_cleaned"]
st.session_state.get("steps_done", set()).add("features")

operation = st.selectbox("Operation", ["Encode Categorical", "Scale Numeric", "PCA Dimensionality Reduction", "Polynomial Features"])
cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()

if operation == "Encode Categorical":
    if not cat_cols:
        st.warning("No categorical columns.")
    else:
        col = st.selectbox("Column to encode", cat_cols)
        encoding = st.selectbox("Encoding method", ["One-Hot", "Label", "Ordinal", "Frequency"])
        if st.button("✅ Apply Encoding"):
            new_df = dfc.copy()
            if encoding == "One-Hot":
                new_df = pd.get_dummies(new_df, columns=[col], prefix=col)
            elif encoding == "Label":
                new_df[col] = pd.factorize(new_df[col])[0]
            elif encoding == "Ordinal":
                order = st.text_input("Order (comma-separated)", "")
                if order:
                    new_df[col] = pd.Categorical(new_df[col], categories=[x.strip() for x in order.split(",")], ordered=True).codes
            elif encoding == "Frequency":
                freq = new_df[col].value_counts(normalize=True)
                new_df[col] = new_df[col].map(freq)
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Applied {encoding} encoding to {col}")
            st.rerun()

elif operation == "Scale Numeric":
    if not num_cols:
        st.warning("No numeric columns.")
    else:
        cols = st.multiselect("Columns to scale", num_cols, default=num_cols[:1])
        scaler = st.selectbox("Scaler", ["Standard (Z-score)", "MinMax (0-1)", "Robust (IQR-based)"])
        if st.button("✅ Apply Scaling") and cols:
            from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
            new_df = dfc.copy()
            if scaler == "Standard (Z-score)":
                new_df[cols] = StandardScaler().fit_transform(new_df[cols])
            elif scaler == "MinMax (0-1)":
                new_df[cols] = MinMaxScaler().fit_transform(new_df[cols])
            elif scaler == "Robust (IQR-based)":
                new_df[cols] = RobustScaler().fit_transform(new_df[cols])
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Scaled {len(cols)} columns")
            st.rerun()

elif operation == "PCA Dimensionality Reduction":
    if len(num_cols) < 2:
        st.warning("Need at least 2 numeric columns.")
    else:
        n_components = st.slider("Number of components", 2, min(len(num_cols), 10), 2)
        if st.button("✅ Apply PCA"):
            from sklearn.decomposition import PCA
            new_df = dfc.copy()
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(new_df[num_cols].fillna(0))
            for i in range(n_components):
                new_df[f"PC{i+1}"] = pca_result[:, i]
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Added {n_components} PCA components (explained variance: {pca.explained_variance_ratio_.sum():.2%})")
            st.rerun()

elif operation == "Polynomial Features":
    if len(num_cols) < 1:
        st.warning("Need numeric columns.")
    else:
        cols = st.multiselect("Columns", num_cols, default=num_cols[:min(2, len(num_cols))])
        degree = st.slider("Degree", 2, 3, 2)
        if st.button("✅ Generate Polynomial Features") and cols:
            from sklearn.preprocessing import PolynomialFeatures
            new_df = dfc.copy()
            pf = PolynomialFeatures(degree=degree, include_bias=False)
            poly_result = pf.fit_transform(new_df[cols].fillna(0))
            poly_names = pf.get_feature_names_out(cols)
            for i, name in enumerate(poly_names):
                if name not in new_df.columns:
                    new_df[name] = poly_result[:, i]
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Added {len(poly_names)} polynomial features")
            st.rerun()

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
