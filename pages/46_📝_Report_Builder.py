"""
Module 46: Report Builder — DataScience Flow v9.5
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



st.set_page_config(page_title="Report Builder | DataScience Flow", page_icon="📝", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📝 REPORT BUILDER</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Custom multi-section report composer. Select findings → arrange sections → export as styled HTML. Professional presentation-ready output.

**🎯 Why you need it:** Combine insights from multiple modules into one polished, exportable report — perfect for stakeholders and documentation.

**📖 How to use it:** Add report sections → arrange order → preview → export as HTML.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📝 Custom Report Builder")
st.caption("Build a custom report by adding sections. Export as styled HTML.")

if "report_sections" not in st.session_state:
    st.session_state["report_sections"] = []

section_type = st.selectbox("Add section", [
    "Dataset Overview", "Missing Values Summary", "Key Statistics", 
    "Correlation Analysis", "Distribution Insights", "Custom Text"
])

if section_type == "Dataset Overview":
    title = st.text_input("Section title", "Dataset Overview")
    if st.button("➕ Add Section"):
        text = f"<h3>{title}</h3><p>Dataset: <strong>{st.session_state.get('filename','N/A')}</strong></p><p>Rows: {dfc.shape[0]:,} | Columns: {dfc.shape[1]}</p>"
        st.session_state["report_sections"].append(text)
        st.rerun()

elif section_type == "Missing Values Summary":
    title = st.text_input("Section title", "Missing Values Summary")
    if st.button("➕ Add Section"):
        miss = dfc.isnull().sum()
        miss_pct = (miss/len(dfc)*100).round(2)
        text = f"<h3>{title}</h3><ul>"
        for col in dfc.columns:
            if miss[col] > 0:
                text += f"<li><strong>{col}</strong>: {miss[col]} ({miss_pct[col]}%)</li>"
        text += "</ul>"
        if miss.sum() == 0: text += "<p>✅ No missing values.</p>"
        st.session_state["report_sections"].append(text)
        st.rerun()

elif section_type == "Key Statistics":
    title = st.text_input("Section title", "Key Statistics")
    if st.button("➕ Add Section"):
        num = dfc.select_dtypes(include=np.number).columns[:10]
        text = f"<h3>{title}</h3><table border='1' cellpadding='5'><tr><th>Column</th><th>Mean</th><th>Std</th><th>Min</th><th>Max</th></tr>"
        for c in num:
            text += f"<tr><td>{c}</td><td>{dfc[c].mean():.2f}</td><td>{dfc[c].std():.2f}</td><td>{dfc[c].min():.2f}</td><td>{dfc[c].max():.2f}</td></tr>"
        text += "</table>"
        st.session_state["report_sections"].append(text)
        st.rerun()

elif section_type == "Correlation Analysis":
    title = st.text_input("Section title", "Correlation Analysis")
    if st.button("➕ Add Section"):
        num = dfc.select_dtypes(include=np.number).columns
        if len(num) >= 2:
            corr = dfc[num].corr()
            text = f"<h3>{title}</h3><ul>"
            for i in range(len(num)):
                for j in range(i+1, len(num)):
                    if abs(corr.iloc[i,j]) > 0.5:
                        text += f"<li>{num[i]} ↔ {num[j]}: r={corr.iloc[i,j]:.3f}</li>"
            text += "</ul>"
            st.session_state["report_sections"].append(text)
            st.rerun()

elif section_type == "Custom Text":
    title = st.text_input("Section title", "Custom Section")
    custom = st.text_area("Content (HTML allowed)", height=100)
    if st.button("➕ Add Section") and custom:
        text = f"<h3>{title}</h3><p>{custom}</p>"
        st.session_state["report_sections"].append(text)
        st.rerun()

if st.session_state["report_sections"]:
    st.markdown("### 📄 Report Preview")
    full_report = "<html><head><style>body{font-family:Arial,sans-serif;background:#fff;color:#333;padding:2rem;}h2{color:#00d9a7;}h3{color:#333;}table{border-collapse:collapse;}th{background:#00d9a7;color:#fff;padding:8px;}td{padding:6px;border:1px solid #ddd;}</style></head><body><h1>📊 DataScience Flow Report</h1><p>Built by Adewale Samson Adeagbo | HMG Concepts</p><p>Generated: """ + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M") + "</p><hr>"
    for i, section in enumerate(st.session_state["report_sections"]):
        full_report += section
    full_report += "<hr><p style='color:#888;font-size:0.8em;'>DataScience Flow Suite v7.0 | HMG Concepts | Lagos, Nigeria</p></body></html>"
    
    st.markdown(full_report[:3000] + ("..." if len(full_report) > 3000 else ""), unsafe_allow_html=True)
    
    if st.button("🗑️ Clear All Sections"):
        st.session_state["report_sections"] = []
        st.rerun()
    
    st.download_button("⬇️ Download Report (HTML)", full_report.encode(), "dataflow_report.html", "text/html")

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
