"""
Module 57: DS Roadmap — DataScience Flow v9.5
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


st.set_page_config(page_title="DS Roadmap | DataFlow v9.0", page_icon="🗺️", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🗺️ DATA SCIENCE ROADMAP — Your Learning Compass</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** A complete, interactive roadmap showing every step to become a data scientist — from absolute zero to deployment-ready. Each milestone links to the relevant DataFlow module.

**🎯 Why you need it:** Data science can feel overwhelming. This roadmap breaks it down into small, achievable steps with clear "learn → practice → build" cycles. No prior knowledge assumed.

**📖 How to use it:** Start at the top. Follow the phases. Click any module to jump directly to it. Track your progress.
""")

# Define the roadmap
roadmap_phases = [
    {
        "phase": "🌱 Foundation",
        "color": "#4f8ef7",
        "steps": [
            {"emoji": "📊", "title": "Understand Your Data", "desc": "Learn to load, preview, and explore datasets. Master head/tail, column types, and basic statistics.", "module": 1, "time": "15 min"},
            {"emoji": "📋", "title": "Audit Data Quality", "desc": "Learn to assess data quality with a systematic scorecard. Understand completeness, uniqueness, and consistency.", "module": 9, "time": "10 min"},
            {"emoji": "📈", "title": "Create Your First Charts", "desc": "Transform raw numbers into visual stories. Master histograms, box plots, scatter plots, and bar charts.", "module": 5, "time": "20 min"},
            {"emoji": "📊", "title": "Compute Key Statistics", "desc": "Learn mean, median, standard deviation, and confidence intervals. Understand what each statistic tells you.", "module": 4, "time": "15 min"},
        ]
    },
    {
        "phase": "🧹 Data Wrangling",
        "color": "#00d9a7",
        "steps": [
            {"emoji": "🕳️", "title": "Handle Missing Values", "desc": "Missing data is everywhere. Learn 5+ strategies to handle it — from simple deletion to smart imputation.", "module": 2, "time": "15 min"},
            {"emoji": "♻️", "title": "Remove Duplicates", "desc": "Duplicate records distort analysis. Learn to find and handle them — full-row and partial-key methods.", "module": 3, "time": "10 min"},
            {"emoji": "🎯", "title": "Detect & Handle Outliers", "desc": "Extreme values can mislead. Learn IQR, Z-Score, and Modified Z-Score methods to find and fix outliers.", "module": 6, "time": "20 min"},
            {"emoji": "🗂️", "title": "Manage Columns Like a Pro", "desc": "Rename, reorder, cast types, clean headers. Build a clean, well-documented dataset.", "module": 12, "time": "10 min"},
        ]
    },
    {
        "phase": "📊 Analysis & Stats",
        "color": "#d4a843",
        "steps": [
            {"emoji": "📐", "title": "Test Hypotheses", "desc": "Is the difference real or random? Learn T-tests, Chi-square, and ANOVA with plain-English interpretations.", "module": 11, "time": "25 min"},
            {"emoji": "📅", "title": "Analyze Time Series", "desc": "Find trends, seasons, and cycles in time-based data. Learn decomposition, ACF, PACF, and forecasting.", "module": 17, "time": "25 min"},
            {"emoji": "📝", "title": "Analyze Text Data", "desc": "Extract meaning from words. Word frequency, TF-IDF, rule-based sentiment — no AI API needed!", "module": 29, "time": "20 min"},
            {"emoji": "📋", "title": "Query with SQL", "desc": "The universal language of data. Learn SELECT, WHERE, GROUP BY, JOINs — right on your dataset.", "module": 23, "time": "20 min"},
        ]
    },
    {
        "phase": "🤖 Machine Learning",
        "color": "#f85149",
        "steps": [
            {"emoji": "⚙️", "title": "Engineer Features", "desc": "Transform raw columns into ML-ready features. 7 encoding methods, 3 scalers, PCA, polynomial features.", "module": 7, "time": "25 min"},
            {"emoji": "🧬", "title": "Select Best Features", "desc": "Not all columns are useful. Learn RFE, SelectKBest, and correlation-based feature selection.", "module": 20, "time": "20 min"},
            {"emoji": "🤖", "title": "Train Your First Model", "desc": "Train 7 algorithms with one click. Compare accuracy, view confusion matrices, ROC curves, learning curves.", "module": 13, "time": "30 min"},
            {"emoji": "⚖️", "title": "Fix Imbalanced Classes", "desc": "When one class dominates, models fail. Learn SMOTE and other balancing techniques.", "module": 15, "time": "15 min"},
        ]
    },
    {
        "phase": "🏢 Professional & Enterprise",
        "color": "#8b5cf6",
        "steps": [
            {"emoji": "📊", "title": "Tell Data Stories", "desc": "Turn analysis into narratives. Auto-generate reports that stakeholders actually understand.", "module": 14, "time": "15 min"},
            {"emoji": "📤", "title": "Export & Share", "desc": "Get your results out. CSV, Excel, Parquet, JSON, HTML reports — choose the right format.", "module": 8, "time": "10 min"},
            {"emoji": "🔐", "title": "Protect Privacy", "desc": "Handle sensitive data responsibly. 8 masking methods, PII detection, GDPR/NDPR compliance.", "module": 26, "time": "20 min"},
            {"emoji": "⚖️", "title": "Govern Data Properly", "desc": "Enterprise-grade governance: contracts, compliance, retention, disaster recovery.", "module": 32, "time": "30 min"},
        ]
    },
]

# Display roadmap
for phase in roadmap_phases:
    with st.expander(f"{phase['phase']} — {len(phase['steps'])} steps", expanded=True):
        cols = st.columns(len(phase['steps']))
        for i, step in enumerate(phase['steps']):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#161b22;border:2px solid {phase['color']};border-radius:16px;padding:1.2rem;text-align:center;height:280px;">
                    <div style="font-size:2.5rem;">{step['emoji']}</div>
                    <div style="font-weight:700;color:#e6edf3;margin:0.5rem 0;font-size:0.9rem;">{step['title']}</div>
                    <div style="color:#8b949e;font-size:0.75rem;line-height:1.4;margin-bottom:0.5rem;">{step['desc']}</div>
                    <div style="color:#484f58;font-size:0.7rem;">⏱ {step['time']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"→ Module {step['module']}")

st.markdown("---")
st.markdown("### 📊 Track Your Progress")
phases_done = st.multiselect("Which phases have you completed?", [p['phase'] for p in roadmap_phases])
if phases_done:
    pct = len(phases_done) / len(roadmap_phases) * 100
    st.progress(pct / 100, f"🎉 {pct:.0f}% complete — {len(phases_done)} of {len(roadmap_phases)} phases")
    if pct == 100:
        st.balloons()
        st.success("🏆 Congratulations! You've completed the Data Science Roadmap. You're ready for real-world projects!")

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
