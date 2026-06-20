"""
Module 2: Data Simulation — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Simulation | DataScience Flow", page_icon="🧪", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🧪 DATA SIMULATION</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Generate synthetic datasets (normal, uniform, categorical distributions). Bootstrap sampling from existing data. Gaussian/uniform noise injection. Row multiplier.

**🎯 Why you need it:** Synthetic data is invaluable for testing, teaching, and prototyping without exposing real data. Bootstrap helps assess statistical uncertainty.

**📖 How to use it:** Choose simulation type → configure parameters → generate → download or append to current data.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🧪 Data Simulator")
sim_type = st.selectbox("Simulation type", ["Synthetic Dataset", "Bootstrap Sampling", "Add Noise", "Row Multiplier"])

if sim_type == "Synthetic Dataset":
    n_rows = st.slider("Rows", 50, 5000, 500)
    n_cols = st.slider("Columns", 1, 10, 5)
    if st.button("🧬 Generate Synthetic Data"):
        data = {}
        for i in range(n_cols):
            dist = np.random.choice(["normal", "uniform", "exponential", "integer"])
            if dist == "normal":
                data[f"feature_{i+1}"] = np.random.normal(0, 1, n_rows)
            elif dist == "uniform":
                data[f"feature_{i+1}"] = np.random.uniform(0, 100, n_rows)
            elif dist == "exponential":
                data[f"feature_{i+1}"] = np.random.exponential(1, n_rows)
            else:
                data[f"feature_{i+1}"] = np.random.randint(0, 100, n_rows)
        data["category"] = np.random.choice(["A", "B", "C"], n_rows)
        syn_df = pd.DataFrame(data)
        st.session_state["df_cleaned"] = syn_df
        st.session_state["df"] = syn_df
        st.success(f"✅ Generated {n_rows}×{n_cols+1} synthetic dataset")
        st.dataframe(syn_df.head(10), use_container_width=True)
        st.download_button("⬇️ Download", syn_df.to_csv(index=False).encode(), "synthetic_data.csv", "text/csv")

elif sim_type == "Bootstrap Sampling":
    n_samples = st.slider("Number of bootstrap samples", 100, 5000, 1000)
    if st.button("🎲 Bootstrap"):
        boot = dfc.sample(n=n_samples, replace=True, random_state=42).reset_index(drop=True)
        st.markdown(f"**Bootstrap sample:** {boot.shape[0]:,} rows")
        st.dataframe(boot.head(10), use_container_width=True)
        st.download_button("⬇️ Download Bootstrap", boot.to_csv(index=False).encode(), "bootstrap_sample.csv", "text/csv")

elif sim_type == "Add Noise":
    num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
    if num_cols:
        cols = st.multiselect("Columns to add noise to", num_cols)
        noise_level = st.slider("Noise level (%)", 1, 50, 10)
        noise_type = st.selectbox("Noise type", ["Gaussian", "Uniform"])
        if st.button("🔊 Add Noise") and cols:
            new_df = dfc.copy()
            for col in cols:
                scale = noise_level / 100 * new_df[col].std()
                if noise_type == "Gaussian":
                    new_df[col] += np.random.normal(0, scale, len(new_df))
                else:
                    new_df[col] += np.random.uniform(-scale, scale, len(new_df))
            st.session_state["df_cleaned"] = new_df
            st.success(f"✅ Added {noise_level}% {noise_type} noise to {len(cols)} columns")
            st.rerun()

elif sim_type == "Row Multiplier":
    factor = st.slider("Multiply rows by", 2, 10, 2)
    if st.button("📋 Multiply Rows"):
        new_df = pd.concat([dfc] * factor, ignore_index=True)
        st.session_state["df_cleaned"] = new_df
        st.success(f"✅ Multiplied: {new_df.shape[0]:,} rows")
        st.rerun()

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
