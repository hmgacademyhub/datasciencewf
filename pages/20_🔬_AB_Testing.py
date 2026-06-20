"""
Module 20: AB Testing Calculator — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription

from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)


st.set_page_config(page_title="AB Testing | DataScience Flow", page_icon="🔬", layout="wide")


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
## 🔬 AB Testing Calculator — Module 20

> **What is AB Testing?** AB testing (split testing) compares two versions (A=control, B=variant) to determine 
> which performs better. It is the gold standard for making data-driven decisions in product design, marketing, 
> and feature development.

### 🎓 Key Concepts
| Concept | Definition | Why It Matters |
|---------|-----------|----------------|
| Control (A) | The existing version | Baseline for comparison |
| Variant (B) | The new version | What you're testing |
| Statistical Significance | Probability the result is not by chance | Confidence in decision |
| p-value | Probability of seeing this result if no real difference exists | Typically need p < 0.05 |
| Power | Probability of detecting a real effect | Typically target 80%+ |
| Minimum Detectable Effect | Smallest meaningful difference | Determines sample size |
| Confidence Interval | Range where true difference likely falls | Shows precision of estimate |
| Lift | Percentage improvement of B over A | Business impact metric |

### 📐 When to Use AB Testing
- Comparing two page designs for conversion rate
- Testing email subject lines for open rate
- Evaluating pricing changes for revenue impact
- Assessing feature changes for user engagement
""")

tab_calculator, tab_significance, tab_from_data, tab_guide = st.tabs([
    "📐 Sample Size Calculator", "📊 Significance Test", "📁 Test from Data", "📖 Guide"
])

