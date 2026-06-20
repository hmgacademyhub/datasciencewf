"""
Module 4: Web Data Connector — DataScience Flow v9.5
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



st.set_page_config(page_title="Web Data Connector | DataScience Flow", page_icon="🌐", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🌐 WEB DATA CONNECTOR</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Import from URLs & APIs. Open data catalog with famous datasets (Iris, Titanic, Diamonds, Gapminder, S&P 500). API key support. JSON path navigation. Auto-detect format.

**🎯 Why you need it:** Access public datasets directly from within the platform. No need to download, save, and re-upload.

**📖 How to use it:** Choose from the open data catalog OR enter a URL → auto-detect format → load into your session.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 🌐 Open Data Catalog")
catalog = {
    "🌸 Iris (Classification)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "🚢 Titanic (Survival)": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
    "💎 Diamonds (Pricing)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv",
    "🌍 Gapminder (World Dev)": "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv",
    "🐧 Penguins (Classification)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    "📈 S&P 500 (Finance)": "https://raw.githubusercontent.com/datasets/s-and-p-500/master/data/data.csv",
}
col1, col2 = st.columns(2)
for i, (name, url) in enumerate(catalog.items()):
    with [col1, col2][i % 2]:
        if st.button(name, key=f"cat_{i}"):
            try:
                import requests
                resp = requests.get(url, timeout=10)
                df = pd.read_csv(pd.io.common.StringIO(resp.text))
                st.session_state.update({"df": df, "filename": name, "df_cleaned": df.copy()})
                st.success(f"✅ Loaded: {name} — {df.shape[0]:,}×{df.shape[1]}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")

st.markdown("---")
st.markdown("### 🔗 Custom URL Import")
url = st.text_input("Data URL (CSV, JSON, Excel)", placeholder="https://example.com/data.csv")
if st.button("📥 Fetch from URL") and url:
    try:
        import requests
        resp = requests.get(url, timeout=15)
        if url.endswith(".json"):
            df = pd.read_json(pd.io.common.StringIO(resp.text))
        elif url.endswith((".xlsx", ".xls")):
            df = pd.read_excel(pd.io.common.BytesIO(resp.content))
        else:
            df = pd.read_csv(pd.io.common.StringIO(resp.text))
        st.session_state.update({"df": df, "filename": url.split("/")[-1], "df_cleaned": df.copy()})
        st.success(f"✅ Loaded: {df.shape[0]:,}×{df.shape[1]}")
        st.dataframe(df.head(5), use_container_width=True)
        st.rerun()
    except Exception as e:
        st.error(f"Failed: {e}")

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
