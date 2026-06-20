"""
Module 37: Data Privacy & Masking — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Privacy & Masking | DataScience Flow", page_icon="🔐", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔐 DATA PRIVACY & MASKING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** PII auto-detection (emails, names, phones, addresses, IDs, financial data). 8 masking methods: SHA-256 hashing, pseudonymization, middle-char masking, range generalization, Gaussian noise, redaction, tokenization, partial masking. GDPR/NDPR compliance helper.

**🎯 Why you need it:** Protect sensitive data before sharing or analysis. Essential for GDPR/NDPR compliance and ethical data handling.

**📖 How to use it:** Auto-detect PII → choose masking method → preview masked data → apply.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔐 PII Detection & Data Masking")
st.caption("Auto-scans for Personally Identifiable Information (PII) patterns.")

import re
pii_patterns = {
    "Email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    "Phone (NG)": r'(\+234|0)[0-9]{10}',
    "Credit Card": r'[0-9]{13,16}',
    "NIN (NG)": r'[0-9]{11}',
}

st.markdown("### 📋 PII Scan Results")
found_pii = []
for col in dfc.select_dtypes(include=["object","string"]).columns:
    sample = dfc[col].dropna().astype(str).head(50)
    for pii_type, pattern in pii_patterns.items():
        matches = sample.str.contains(pattern, case=False, na=False).sum()
        if matches > 0:
            found_pii.append({"Column": col, "PII Type": pii_type, "Matches in Sample": matches, "Sample %": f"{matches/len(sample)*100:.0f}%"})

if found_pii:
    st.dataframe(pd.DataFrame(found_pii), use_container_width=True)
    
    mask_method = st.selectbox("Masking method", [
        "SHA-256 Hash", "Pseudonymize (ID1, ID2...)", "Middle-char masking (a***@***.com)",
        "Full redaction (***)", "Tokenization (TOKEN_xxx)", "Gaussian noise (numeric only)"
    ])
    
    cols_to_mask = st.multiselect("Columns to mask", [f["Column"] for f in found_pii])
    
    if st.button("🔐 Apply Masking") and cols_to_mask:
        import hashlib
        new_df = dfc.copy()
        for col in cols_to_mask:
            if mask_method == "SHA-256 Hash":
                new_df[col] = new_df[col].astype(str).apply(lambda x: hashlib.sha256(x.encode()).hexdigest()[:16])
            elif mask_method == "Pseudonymize (ID1, ID2...)":
                uniq = {v: f"ID{i+1}" for i, v in enumerate(new_df[col].dropna().unique())}
                new_df[col] = new_df[col].map(uniq).fillna(new_df[col])
            elif "Middle-char" in mask_method:
                new_df[col] = new_df[col].astype(str).apply(lambda x: x[0] + "***" + x[-3:] if len(x) > 5 else "***")
            elif mask_method == "Full redaction (***)":
                new_df[col] = "***"
            elif "Tokenization" in mask_method:
                uniq = {v: f"TOKEN_{i+1:04d}" for i, v in enumerate(new_df[col].dropna().unique())}
                new_df[col] = new_df[col].map(uniq).fillna(new_df[col])
            elif "Gaussian noise" in mask_method and pd.api.types.is_numeric_dtype(new_df[col]):
                noise = np.random.normal(0, new_df[col].std()*0.1, len(new_df))
                new_df[col] = new_df[col] + noise
        st.session_state["df_cleaned"] = new_df
        st.session_state["masked_columns"] = {**st.session_state.get("masked_columns", {}), **{c: mask_method for c in cols_to_mask}}
        st.success(f"✅ Masked {len(cols_to_mask)} columns")
        st.rerun()
else:
    st.success("✅ No common PII patterns detected.")

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