with tab_calculator:
    st.markdown("### 📐 Sample Size Calculator")
    st.info("Calculate how many users/samples you need in each group to detect a meaningful difference.")
    
    baseline_rate = st.number_input("Baseline conversion rate (%)", min_value=0.1, max_value=100.0, value=10.0, step=0.5) / 100
    mde = st.number_input("Minimum detectable effect (relative %)", min_value=1.0, max_value=100.0, value=20.0, step=1.0) / 100
    alpha = st.selectbox("Significance level (α)", [0.01, 0.05, 0.10], index=1)
    power = st.selectbox("Statistical power", [0.80, 0.85, 0.90, 0.95], index=0)
    test_type = st.selectbox("Test type", ["Two-sided", "One-sided"])
    
    if st.button("📊 Calculate Sample Size"):
        try:
            z_alpha = stats.norm.ppf(1 - alpha/2 if test_type == "Two-sided" else alpha)
            z_beta = stats.norm.ppf(power)
            
            p1 = baseline_rate
            p2 = baseline_rate * (1 + mde)
            p_avg = (p1 + p2) / 2
            
            n = ((z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + 
                  z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p2 - p1) ** 2
            n = int(np.ceil(n))
            
            st.success(f"### 📊 Required Sample Size per Group: **{n:,}**")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Per Group", f"{n:,}")
            c2.metric("Total (A + B)", f"{2*n:,}")
            c3.metric("Baseline Rate", f"{baseline_rate*100:.1f}%")
            c4.metric("Expected Variant Rate", f"{p2*100:.2f}%")
            
            st.markdown("#### 📋 Test Parameters Summary")
            st.markdown(f"""
            | Parameter | Value |
            |-----------|-------|
            | Baseline rate | {baseline_rate*100:.1f}% |
            | Minimum detectable effect | {mde*100:.1f}% (relative) |
            | Expected variant rate | {p2*100:.2f}% |
            | Absolute difference | {(p2-p1)*100:.2f}% |
            | Significance level (α) | {alpha} |
            | Statistical power | {power} |
            | Test type | {test_type} |
            | **Sample size per group** | **{n:,}** |
            | **Total sample needed** | **{2*n:,}** |
            """)
        except Exception as e:
            st.error(f"Calculation error: {e}")

with tab_significance:
    st.markdown("### 📊 Statistical Significance Test")
    st.info("Enter your test results to determine if the difference is statistically significant.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🅰️ Control Group")
        a_visitors = st.number_input("Visitors/Users (A)", min_value=1, value=10000, key="a_vis")
        a_conversions = st.number_input("Conversions (A)", min_value=0, max_value=a_visitors, value=1000, key="a_conv")
    with c2:
        st.markdown("#### 🅱️ Variant Group")
        b_visitors = st.number_input("Visitors/Users (B)", min_value=1, value=10000, key="b_vis")
        b_conversions = st.number_input("Conversions (B)", min_value=0, max_value=b_visitors, value=1100, key="b_conv")
    
    sig_alpha = st.selectbox("Significance level", [0.01, 0.05, 0.10], index=1, key="sig_alpha")
    
    if st.button("🔬 Test Significance"):
        p_a = a_conversions / a_visitors
        p_b = b_conversions / b_visitors
        p_pool = (a_conversions + b_conversions) / (a_visitors + b_visitors)
        
        se = np.sqrt(p_pool * (1 - p_pool) * (1/a_visitors + 1/b_visitors))
        z_score = (p_b - p_a) / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        lift = (p_b - p_a) / p_a * 100
        
        # Confidence interval
        se_diff = np.sqrt(p_a * (1 - p_a) / a_visitors + p_b * (1 - p_b) / b_visitors)
        ci_lower = (p_b - p_a) - 1.96 * se_diff
        ci_upper = (p_b - p_a) + 1.96 * se_diff
        
        is_significant = p_value < sig_alpha
        
        if is_significant:
            st.success(f"### ✅ Statistically Significant! (p = {p_value:.4f})")
            winner = "Variant B wins! 🎉" if p_b > p_a else "Control A wins! 🏆"
            st.markdown(f"**{winner}**")
        else:
            st.warning(f"### ⚠️ Not Statistically Significant (p = {p_value:.4f})")
            st.info("The difference could be due to chance. Consider running the test longer or increasing sample size.")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("A Conversion Rate", f"{p_a*100:.2f}%")
        c2.metric("B Conversion Rate", f"{p_b*100:.2f}%")
        c3.metric("Lift", f"{lift:+.2f}%")
        c4.metric("Z-score", f"{z_score:.4f}")
        
        st.markdown(f"""
        #### 📋 Detailed Results
        | Metric | Value |
        |--------|-------|
        | Control rate (A) | {p_a*100:.2f}% |
        | Variant rate (B) | {p_b*100:.2f}% |
        | Absolute difference | {(p_b-p_a)*100:.2f}% |
        | Relative lift | {lift:+.2f}% |
        | Z-score | {z_score:.4f} |
        | p-value | {p_value:.4f} |
        | 95% CI of difference | [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%] |
        | Significant at α={sig_alpha}? | {'Yes ✅' if is_significant else 'No ❌'} |
        """)

with tab_from_data:
    st.markdown("### 📁 AB Test from Your Dataset")
    st.info("If your loaded dataset contains AB test results, select the relevant columns to perform the test.")
    
    if st.session_state.get("df_cleaned") is not None:
        df = st.session_state["df_cleaned"]
        group_col = st.selectbox("Group column (A/B)", df.columns.tolist(), key="ab_group")
        metric_col = st.selectbox("Metric column", df.columns.tolist(), key="ab_metric")
        
        groups = df[group_col].dropna().unique()
        if len(groups) >= 2:
            g1, g2 = groups[0], groups[1]
            data1 = df[df[group_col] == g1][metric_col].dropna()
            data2 = df[df[group_col] == g2][metric_col].dropna()
            
            if st.button("🔬 Run Test from Data"):
                if pd.api.types.is_numeric_dtype(df[metric_col]):
                    # Continuous metric - t-test
                    t_stat, p_val = stats.ttest_ind(data1, data2)
                    st.markdown(f"**T-test:** t = {t_stat:.4f}, p = {p_val:.4f}")
                    
                    if p_val < 0.05:
                        st.success("✅ Statistically significant difference!")
                    else:
                        st.warning("⚠️ No statistically significant difference.")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Group: {g1}**")
                        st.write(f"Mean: {data1.mean():.4f}, Std: {data1.std():.4f}, N: {len(data1)}")
                    with c2:
                        st.markdown(f"**Group: {g2}**")
                        st.write(f"Mean: {data2.mean():.4f}, Std: {data2.std():.4f}, N: {len(data2)}")
                else:
                    st.info("For categorical metrics, use the Significance Test tab with aggregate counts.")
        else:
            st.warning("The group column needs at least 2 unique values.")
    else:
        st.warning("Load a dataset first.")

with tab_guide:
    st.markdown("### 📖 AB Testing Best Practices Guide")
    st.markdown("""
    ### 🏗️ Planning Your Test
    1. **Define a clear hypothesis** — "Changing X will increase Y by at least Z%"
    2. **Calculate sample size upfront** — Use the calculator above
    3. **Set your significance level** — Usually α = 0.05
    4. **Set your power** — Usually 80%
    5. **Run for the full planned duration** — Do NOT stop early when results look good

    ### ⚠️ Common Pitfalls
    - **Peeking**: Checking results repeatedly and stopping when significant → inflated false positives
    - **Novelty effect**: Users initially engage more with new features, then settle
    - **Simpson's Paradox**: Results reverse when you segment data
    - **Multiple testing**: Running many tests inflates the chance of false positives
    - **Insufficient sample size**: Underpowered tests miss real effects

    ### 📊 Interpreting Results
    - **p < 0.05** → Statistically significant (unlikely due to chance)
    - **Lift** → Practical/business significance (is the difference meaningful?)
    - **Confidence interval** → Range of plausible true values
    - Always report both statistical AND practical significance

    ### 🇳🇬 Nigerian Context
    - Consider internet connectivity issues affecting data collection
    - Account for time-of-day patterns in user behaviour
    - Mobile-first: most Nigerian users are on mobile devices
    - Weekend vs weekday patterns may be more pronounced
    """)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Statistical significance ≠ practical significance. A result can be statistically significant 
but too small to matter. Always report the **lift** and **confidence interval** alongside p-values.

📚 **Next Steps:** Use insights from AB testing in Module 20 (Hypothesis Testing) for deeper statistical analysis.
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
