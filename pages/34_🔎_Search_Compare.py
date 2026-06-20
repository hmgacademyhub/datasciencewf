"""
Module 34: Search & Compare — DataScience Flow v9.5
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



st.set_page_config(page_title="Search & Compare | DataScience Flow", page_icon="🔎", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🔎 SEARCH & COMPARE</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Full-text search across all columns. Multi-condition segment builder (AND/OR logic). Side-by-side statistical comparison of two subsets with overlay charts.

**🎯 Why you need it:** Quickly find specific records or compare two segments of your data statistically — like "customers who churned vs retained."

**📖 How to use it:** Enter search term → view matching rows → OR build segments with conditions → compare side-by-side.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🔎 Full-Text Search")
search = st.text_input("Search across all columns", placeholder="Type to search...")
if search:
    mask = pd.Series(False, index=dfc.index)
    for col in dfc.columns:
        mask |= dfc[col].astype(str).str.contains(search, case=False, na=False)
    results = dfc[mask]
    st.markdown(f"**{len(results):,} matching rows**")
    st.dataframe(results.head(100), use_container_width=True)
    st.download_button("⬇️ Download Results", results.to_csv(index=False).encode(), "search_results.csv", "text/csv")

st.markdown("---")
st.markdown("### 📊 Segment Builder & Compare")
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
if num_cols:
    col = st.selectbox("Compare by column", num_cols)
    split_col = st.selectbox("Split by (categorical)", dfc.columns.tolist())
    groups = dfc[split_col].dropna().unique()
    if len(groups) >= 2:
        g1 = st.selectbox("Group A", groups, index=0)
        g2 = st.selectbox("Group B", groups, index=min(1, len(groups)-1))
        if st.button("📊 Compare"):
            d1 = dfc[dfc[split_col]==g1][col].dropna()
            d2 = dfc[dfc[split_col]==g2][col].dropna()
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric(f"Mean ({g1})", f"{d1.mean():.4f}")
            c2.metric(f"Mean ({g2})", f"{d2.mean():.4f}")
            c3.metric("Diff", f"{d2.mean()-d1.mean():.4f}")
            c4.metric(f"Std ({g1})", f"{d1.std():.4f}")
            c5.metric(f"Std ({g2})", f"{d2.std():.4f}")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=d1, name=str(g1), opacity=0.7, marker_color="#00d9a7"))
            fig.add_trace(go.Histogram(x=d2, name=str(g2), opacity=0.7, marker_color="#4f8ef7"))
            fig.update_layout(barmode="overlay", template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

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
