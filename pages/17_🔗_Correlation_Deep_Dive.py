"""
Module 17: Correlation Deep Dive — DataScience Flow v9.5
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


st.set_page_config(page_title="Correlation Deep Dive | DataScience Flow", page_icon="🔗", layout="wide")


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
## 🔗 Correlation Deep Dive — Module 17

> **What is Correlation?** Correlation measures the strength and direction of the linear (or monotonic) 
> relationship between two variables. Understanding correlations is essential for feature selection, 
> detecting multicollinearity, and building interpretable models.

### 🎓 Why Study Correlations?
- **Feature Selection**: Highly correlated features are redundant — remove one
- **Multicollinearity**: Correlated predictors distort regression coefficients and model interpretation
- **Causal Hypotheses**: Correlation does not imply causation, but it points to where to investigate
- **Data Understanding**: Knowing which variables move together builds domain intuition

### 📐 Correlation Methods
| Method | Measures | Range | When to Use |
|--------|----------|-------|-------------|
| Pearson | Linear relationship | -1 to +1 | Continuous, normally distributed |
| Spearman | Monotonic relationship | -1 to +1 | Ordinal, non-normal, rank-based |
| Kendall | Rank concordance | -1 to +1 | Small samples, many ties |
| Partial | Relationship controlling for others | -1 to +1 | Confounding variables |

### ⚠️ Key Warning: VIF (Variance Inflation Factor)
- VIF > 5: Moderate multicollinearity
- VIF > 10: Severe multicollinearity — consider removing the feature
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()

if len(num_cols) < 2:
    st.warning("Need at least 2 numeric columns for correlation analysis.")
    st.stop()

tab_pearson, tab_spearman, tab_partial, tab_vif, tab_pair = st.tabs([
    "📊 Pearson", "📈 Spearman", "🎯 Partial", "⚠️ VIF", "🔗 Pairwise"
])

with tab_pearson:
    st.markdown("### Pearson Correlation Matrix")
    st.info("""**Pearson correlation** measures the linear relationship between two continuous variables. 
    A value of +1 means perfect positive linear relationship, -1 means perfect negative, and 0 means no linear relationship.
    
    **Assumptions:** Both variables should be continuous and approximately normally distributed.""")
    
    corr = df[num_cols].corr(method='pearson')
    st.dataframe(corr.round(3), use_container_width=True)
    
    # Visualize
    import plotly.express as px
    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdBu_r", range_color=[-1, 1],
                    title="Pearson Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)
    
    # Strong correlations
    st.markdown("#### 🔥 Strong Correlations (|r| > 0.7)")
    strong_corrs = []
    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            r = corr.iloc[i, j]
            if abs(r) > 0.7:
                strong_corrs.append({
                    "Variable 1": corr.columns[i],
                    "Variable 2": corr.columns[j],
                    "Correlation": round(r, 3),
                    "Strength": "Very Strong" if abs(r) > 0.9 else "Strong"
                })
    if strong_corrs:
        st.dataframe(pd.DataFrame(strong_corrs), use_container_width=True)
    else:
        st.info("No strong correlations (|r| > 0.7) found.")

with tab_spearman:
    st.markdown("### Spearman Rank Correlation")
    st.info("""**Spearman correlation** measures the monotonic relationship between two variables 
    using their ranks rather than actual values. It is robust to outliers and does not assume normality.
    
    **When to use:** When your data is ordinal, has outliers, or the relationship is monotonic but not linear.""")
    
    corr_sp = df[num_cols].corr(method='spearman')
    fig = px.imshow(corr_sp, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdBu_r", range_color=[-1, 1],
                    title="Spearman Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)

with tab_partial:
    st.markdown("### Partial Correlation")
    st.info("""**Partial correlation** measures the relationship between two variables while controlling 
    for the effect of one or more other variables. This helps identify if a correlation is genuine or 
    driven by a confounding variable.
    
    **Example:** If income and education are correlated, partial correlation with age controlled tells you 
    if the relationship exists independent of age.""")
    
    c1, c2 = st.columns(2)
    with c1:
        var1 = st.selectbox("Variable 1", num_cols, key="p_var1")
    with c2:
        var2 = st.selectbox("Variable 2", [c for c in num_cols if c != var1], key="p_var2")
    
    control_vars = st.multiselect("Control variables (hold constant)", 
                                   [c for c in num_cols if c not in [var1, var2]])
    
    if var1 and var2:
        from scipy import stats
        if control_vars:
            try:
                # Residualize approach for partial correlation
                from sklearn.linear_model import LinearRegression
                X_control = df[control_vars].fillna(df[control_vars].mean())
                y1 = df[var1].fillna(df[var1].mean())
                y2 = df[var2].fillna(df[var2].mean())
                
                lr1 = LinearRegression().fit(X_control, y1)
                lr2 = LinearRegression().fit(X_control, y2)
                
                resid1 = y1 - lr1.predict(X_control)
                resid2 = y2 - lr2.predict(X_control)
                
                partial_r, partial_p = stats.pearsonr(resid1, resid2)
                
                # Also compute zero-order correlation
                zero_r, zero_p = stats.pearsonr(y1, y2)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Zero-order Correlation", f"{zero_r:.4f}")
                    st.caption(f"p-value: {zero_p:.4e}")
                with c2:
                    st.metric("Partial Correlation", f"{partial_r:.4f}")
                    st.caption(f"p-value: {partial_p:.4e}")
                
                diff = abs(zero_r) - abs(partial_r)
                if diff > 0.1:
                    st.warning(f"⚠️ Correlation changed by {diff:.3f} after controlling for {control_vars}. "
                              f"The original correlation may be partially confounded.")
                else:
                    st.success("✅ Correlation is robust — not significantly affected by control variables.")
            except Exception as e:
                st.error(f"Error computing partial correlation: {e}")
        else:
            r, p = stats.pearsonr(df[var1].dropna(), df[var2].dropna())
            st.metric("Pearson r", f"{r:.4f}")
            st.metric("p-value", f"{p:.4e}")
            st.info("Select control variables to compute partial correlation.")

with tab_vif:
    st.markdown("### ⚠️ Variance Inflation Factor (VIF)")
    st.info("""**VIF** quantifies how much the variance of a regression coefficient is inflated due to 
    multicollinearity. A VIF of 5 means the coefficient's variance is 5x larger than it would be if the 
    variable were uncorrelated with other predictors.
    
    **Thresholds:** VIF > 5 = Moderate concern | VIF > 10 = Severe multicollinearity""")
    
    try:
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        X = df[num_cols].dropna()
        if len(X) > 0:
            vif_data = []
            for i, col in enumerate(X.columns):
                vif = variance_inflation_factor(X.values, i)
                vif_data.append({
                    "Variable": col,
                    "VIF": round(vif, 2),
                    "Status": "🔴 Severe" if vif > 10 else "🟡 Moderate" if vif > 5 else "🟢 OK"
                })
            vif_df = pd.DataFrame(vif_data)
            st.dataframe(vif_df, use_container_width=True)
            
            severe = vif_df[vif_df["VIF"] > 10]
            if len(severe) > 0:
                st.warning(f"⚠️ {len(severe)} variables have severe multicollinearity (VIF > 10):")
                st.write(severe["Variable"].tolist())
        else:
            st.warning("Not enough data after dropping nulls for VIF calculation.")
    except Exception as e:
        st.error(f"VIF calculation error: {e}")

with tab_pair:
    st.markdown("### 🔗 Pairwise Correlation Explorer")
    col1 = st.selectbox("Column 1", num_cols, key="pair_col1")
    col2 = st.selectbox("Column 2", [c for c in num_cols if c != col1], key="pair_col2")
    
    from scipy import stats
    valid = df[[col1, col2]].dropna()
    if len(valid) > 2:
        pearson_r, pearson_p = stats.pearsonr(valid[col1], valid[col2])
        spearman_r, spearman_p = stats.spearmanr(valid[col1], valid[col2])
        kendall_r, kendall_p = stats.kendalltau(valid[col1], valid[col2])
        
        metrics_data = {
            "Method": ["Pearson", "Spearman", "Kendall"],
            "Correlation": [f"{pearson_r:.4f}", f"{spearman_r:.4f}", f"{kendall_r:.4f}"],
            "p-value": [f"{pearson_p:.4e}", f"{spearman_p:.4e}", f"{kendall_p:.4e}"],
            "Significant?": ["Yes ✅" if p < 0.05 else "No ❌" for p in [pearson_p, spearman_p, kendall_p]]
        }
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)
        
        import plotly.express as px
        fig = px.scatter(valid, x=col1, y=col2, title=f"{col1} vs {col2}",
                        trendline="ols", opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough valid data points.")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Always check both Pearson and Spearman correlations. If they differ significantly, 
your relationship may be monotonic but not linear. Always check VIF before building regression models.

📚 **Next Steps:** Use insights from correlation analysis in Module 17 (Feature Engineering) and Module 17 (Feature Selection).
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
