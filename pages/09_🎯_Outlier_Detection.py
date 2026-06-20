"""
Module 9: Outlier Detection — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Outlier Detection | DataScience Flow", page_icon="🎯", layout="wide")


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

st.markdown("""
## 🎯 Outlier Detection — Module 9

> **What are Outliers?** Outliers are data points that differ significantly from other observations. 
> They can be genuine rare events or data errors. The challenge is distinguishing between the two.

### 🎓 Why Outliers Matter
- **Statistical distortion**: Outliers pull means and inflate variances
- **Model impact**: Many ML algorithms are sensitive to outliers (linear regression, K-means)
- **Data quality signal**: Unexpected outliers may indicate data collection errors
- **Business insights**: Genuine outliers can represent fraud, viral events, or opportunities

### 📐 Detection Methods
| Method | How It Works | Best For | Sensitive to |
|--------|-------------|----------|-------------|
| IQR | Values outside Q1-1.5×IQR to Q3+1.5×IQR | General use, non-normal data | Extreme skewness |
| Z-Score | Values > 3 standard deviations from mean | Normally distributed data | Other outliers inflating std |
| Modified Z-Score | Uses median and MAD instead of mean/std | Robust to outliers | Very small MAD |
| Isolation Forest | Random partitioning isolates outliers | High-dimensional data | Parameter tuning |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()

if not num_cols:
    st.warning("No numeric columns found for outlier detection.")
    st.stop()

col = st.selectbox("Select column", num_cols)
method = st.selectbox("Detection method", ["IQR", "Z-Score", "Modified Z-Score"])

# Detection
data = df[col].dropna()
outlier_mask = pd.Series(False, index=data.index)

if method == "IQR":
    q1, q3 = data.quantile(0.25), data.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_mask = (data < lower) | (data > upper)
    st.info(f"**IQR Bounds:** Lower = {lower:.4f}, Upper = {upper:.4f}, IQR = {iqr:.4f}")
    
elif method == "Z-Score":
    threshold = st.slider("Z-score threshold", 1.0, 5.0, 3.0, 0.5)
    z_scores = np.abs((data - data.mean()) / data.std())
    outlier_mask = z_scores > threshold
    st.info(f"**Z-Score Threshold:** |z| > {threshold}")
    
elif method == "Modified Z-Score":
    threshold = st.slider("Modified Z-score threshold", 1.0, 5.0, 3.5, 0.5)
    median = data.median()
    mad = np.median(np.abs(data - median))
    if mad == 0:
        mad = 1e-10
    modified_z = 0.6745 * (data - median) / mad
    outlier_mask = np.abs(modified_z) > threshold
    st.info(f"**Modified Z-Score Threshold:** |Mz| > {threshold}")

n_outliers = outlier_mask.sum()
st.metric("Outliers detected", f"{n_outliers}", f"{n_outliers/len(data)*100:.1f}%")

# Visualisation
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


fig = go.Figure()
fig.add_trace(go.Histogram(x=data[~outlier_mask], name="Normal", marker_color='#6C63FF'))
fig.add_trace(go.Histogram(x=data[outlier_mask], name="Outliers", marker_color='#FF6B6B'))
fig.update_layout(title=f"Outlier Detection: {col} ({method})", barmode='overlay', opacity=0.7)
st.plotly_chart(fig, use_container_width=True)

# Box plot
fig2 = px.box(data, y=col, title=f"Box Plot: {col}")
st.plotly_chart(fig2, use_container_width=True)

# Outlier rows
if n_outliers > 0:
    with st.expander(f"📋 View {n_outliers} Outlier Rows"):
        st.dataframe(df.loc[outlier_mask[outlier_mask].index].head(50), use_container_width=True)

# Handling
st.markdown("---")
st.markdown("### 🛠️ Outlier Handling Strategy")
strategy = st.selectbox("Strategy", [
    "Keep (no change)", "Remove outliers", "Cap at bounds (Winsorize)",
    "Replace with median", "Replace with mean", "Log transform (positive values only)",
    "Flag only (add column)"
])

if st.button("✅ Apply Strategy"):
    cleaned = st.session_state["df_cleaned"].copy()
    
    if strategy == "Keep (no change)":
        st.info("No changes made.")
    elif strategy == "Remove outliers":
        cleaned = cleaned[~outlier_mask.reindex(cleaned.index, fill_value=False)]
        st.session_state["df_cleaned"] = cleaned
        st.success(f"Removed {n_outliers} outliers. Dataset now has {len(cleaned)} rows.")
    elif strategy == "Cap at bounds (Winsorize)":
        if method == "IQR":
            cleaned.loc[cleaned[col] < lower, col] = lower
            cleaned.loc[cleaned[col] > upper, col] = upper
        else:
            lower_bound = data[~outlier_mask].min()
            upper_bound = data[~outlier_mask].max()
            cleaned.loc[cleaned[col] < lower_bound, col] = lower_bound
            cleaned.loc[cleaned[col] > upper_bound, col] = upper_bound
        st.session_state["df_cleaned"] = cleaned
        st.success("Capped outliers at bounds.")
    elif strategy == "Replace with median":
        median_val = data[~outlier_mask].median()
        cleaned.loc[outlier_mask.reindex(cleaned.index, fill_value=False), col] = median_val
        st.session_state["df_cleaned"] = cleaned
        st.success(f"Replaced outliers with median: {median_val:.4f}")
    elif strategy == "Replace with mean":
        mean_val = data[~outlier_mask].mean()
        cleaned.loc[outlier_mask.reindex(cleaned.index, fill_value=False), col] = mean_val
        st.session_state["df_cleaned"] = cleaned
        st.success(f"Replaced outliers with mean: {mean_val:.4f}")
    elif strategy == "Log transform (positive values only)":
        if (cleaned[col] > 0).all():
            cleaned[col] = np.log1p(cleaned[col])
            st.session_state["df_cleaned"] = cleaned
            st.success("Applied log(1+x) transform.")
        else:
            st.error("Log transform requires all positive values.")
    elif strategy == "Flag only (add column)":
        cleaned[f"{col}_is_outlier"] = outlier_mask.reindex(cleaned.index, fill_value=False)
        st.session_state["df_cleaned"] = cleaned
        st.success(f"Added flag column: {col}_is_outlier")
    
    st.rerun()

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Never remove outliers without understanding why they exist. 
A genuine outlier (e.g., a viral post with 1M views) contains valuable information. 
Always document which method you used and why.

📚 **Next Steps:** After handling outliers, move to Module 9 (Data Quality Audit) for a comprehensive quality scorecard.
""")

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
