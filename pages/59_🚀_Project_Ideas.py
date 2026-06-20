"""
Module 59: Project Ideas — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
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


st.set_page_config(page_title="Projects | DataFlow v9.0", page_icon="🚀", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🚀 PROJECT IDEAS & PORTFOLIO BUILDER</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** Curated data science project ideas for every skill level, complete with datasets, workflow suggestions, and portfolio-building guidance. Build real projects that demonstrate your skills.

**🎯 Why you need it:** Employers and clients care about what you've BUILT, not what you've studied. This module gives you 15 project ideas with clear, achievable roadmaps using only free tools.

**📖 How to use it:** Pick a project → get the full workflow → use DataFlow modules to complete it → add it to your portfolio.
""")

projects_db = [
    {"title": "📊 Sales Performance Dashboard", "level": "🟢 Beginner", "time": "3-5 hours",
     "desc": "Analyze sales data to find top products, best months, and regional trends. Create visualizations that tell a clear story.",
     "dataset": "Use your own sales CSV or the Sample E-commerce dataset",
     "modules": [1, 4, 5, 8, 14],
     "deliverable": "A polished dashboard with 5+ charts and a 1-page summary report."},
    {"title": "🏥 Patient Readmission Analysis", "level": "🟡 Intermediate", "time": "8-12 hours",
     "desc": "Predict which patients are likely to be readmitted within 30 days. A classic healthcare ML problem.",
     "dataset": "Diabetes dataset (built-in) or hospital discharge data",
     "modules": [1, 4, 9, 2, 7, 13, 15, 8],
     "deliverable": "ML model with 80%+ accuracy, feature importance chart, and deployment recommendations."},
    {"title": "📰 News Category Classifier (NLP)", "level": "🟡 Intermediate", "time": "10-15 hours",
     "desc": "Build a text classifier that categorizes news articles into topics. Pure NLP — no AI API!",
     "dataset": "Any text dataset with categories (news, reviews, etc.)",
     "modules": [1, 29, 7, 20, 13, 14],
     "deliverable": "TF-IDF based classifier with 75%+ accuracy, confusion matrix, and word cloud analysis."},
    {"title": "💰 Customer Churn Predictor", "level": "🟡 Intermediate", "time": "8-12 hours",
     "desc": "Predict which customers are about to leave. Critical for subscription businesses and telcos.",
     "dataset": "Telecom or subscription churn dataset",
     "modules": [1, 9, 2, 6, 7, 20, 13, 14, 8],
     "deliverable": "Churn prediction model, top churn factors identified, retention strategy recommendations."},
    {"title": "🏠 House Price Estimator", "level": "🟢 Beginner", "time": "5-8 hours",
     "desc": "Build a model that estimates house prices based on features like location, size, and bedrooms.",
     "dataset": "California Housing (built-in)",
     "modules": [1, 4, 5, 7, 13, 14],
     "deliverable": "Price prediction model, feature importance analysis, visualization of price drivers."},
    {"title": "🛒 Market Basket Analysis", "level": "🟡 Intermediate", "time": "6-10 hours",
     "desc": "Discover which products are frequently bought together. Classic retail analytics.",
     "dataset": "Transaction data (each row = one item in a basket)",
     "modules": [1, 3, 10, 4, 5, 14],
     "deliverable": "Association rules, product affinity matrix, recommendations for cross-selling."},
    {"title": "📈 Stock Price Trend Analyzer", "level": "🔴 Advanced", "time": "12-20 hours",
     "desc": "Analyze historical stock data to identify trends, seasonality, and create basic forecasts.",
     "dataset": "Any stock CSV (Yahoo Finance export)",
     "modules": [1, 17, 5, 19, 7, 13, 27, 14],
     "deliverable": "Time series decomposition, trend analysis, ADF test results, basic forecast with Holt-Winters."},
    {"title": "🎓 Student Performance Predictor", "level": "🟢 Beginner", "time": "5-8 hours",
     "desc": "Predict student grades based on study hours, attendance, and past performance. Built by a teacher!",
     "dataset": "Student records (create synthetic with Module 18 or use real data)",
     "modules": [1, 4, 5, 7, 13, 14, 18],
     "deliverable": "Grade prediction model, key success factors identified, intervention recommendations."},
    {"title": "🔐 Data Privacy Audit Report", "level": "🟡 Intermediate", "time": "4-6 hours",
     "desc": "Conduct a full GDPR/NDPR compliance audit on a dataset. Essential for enterprise roles.",
     "dataset": "Any dataset containing PII (names, emails, phones)",
     "modules": [26, 33, 32, 34, 39],
     "deliverable": "Comprehensive privacy audit report with findings, risk assessment, and remediation plan."},
    {"title": "📊 Executive KPI Dashboard", "level": "🔴 Advanced", "time": "8-12 hours",
     "desc": "Build a C-suite-ready dashboard with KPIs, gauges, and radar charts for enterprise data operations.",
     "dataset": "Any business dataset (sales, operations, HR, etc.)",
     "modules": [1, 9, 4, 5, 19, 38, 14, 8],
     "deliverable": "Executive dashboard with 6+ KPIs, quality gauges, operations radar, and executive summary."},
]

for proj in projects_db:
    with st.expander(f"{proj['level']} {proj['title']} — ⏱ {proj['time']}", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Description:** {proj['desc']}")
            st.markdown(f"**Dataset:** {proj['dataset']}")
            st.markdown(f"**DataFlow Modules needed:** {', '.join(f'Module {m}' for m in proj['modules'])}")
        with col2:
            st.markdown(f"**Deliverable:** {proj['deliverable']}")
            if st.button(f"🚀 Start This Project", key=f"proj_{proj['title'][:20]}"):
                st.success("✅ Great choice! Use the modules listed above to complete this project. Don't forget to export your results!")
                st.info("💡 **Portfolio Tip:** Document your process — what you did, why you did it, and what you found. Employers love seeing your thinking, not just your results.")

st.markdown("---")
st.markdown("### 📁 Portfolio Builder Checklist")
st.markdown("""
Build your data science portfolio step by step:

- [ ] Complete 2 beginner projects
- [ ] Complete 2 intermediate projects  
- [ ] Complete 1 advanced project
- [ ] Write a 1-page summary for each project
- [ ] Host your projects on GitHub (free)
- [ ] Deploy at least 1 project to Streamlit Cloud (free)
- [ ] Share on LinkedIn and tag relevant communities
- [ ] Add projects to your CV/resume

> **Pro Tip from Adewale Samson Adeagbo:** "My first ML project (Fake News Detector) took 2 weeks of learning and building. Today it's my most viewed project with AUC 0.9393. Start small, document everything, and ship it."
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
