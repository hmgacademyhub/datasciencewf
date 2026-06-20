"""
Module 19: Hypothesis Testing — DataScience Flow v9.5
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



st.set_page_config(page_title="Hypothesis Testing | DataScience Flow", page_icon="📐", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📐 HYPOTHESIS TESTING</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Independent T-test, Paired T-test, One-sample T-test, Chi-square + Cramér's V, One-way ANOVA + Tukey post-hoc, Mann-Whitney U, Kruskal-Wallis — all with plain-English interpretations.

**🎯 Why you need it:** Statistical tests tell you whether patterns in your data are real or just random noise. Essential for making data-driven decisions with confidence.

**📖 How to use it:** Choose a test → select columns/groups → set significance level → view results with plain-English interpretation.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


from scipy import stats as scipy_stats
st.markdown("### 🧪 Statistical Hypothesis Testing")

test_type = st.selectbox("Test type", [
    "Independent T-test", "Paired T-test", "One-sample T-test",
    "Chi-Square Test", "One-way ANOVA", "Mann-Whitney U", "Kruskal-Wallis"
])
alpha = st.slider("Significance level (α)", 0.01, 0.10, 0.05)
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()

if test_type in ["Independent T-test", "Mann-Whitney U"]:
    if not num_cols or not cat_cols:
        st.warning("Need numeric + categorical columns.")
    else:
        num_col = st.selectbox("Numeric column", num_cols)
        cat_col = st.selectbox("Group column", cat_cols)
        groups = dfc[cat_col].dropna().unique()
        if len(groups) >= 2:
            g1 = st.selectbox("Group 1", groups, index=0); g2 = st.selectbox("Group 2", groups, index=min(1, len(groups)-1))
            if st.button("Run Test"):
                d1 = dfc[dfc[cat_col]==g1][num_col].dropna(); d2 = dfc[dfc[cat_col]==g2][num_col].dropna()
                if test_type == "Independent T-test":
                    stat, p = scipy_stats.ttest_ind(d1, d2)
                else:
                    stat, p = scipy_stats.mannwhitneyu(d1, d2)
                result = "✅ Significant difference" if p < alpha else "❌ No significant difference"
                st.markdown(f"**Statistic:** {stat:.4f} | **p-value:** {p:.6f} | **Result:** {result}")
                st.markdown(f"Mean({g1}): {d1.mean():.4f} | Mean({g2}): {d2.mean():.4f}")

elif test_type == "Chi-Square Test":
    if len(cat_cols) >= 2:
        c1 = st.selectbox("Column 1", cat_cols, index=0); c2 = st.selectbox("Column 2", cat_cols, index=min(1, len(cat_cols)-1))
        if st.button("Run Chi-Square"):
            ct = pd.crosstab(dfc[c1], dfc[c2])
            chi2, p, dof, expected = scipy_stats.chi2_contingency(ct)
            result = "✅ Significant association" if p < alpha else "❌ No significant association"
            st.markdown(f"**Chi²:** {chi2:.4f} | **p-value:** {p:.6f} | **dof:** {dof} | **Result:** {result}")
            cramers_v = np.sqrt(chi2 / (ct.sum().sum() * (min(ct.shape)-1))) if min(ct.shape) > 1 else 0
            st.markdown(f"**Cramér's V (effect size):** {cramers_v:.4f}")

elif test_type == "One-way ANOVA":
    if num_cols and cat_cols:
        num_col = st.selectbox("Numeric", num_cols); cat_col = st.selectbox("Group", cat_cols)
        if st.button("Run ANOVA"):
            groups = [dfc[dfc[cat_col]==g][num_col].dropna().values for g in dfc[cat_col].dropna().unique()]
            if len(groups) >= 2:
                f_stat, p = scipy_stats.f_oneway(*groups)
                result = "✅ Significant difference between groups" if p < alpha else "❌ No significant difference"
                st.markdown(f"**F-statistic:** {f_stat:.4f} | **p-value:** {p:.6f} | **Result:** {result}")

elif test_type == "Paired T-test":
    if len(num_cols) >= 2:
        c1 = st.selectbox("Column 1", num_cols, index=0); c2 = st.selectbox("Column 2", num_cols, index=1)
        if st.button("Run Paired T-test"):
            stat, p = scipy_stats.ttest_rel(dfc[c1].dropna(), dfc[c2].dropna())
            result = "✅ Significant difference" if p < alpha else "❌ No significant difference"
            st.markdown(f"**Statistic:** {stat:.4f} | **p-value:** {p:.6f} | **Result:** {result}")

elif test_type == "One-sample T-test":
    if num_cols:
        num_col = st.selectbox("Column", num_cols); pop_mean = st.number_input("Population mean to test against", value=0.0)
        if st.button("Run One-sample T-test"):
            stat, p = scipy_stats.ttest_1samp(dfc[num_col].dropna(), pop_mean)
            result = "✅ Significantly different from population mean" if p < alpha else "❌ Not significantly different"
            st.markdown(f"**Statistic:** {stat:.4f} | **p-value:** {p:.6f} | **Result:** {result}")

elif test_type == "Kruskal-Wallis":
    if num_cols and cat_cols:
        num_col = st.selectbox("Numeric", num_cols); cat_col = st.selectbox("Group", cat_cols)
        if st.button("Run Kruskal-Wallis"):
            groups = [dfc[dfc[cat_col]==g][num_col].dropna().values for g in dfc[cat_col].dropna().unique()]
            if len(groups) >= 2:
                h_stat, p = scipy_stats.kruskal(*groups)
                result = "✅ Significant difference" if p < alpha else "❌ No significant difference"
                st.markdown(f"**H-statistic:** {h_stat:.4f} | **p-value:** {p:.6f} | **Result:** {result}")

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
