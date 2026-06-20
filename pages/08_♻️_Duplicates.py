"""
Module 8: Duplicates — DataScience Flow v9.5
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


st.set_page_config(page_title="Duplicates | DataScience Flow", page_icon="♻️", layout="wide")


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
## ♻️ Duplicates — Module 8

> **What are Duplicates?** Duplicate records are rows that have identical values across all or some columns. 
> They inflate counts, bias statistics, and cause models to overfit on repeated data.

### 🎓 Types of Duplicates
| Type | Description | Example |
|------|-------------|---------|
| Exact duplicates | All columns identical | Same row entered twice |
| Partial duplicates | Key columns identical, others differ | Same customer ID, different timestamps |
| Near duplicates | Very similar but not identical | Slight spelling variations |

### 📐 When to Remove vs Keep
- **Remove**: Accidental double-entry, test data mixed in
- **Keep**: Legitimate repeated events (same customer buying twice), time-series data with same values at different times
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

tab_exact, tab_partial, tab_handle = st.tabs(["🔍 Exact Duplicates", "🔗 Partial Key Duplicates", "🛠️ Handle Duplicates"])

with tab_exact:
    exact_dupes = df.duplicated(keep=False)
    n_dupes = exact_dupes.sum()
    n_unique_dupes = df[df.duplicated(keep='first')].shape[0]
    
    st.metric("Exact duplicate rows", f"{n_dupes}", f"{n_dupes/len(df)*100:.1f}% of total")
    st.metric("Rows to remove (keeping first)", f"{n_unique_dupes}")
    
    if n_dupes > 0:
        st.markdown("#### Duplicate Rows Preview")
        st.dataframe(df[exact_dupes].head(20), use_container_width=True)
        
        import plotly.express as px
        rate_data = pd.DataFrame({
            "Type": ["Unique", "Duplicates"],
            "Count": [len(df) - n_dupes, n_dupes]
        })
        fig = px.pie(rate_data, values="Count", names="Type", title="Duplicate Rate")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No exact duplicates found!")

with tab_partial:
    st.markdown("### 🔗 Partial Key Duplicate Detection")
    st.info("Select the columns that form a 'unique key'. Rows with the same key are flagged as partial duplicates.")
    
    key_cols = st.multiselect("Key columns (define uniqueness)", df.columns.tolist())
    
    if key_cols:
        partial_dupes = df.duplicated(subset=key_cols, keep=False)
        n_partial = partial_dupes.sum()
        
        st.metric("Partial duplicates by key", f"{n_partial}", f"{n_partial/len(df)*100:.1f}% of total")
        
        if n_partial > 0:
            st.dataframe(df[partial_dupes].sort_values(key_cols).head(30), use_container_width=True)

with tab_handle:
    st.markdown("### 🛠️ Handle Duplicates")
    
    strategy = st.selectbox("Handling strategy", [
        "Remove exact duplicates (keep first)",
        "Remove exact duplicates (keep last)",
        "Remove all exact duplicates",
        "Flag duplicates (add column)",
        "Remove partial key duplicates",
    ])
    
    if strategy == "Remove partial key duplicates":
        key_cols = st.multiselect("Key columns for partial dedup", df.columns.tolist(), key="partial_key")
    
    if st.button("✅ Apply Strategy"):
        cleaned = df.copy()
        
        if strategy == "Remove exact duplicates (keep first)":
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates(keep='first')
            removed = before - len(cleaned)
        elif strategy == "Remove exact duplicates (keep last)":
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates(keep='last')
            removed = before - len(cleaned)
        elif strategy == "Remove all exact duplicates":
            before = len(cleaned)
            cleaned = cleaned.drop_duplicates(keep=False)
            removed = before - len(cleaned)
        elif strategy == "Flag duplicates (add column)":
            cleaned["is_duplicate"] = cleaned.duplicated(keep='first')
            removed = "N/A (flagged, not removed)"
        elif strategy == "Remove partial key duplicates":
            if key_cols:
                before = len(cleaned)
                cleaned = cleaned.drop_duplicates(subset=key_cols, keep='first')
                removed = before - len(cleaned)
            else:
                st.warning("Select key columns for partial dedup.")
                st.stop()
        
        st.success(f"Removed/flagged: {removed} rows")
        st.session_state["df_cleaned"] = cleaned
        st.rerun()

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Always understand WHY duplicates exist before removing them. 
Some duplicates are legitimate (e.g., a customer making multiple purchases). Removing them could lose valuable information.

📚 **Next Steps:** After handling duplicates, move to Module 8 (Outlier Detection).
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
