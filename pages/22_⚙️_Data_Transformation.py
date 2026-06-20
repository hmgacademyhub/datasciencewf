"""
Module 22: Data Transformation — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription

from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)


st.set_page_config(page_title="Data Transformation | DataScience Flow", page_icon="⚙️", layout="wide")


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
## ⚙️ Data Transformation — Module 22

> **What is Data Transformation?** Transformation changes the scale or distribution of your data to make it 
> more suitable for analysis or modelling. Many ML algorithms assume normal distributions or require features 
> to be on similar scales.

### 🎓 Why Transform Data?
| Reason | Example | Transformation |
|--------|---------|---------------|
| Reduce skewness | Income data heavily right-skewed | Log transform |
| Stabilize variance | Variance increases with mean | Square root transform |
| Meet normality assumptions | For parametric tests | Box-Cox transform |
| Make relationships linear | Exponential growth patterns | Log transform |
| Create meaningful categories | Age → Age Groups | Binning/Discretization |
| Flag conditions | Temperature > 30°C | Binarization |

### 📐 Common Transformations
| Transform | Formula | Effect | Use When |
|-----------|---------|--------|----------|
| Log | log(x) | Compresses right tail | Right-skewed, positive values |
| Square Root | √x | Mild compression | Counts, moderate skew |
| Reciprocal | 1/x | Strong compression | Very right-skewed |
| Box-Cox | Adaptive | Makes data normal | When optimal transform is unknown |
| Yeo-Johnson | Adaptive | Handles neg values | When data has zero/neg values |
| Min-Max | (x-min)/(max-min) | Scales to [0,1] | Neural networks, KNN |
| Standard | (x-mean)/std | Zero mean, unit var | Linear models, SVM |
| Binning | Cut into groups | Continuous → Categorical | Non-linear effects |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()

tab_transform, tab_binning, tab_formula = st.tabs(["🔄 Numeric Transform", "📦 Binning", "📝 Custom Formula"])

with tab_transform:
    col = st.selectbox("Select column to transform", num_cols)
    transform_type = st.selectbox("Transformation", [
        "Log (natural)", "Log10", "Square Root", "Reciprocal (1/x)",
        "Square (x²)", "Cube (x³)", "Absolute Value",
        "Box-Cox", "Yeo-Johnson",
        "Min-Max Scaling", "Standard Scaling (Z-score)", "Robust Scaling"
    ])
    
    if col:
        import plotly.express as px
        c1, c2 = st.columns(2)
        
        # Before
        with c1:
            fig_before = px.histogram(df[col].dropna(), nbins=30, title=f"Before: {col}")
            st.plotly_chart(fig_before, use_container_width=True)
            st.metric("Skewness", f"{df[col].skew():.4f}")
        
        # Apply transform
        transformed = df[col].copy()
        try:
            if transform_type == "Log (natural)":
                if (df[col] <= 0).any():
                    st.warning("Log requires positive values. Adding 1 to shift.")
                    transformed = np.log1p(df[col] - df[col].min() + 1)
                else:
                    transformed = np.log(df[col])
            elif transform_type == "Log10":
                if (df[col] <= 0).any():
                    st.warning("Log10 requires positive values. Adding 1 to shift.")
                    transformed = np.log10(df[col] - df[col].min() + 1)
                else:
                    transformed = np.log10(df[col])
            elif transform_type == "Square Root":
                if (df[col] < 0).any():
                    st.warning("Square root requires non-negative values. Using absolute values.")
                    transformed = np.sqrt(df[col].abs())
                else:
                    transformed = np.sqrt(df[col])
            elif transform_type == "Reciprocal (1/x)":
                transformed = 1 / (df[col].replace(0, np.nan))
            elif transform_type == "Square (x²)":
                transformed = df[col] ** 2
            elif transform_type == "Cube (x³)":
                transformed = df[col] ** 3
            elif transform_type == "Absolute Value":
                transformed = df[col].abs()
            elif transform_type in ["Box-Cox", "Yeo-Johnson"]:
                from sklearn.preprocessing import PowerTransformer
                method = 'box-cox' if transform_type == "Box-Cox" else 'yeo-johnson'
                pt = PowerTransformer(method=method, standardize=True)
                vals = df[col].dropna().values.reshape(-1, 1)
                if method == 'box-cox' and (vals <= 0).any():
                    st.warning("Box-Cox requires strictly positive values. Using Yeo-Johnson instead.")
                    pt = PowerTransformer(method='yeo-johnson', standardize=True)
                transformed_vals = pt.fit_transform(vals)
                transformed = pd.Series(index=df[col].dropna().index, data=transformed_vals.flatten())
            elif transform_type == "Min-Max Scaling":
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                vals = df[col].dropna().values.reshape(-1, 1)
                transformed_vals = scaler.fit_transform(vals)
                transformed = pd.Series(index=df[col].dropna().index, data=transformed_vals.flatten())
            elif transform_type == "Standard Scaling (Z-score)":
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                vals = df[col].dropna().values.reshape(-1, 1)
                transformed_vals = scaler.fit_transform(vals)
                transformed = pd.Series(index=df[col].dropna().index, data=transformed_vals.flatten())
            elif transform_type == "Robust Scaling":
                from sklearn.preprocessing import RobustScaler
                scaler = RobustScaler()
                vals = df[col].dropna().values.reshape(-1, 1)
                transformed_vals = scaler.fit_transform(vals)
                transformed = pd.Series(index=df[col].dropna().index, data=transformed_vals.flatten())
            
            # After
            with c2:
                fig_after = px.histogram(transformed.dropna(), nbins=30, title=f"After: {transform_type}")
                st.plotly_chart(fig_after, use_container_width=True)
                st.metric("Skewness", f"{transformed.skew():.4f}")
            
            new_col_name = st.text_input("New column name", f"{col}_{transform_type.split()[0].lower()}")
            if st.button("✅ Apply Transformation"):
                st.session_state["df_cleaned"][new_col_name] = transformed
                st.success(f"Column '{new_col_name}' added!")
                st.rerun()
        except Exception as e:
            st.error(f"Transformation error: {e}")

with tab_binning:
    st.markdown("### 📦 Binning / Discretization")
    st.info("""**What is Binning?** Binning converts a continuous variable into categorical groups (bins). 
    This is useful for creating age groups, income brackets, or score bands.
    
    **Methods:** Equal-width (same interval size) or Equal-frequency (same number per bin, i.e., quantiles).""")
    
    bin_col = st.selectbox("Column to bin", num_cols, key="bin_col")
    bin_method = st.selectbox("Binning method", ["Equal Width", "Equal Frequency (Quantiles)", "Custom Cut Points"])
    
    if bin_method in ["Equal Width", "Equal Frequency (Quantiles)"]:
        n_bins = st.slider("Number of bins", 2, 20, 5, key="n_bins")
    
    if bin_method == "Custom Cut Points":
        cut_points = st.text_input("Cut points (comma-separated)", "0, 25, 50, 75, 100")
    
    if st.button("📦 Apply Binning"):
        try:
            if bin_method == "Equal Width":
                binned = pd.cut(df[bin_col], bins=n_bins)
            elif bin_method == "Equal Frequency (Quantiles)":
                binned = pd.qcut(df[bin_col], q=n_bins, duplicates='drop')
            else:
                cuts = [float(x.strip()) for x in cut_points.split(",")]
                binned = pd.cut(df[bin_col], bins=cuts)
            
            bin_col_name = f"{bin_col}_binned"
            st.session_state["df_cleaned"][bin_col_name] = binned
            
            st.success(f"Created binned column: {bin_col_name}")
            st.dataframe(st.session_state["df_cleaned"][[bin_col, bin_col_name]].head(20), use_container_width=True)
            
            # Show distribution
            import plotly.express as px
            fig = px.histogram(st.session_state["df_cleaned"], x=bin_col_name, title=f"Distribution of {bin_col_name}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Binning error: {e}")

with tab_formula:
    st.markdown("### 📝 Custom Formula Builder")
    st.info("""Write a Python expression using your column names. Available variables: 
    all your column names, plus `np` (NumPy) and `pd` (Pandas).
    
    **Examples:** 
    - `revenue / cost` → Profit ratio
    - `np.log(price + 1)` → Log-transformed price
    - `(score - score.mean()) / score.std()` → Z-score
    """)
    
    formula = st.text_area("Formula (Python expression)", "col1 + col2")
    new_name = st.text_input("New column name", "custom_column")
    
    if st.button("📝 Apply Formula"):
        try:
            # Build namespace with column data
            namespace = {"np": np, "pd": pd}
            for col in df.columns:
                namespace[col] = df[col]
            
            result = eval(formula, namespace)
            st.session_state["df_cleaned"][new_name] = result
            st.success(f"Column '{new_name}' created!")
            st.dataframe(st.session_state["df_cleaned"][[new_name]].head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Formula error: {e}")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Transformations change your data's distribution and scale. Always check the 
before/after distribution and skewness. Log transforms are the most common for right-skewed data.

📚 **Next Steps:** After transforming, check Module 22 (Feature Engineering) for encoding and scaling.
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
