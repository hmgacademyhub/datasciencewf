"""
Module 5: Sampling Strategies — DataScience Flow v9.5
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


st.set_page_config(page_title="Sampling Strategies | DataScience Flow", page_icon="🗂️", layout="wide")


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
## 🗂️ Sampling Strategies — Module 5

> **What is Data Sampling?** Sampling is the process of selecting a subset of data from a larger dataset. 
> Proper sampling ensures your subset is **representative** of the whole population, which is critical for 
> training ML models, performing statistical tests, and exploring large datasets efficiently.

### 🎓 Why Sampling Matters
- **Reduce computation time**: Working with 10K rows instead of 1M
- **Balanced training data**: Ensure minority classes are represented
- **Statistical validity**: Proper sampling preserves population characteristics
- **Cost efficiency**: In surveys and experiments, you cannot collect all data

### 📐 Sampling Methods Compared
| Method | How It Works | Best For | Risk |
|--------|-------------|----------|------|
| Simple Random | Every row has equal probability | General exploration | May miss rare categories |
| Stratified | Proportional sampling within groups | Preserving class balance | Requires a grouping column |
| Systematic | Every k-th row | Ordered data, quick sampling | Periodic patterns can bias |
| Cluster | Random groups, then all rows in group | Geographic/regional data | High within-cluster similarity |
| Reservoir | Streaming data, fixed-size sample | Data streams, large files | Less control over distribution |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

st.markdown("### 🎯 Sampling Configuration")
sample_fraction = st.slider("Sample fraction (%)", 1, 100, 20) / 100
random_seed = st.number_input("Random seed", value=42)

tab_random, tab_stratified, tab_systematic, tab_compare = st.tabs([
    "🎲 Random", "📊 Stratified", "🔢 Systematic", "📈 Compare"
])

with tab_random:
    st.markdown("### Simple Random Sampling")
    n_samples = int(len(df) * sample_fraction)
    sample = df.sample(n=n_samples, random_state=random_seed)
    st.metric("Sample size", f"{len(sample):,} / {len(df):,}")
    st.dataframe(sample.head(20), use_container_width=True)
    if st.button("📥 Apply Random Sample"):
        st.session_state["df_cleaned"] = sample
        st.success("Random sample applied!")

with tab_stratified:
    st.markdown("### Stratified Sampling")
    st.info("""**What is Stratified Sampling?** The dataset is divided into groups (strata) based on a categorical column, 
    and samples are taken proportionally from each group. This ensures every group is represented in the same proportion 
    as in the original data.""")
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    if cat_cols:
        strat_col = st.selectbox("Stratify by column", cat_cols, key="strat_col")
        try:
            sample = df.groupby(strat_col, group_keys=False).apply(
                lambda x: x.sample(frac=sample_fraction, random_state=random_seed)
            )
            st.metric("Sample size", f"{len(sample):,} / {len(df):,}")
            
            # Show distribution comparison
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Original Distribution**")
                orig_dist = df[strat_col].value_counts(normalize=True).round(3)
                st.dataframe(orig_dist)
            with c2:
                st.markdown("**Sample Distribution**")
                samp_dist = sample[strat_col].value_counts(normalize=True).round(3)
                st.dataframe(samp_dist)
            
            st.dataframe(sample.head(20), use_container_width=True)
            if st.button("📥 Apply Stratified Sample"):
                st.session_state["df_cleaned"] = sample
                st.success("Stratified sample applied!")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("No categorical columns found for stratification.")

with tab_systematic:
    st.markdown("### Systematic Sampling")
    k = max(1, int(1 / sample_fraction))
    start = st.number_input("Start index", min_value=0, max_value=k-1, value=0)
    sample = df.iloc[start::k]
    st.metric("Sample size", f"{len(sample):,} / {len(df):,}")
    st.info(f"Taking every {k}-th row starting at index {start}")
    st.dataframe(sample.head(20), use_container_width=True)
    if st.button("📥 Apply Systematic Sample"):
        st.session_state["df_cleaned"] = sample
        st.success("Systematic sample applied!")

with tab_compare:
    st.markdown("### 📈 Sampling Comparison")
    n_samples = int(len(df) * sample_fraction)
    results = []
    
    # Random
    random_sample = df.sample(n=min(n_samples, len(df)), random_state=random_seed)
    
    # Systematic
    k = max(1, len(df) // n_samples)
    systematic_sample = df.iloc[::k]
    
    results.append({"Method": "Original", "Rows": len(df)})
    results.append({"Method": "Random", "Rows": len(random_sample)})
    results.append({"Method": "Systematic", "Rows": len(systematic_sample)})
    
    # Compare numeric column distributions
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        compare_col = st.selectbox("Compare distribution of", num_cols, key="compare_col")
        compare_data = pd.DataFrame({
            "Original": df[compare_col].describe(),
            "Random": random_sample[compare_col].describe(),
            "Systematic": systematic_sample[compare_col].describe(),
        })
        st.dataframe(compare_data.round(3), use_container_width=True)
    
    st.dataframe(pd.DataFrame(results), use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Stratified sampling is the gold standard when your data has imbalanced categories. 
Random sampling is simplest but can underrepresent minority groups. 
Systematic sampling is fast but beware of periodic patterns in your data.

📚 **Next Steps:** After sampling, proceed to Module 6 (Data Exploration) to understand your sample.
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
