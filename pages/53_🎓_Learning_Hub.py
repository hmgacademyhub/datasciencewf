"""
Module 53: Learning Hub — DataScience Flow v9.5
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



st.set_page_config(page_title="Learning Hub | DataScience Flow", page_icon="🎓", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🎓 LEARNING HUB</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** 50+ interactive glossary terms, concept explainers for beginners, module-specific tips & best practices, data science quiz with explanations.

**🎯 Why you need it:** Build your data literacy while you work. Every term is explained clearly with examples — designed for absolute beginners to professionals.

**📖 How to use it:** Browse the glossary → search terms → take the quiz → learn as you go.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🎓 Data Science Glossary (50+ Terms)")
glossary = {
    "Mean": "The average — sum all values, divide by count. Best for symmetric distributions.",
    "Median": "The middle value when sorted. Better than mean when data has outliers.",
    "Mode": "The most frequent value. Useful for categorical data.",
    "Standard Deviation": "Measures how spread out your data is. Low = values cluster near the mean.",
    "IQR (Interquartile Range)": "Q3 - Q1. The range of the middle 50% of data. Robust to outliers.",
    "P-value": "Probability of seeing your result by random chance. p < 0.05 is typically 'significant'.",
    "Correlation (r)": "Strength of linear relationship (-1 to +1). 0 = no relationship. Positive = both go up together.",
    "R² (R-squared)": "How well your model fits the data. 1 = perfect fit, 0 = no fit.",
    "Overfitting": "Model memorizes training data but fails on new data. Fix with cross-validation.",
    "Cross-Validation": "Split data into folds, train on some, test on others. Shows true model performance.",
    "TF-IDF": "Term Frequency-Inverse Document Frequency. Measures word importance in text.",
    "SMOTE": "Synthetic Minority Oversampling Technique. Creates synthetic examples of minority class.",
    "PCA": "Principal Component Analysis. Reduces dimensions while preserving variance.",
    "One-Hot Encoding": "Converts categories to binary columns (0/1). E.g., 'Red' → [1,0,0], 'Blue'→[0,1,0].",
    "Normal Distribution": "Bell curve. Most values near the mean, symmetric. Common in nature.",
    "Skewness": "Asymmetry of distribution. Positive = tail to right. Negative = tail to left.",
    "Outlier": "Extreme value far from others. Can distort analysis. Detect with IQR or Z-Score.",
    "Confidence Interval": "Range where true population value likely falls. Usually 95% CI.",
    "Hypothesis Testing": "Formal method to decide if an effect is real or random. Uses p-values.",
    "F1 Score": "Harmonic mean of precision and recall. Best for imbalanced classification.",
}
search = st.text_input("🔍 Search glossary")
filtered = {k:v for k,v in glossary.items() if search.lower() in k.lower() or search.lower() in v.lower()} if search else glossary
for term, defn in filtered.items():
    st.markdown(f"**{term}** — {defn}")

st.markdown("---")
st.markdown("### 📝 Data Science Quick Quiz")
q = st.radio("What does a p-value of 0.03 mean?", 
    ["The result is definitely real", "There's a 3% chance of seeing this result if nothing is really happening", 
     "The data is 97% accurate", "The model is 3% wrong"], key="quiz1")
if st.button("Check Answer"):
    if "3%" in q: st.success("✅ Correct! p=0.03 means 3% probability of observing this result by chance alone.")
    else: st.error("❌ Not quite. A p-value is the probability of your result (or more extreme) if the null hypothesis were true.")

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
