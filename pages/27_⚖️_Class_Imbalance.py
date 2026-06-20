"""
Module 27: Class Imbalance — DataScience Flow v9.5
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



st.set_page_config(page_title="Class Imbalance | DataScience Flow", page_icon="⚖️", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">⚖️ CLASS IMBALANCE</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** SMOTE oversampling (synthetic minority), random oversampling & undersampling, class weight calculator, before/after distribution comparison.

**🎯 Why you need it:** Imbalanced classes (e.g., 95% normal, 5% fraud) cause ML models to ignore the minority class. This module fixes that bias.

**📖 How to use it:** Select target column → view class distribution → choose balancing strategy → apply → compare before/after.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### ⚖️ Class Imbalance Handler")
target = st.selectbox("Target column (classification)", dfc.columns.tolist())
vc = dfc[target].value_counts()
st.markdown(f"**Class distribution:**")
st.dataframe(vc.reset_index().rename(columns={"index": "Class", target: "Count"}), use_container_width=True)

fig = px.pie(values=vc.values, names=vc.index, template="plotly_dark", title="Class Distribution")
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

minority_pct = vc.min() / vc.sum() * 100
if minority_pct < 30:
    st.warning(f"⚠️ Imbalance detected! Minority class is only {minority_pct:.1f}%")
    strategy = st.selectbox("Balancing strategy", ["SMOTE (oversampling)", "Random Oversampling", "Random Undersampling"])
    if st.button("✅ Balance Classes"):
        try:
            from imblearn.over_sampling import SMOTE
            from imblearn.under_sampling import RandomUnderSampler
            num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
            X = dfc[num_cols].fillna(0)
            y = dfc[target]
            if strategy == "SMOTE (oversampling)":
                X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
            elif strategy == "Random Oversampling":
                from imblearn.over_sampling import RandomOverSampler
                X_res, y_res = RandomOverSampler(random_state=42).fit_resample(X, y)
            else:
                X_res, y_res = RandomUnderSampler(random_state=42).fit_resample(X, y)
            new_df = pd.DataFrame(X_res, columns=num_cols)
            new_df[target] = y_res
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Balanced! New shape: {new_df.shape[0]:,} rows")
            st.bar_chart(y_res.value_counts())
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.success(f"✅ Classes relatively balanced (minority: {minority_pct:.1f}%)")

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
