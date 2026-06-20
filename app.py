"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  CONFIDENTIAL — DataScience Flow v10.0                                       ║
║  Copyright © 2015-2026 HMG Concepts — All Rights Reserved                   ║
║                                                                              ║
║  This software is the proprietary property of HMG Concepts and its          ║
║  subsidiaries (HMG Academy, HMG Technologies, HMG Media, HMG Gospel).       ║
║  Unauthorized copying, distribution, modification, reverse engineering,     ║
║  or forking of this codebase is strictly prohibited.                         ║
║                                                                              ║
║  Built by: Adewale Samson Adeagbo                                           ║
║  Founder, HMG Concepts (est. 2015)                                          ║
║  Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts                 ║
║  Email: adeagboadewalesamson@gmail.com                                      ║
║  Portfolio: https://cssadewale.pages.dev                                    ║
║  Organisation: https://hmgconcepts.pages.dev                                ║
║  Academy: https://hmgacademy.pages.dev                                      ║
║                                                                              ║
║  76-Module Enterprise Data Science Workflow Platform                        ║
║  100% Free Tools — No AI API Required — PWA + SEO Optimized                 ║
║  Covering Every Aspect of the Data Science Workflow                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import json
from datetime import datetime, timedelta

# ═══════════════ PAGE CONFIG ═══════════════
st.set_page_config(
    page_title="DataScience Flow | HMG Academy | Data Science Workflow Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": """DataScience Flow v10.0 — 76-Module Enterprise Data Science Workflow Platform

Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts (est. 2015)

Built by Adewale Samson Adeagbo
Data Scientist | EdTech Builder | AI-Augmented Solutions Developer

🔗 Portfolio: https://cssadewale.pages.dev
🏢 HMG Concepts: https://hmgconcepts.pages.dev
🎓 HMG Academy: https://hmgacademy.pages.dev
💻 HMG Technologies: https://hmgtechnologies.pages.dev
📢 HMG Media: https://hmgmedia.pages.dev
✝️ HMG Gospel: https://hmggospel.pages.dev

© HMG Concepts — All Rights Reserved""",
        "Get Help": "https://hmgacademy.pages.dev/",
        "Report a Bug": "mailto:adeagboadewalesamson@gmail.com",
    }
)

# ═══════════════ IMPORTS ═══════════════
from subscription import (
    init_subscription_state, TIERS,
    tier_badge_html, get_tier_info, local_save_subscription
)
from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email, sanitise_url, sanitise_sql,
    log_action, check_session_timeout, get_security_status,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)

# ═══════════════ SEO META TAGS ═══════════════
st.markdown(f"""
<!-- SEO: Primary Meta Tags -->
<title>DataScience Flow — 76-Module Data Science Workflow Platform | HMG Academy</title>
<meta name="title" content="DataScience Flow — 76-Module Data Science Workflow Platform | HMG Academy">
<meta name="description" content="DataScience Flow is a comprehensive, free data science workflow platform with 76 modules covering EDA, ML, statistics, NLP, geospatial, governance, and more. Built by Adewale Samson Adeagbo for HMG Academy.">
<meta name="keywords" content="data science, machine learning, EDA, data analysis, Streamlit, free data tools, HMG Academy, Adewale Adeagbo, Nigeria, data workflow, data cleaning, feature engineering, model deployment">
<meta name="author" content="Adewale Samson Adeagbo">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://datascienceflow-hmgacademy.streamlit.app/">

<!-- SEO: Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://datascienceflow-hmgacademy.streamlit.app/">
<meta property="og:title" content="DataScience Flow — 76-Module Data Science Workflow Platform">
<meta property="og:description" content="From data collection to deployment — every stage of the data science lifecycle, in one platform. 100% free. No AI API.">
<meta property="og:site_name" content="DataScience Flow">

<!-- SEO: Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="https://datascienceflow-hmgacademy.streamlit.app/">
<meta property="twitter:title" content="DataScience Flow — 76-Module Data Science Workflow Platform">
<meta property="twitter:description" content="From data collection to deployment — every stage of the data science lifecycle, in one platform. 100% free. No AI API.">

<!-- Structured Data (JSON-LD) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "DataScience Flow",
  "applicationCategory": "DataScienceApplication",
  "operatingSystem": "Web",
  "description": "76-Module Enterprise Data Science Workflow Platform covering EDA, ML, statistics, NLP, geospatial, governance, and more.",
  "author": {{
    "@type": "Person",
    "name": "Adewale Samson Adeagbo",
    "url": "https://cssadewale.pages.dev",
    "jobTitle": "Data Scientist | AI-Augmented Solutions Developer",
    "worksFor": {{
      "@type": "Organization",
      "name": "HMG Concepts",
      "url": "https://hmgconcepts.pages.dev"
    }}
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "HMG Academy",
    "url": "https://hmgacademy.pages.dev",
    "parentOrganization": {{
      "@type": "Organization",
      "name": "HMG Concepts",
      "url": "https://hmgconcepts.pages.dev"
    }}
  }},
  "offers": [
    {{"@type": "Offer", "price": "0", "priceCurrency": "NGN", "description": "1-Day Free Trial"}},
    {{"@type": "Offer", "price": "3500", "priceCurrency": "NGN", "description": "Essential Plan / month"}},
    {{"@type": "Offer", "price": "8500", "priceCurrency": "NGN", "description": "Professional Plan / month"}},
    {{"@type": "Offer", "price": "25000", "priceCurrency": "NGN", "description": "Enterprise Plan / month"}}
  ]
}}
</script>
""", unsafe_allow_html=True)

# ═══════════════ ENTERPRISE CSS ═══════════════
st.markdown("""
<style>
/* ═══ Root Variables ═══ */
:root {
    --primary: #6C63FF;
    --primary-dark: #5A52D5;
    --secondary: #00D9A7;
    --accent: #FF6B6B;
    --bg-dark: #0E1117;
    --bg-card: #1A1D29;
    --bg-sidebar: #161922;
    --text-primary: #FAFAFA;
    --text-secondary: #A0A8B8;
    --border: #2D3348;
    --success: #00D9A7;
    --warning: #FFB74D;
    --error: #FF6B6B;
    --info: #64B5F6;
    --gradient-1: linear-gradient(135deg, #6C63FF 0%, #00D9A7 100%);
    --gradient-2: linear-gradient(135deg, #FF6B6B 0%, #FFB74D 100%);
    --shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ═══ Global ═══ */
.stApp { background: var(--bg-dark) !important; }
h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; font-family: 'Segoe UI', system-ui, sans-serif !important; }
.stMarkdown, .stText { color: var(--text-secondary) !important; }
.stMetric label { color: var(--text-secondary) !important; }
.stMetric value { color: var(--text-primary) !important; font-weight: 700 !important; }

/* ═══ Hero Section ═══ */
.hero-section {
    background: var(--gradient-1);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    box-shadow: var(--shadow);
}
.hero-section h1 { color: #FFFFFF !important; font-size: 2.4rem !important; font-weight: 800 !important; margin-bottom: 8px !important; }
.hero-section p { color: rgba(255,255,255,0.9) !important; font-size: 1.05rem; line-height: 1.6; }
.hero-badge { display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; margin: 4px 4px 4px 0; backdrop-filter: blur(4px); }

/* ═══ Feature Cards ═══ */
.feature-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 18px 16px; margin-bottom: 12px; transition: all 0.25s ease; cursor: pointer; min-height: 140px; }
.feature-card:hover { border-color: var(--primary); box-shadow: 0 0 20px rgba(108,99,255,0.15); transform: translateY(-2px); }
.ent-card { border-left: 3px solid var(--secondary) !important; }
.feature-card h4 { font-size: 0.95rem !important; font-weight: 700 !important; margin: 6px 0 !important; color: var(--text-primary) !important; }
.feature-card p { font-size: 0.78rem !important; color: var(--text-secondary) !important; line-height: 1.4; margin: 0 !important; }

/* ═══ Tags ═══ */
.tag { display: inline-block; background: rgba(108,99,255,0.15); color: var(--primary); padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; }
.tag-orange { background: rgba(255,183,77,0.15); color: var(--warning); }
.tag-ent { background: rgba(0,217,167,0.15); color: var(--secondary); }
.tag-new { background: rgba(255,107,107,0.15); color: var(--accent); }

/* ═══ Sidebar ═══ */
[data-testid="stSidebar"] { background: var(--bg-sidebar) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }

/* ═══ Buttons ═══ */
.stButton > button { background: var(--primary) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease; }
.stButton > button:hover { background: var(--primary-dark) !important; box-shadow: 0 4px 12px rgba(108,99,255,0.3); }

/* ═══ Footer ═══ */
.footer-section { background: var(--bg-card); border-top: 1px solid var(--border); padding: 28px 0; margin-top: 40px; text-align: center; }
.footer-section a { color: var(--primary); text-decoration: none; font-weight: 600; }
.footer-section a:hover { text-decoration: underline; }

/* ═══ Subscription Cards ═══ */
.sub-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center; height: 100%; }
.sub-card.featured { border: 2px solid #d4a843; box-shadow: 0 0 20px rgba(212,168,67,0.15); }
.sub-card .price { font-size: 1.4rem; font-weight: 800; color: var(--primary); margin: 8px 0; }
.sub-card ul { text-align: left; font-size: 0.82rem; color: var(--text-secondary); list-style: none; padding: 0; }
.sub-card li { padding: 3px 0; }
.sub-card li::before { content: '✓ '; color: var(--success); font-weight: 700; }

/* ═══ Security Banner ═══ */
.security-banner { background: rgba(255,107,107,0.1); border: 1px solid rgba(255,107,107,0.3); border-radius: 8px; padding: 12px; margin: 8px 0; font-size: 0.85rem; color: var(--accent); }

/* ═══ Responsive ═══ */
@media (max-width: 768px) {
    .hero-section h1 { font-size: 1.6rem !important; }
    .hero-section { padding: 20px; }
}

/* ═══ Scrollbar ═══ */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ═══ Animations ═══ */
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.feature-card, .sub-card { animation: fadeIn 0.4s ease-out; }

/* ═══ Brand Bar ═══ */
.brand-bar { background: var(--bg-card); border-radius: 8px; padding: 10px 16px; margin: 8px 0; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
.brand-bar a { color: var(--secondary); font-size: 0.78rem; text-decoration: none; font-weight: 600; }
.brand-bar a:hover { color: var(--primary); }
</style>
""", unsafe_allow_html=True)

# ═══════════════ SESSION STATE ═══════════════
for k, v in {
    "df": None, "filename": None, "df_cleaned": None,
    "history": [], "steps_done": set(), "data_dictionary": {}, "bookmarks": [],
    "lineage": [], "monitored_rules": [], "sql_saved_queries": [], "masked_columns": {},
    "whatif_scenarios": [],
    "ent_audit_log": [], "ent_role": "admin", "ent_data_versions": [],
    "ent_scheduled_jobs": [], "ent_compliance_checks": [], "ent_policies": {},
    "ent_collab_notes": [], "ent_api_spec": {}, "ent_data_contracts": [],
    "ent_retention_rules": [], "ent_batch_queue": [], "ent_gdpr_requests": [],
    "ent_kpi_dashboard": {}, "ent_disaster_recovery": [],
    "ent_workflow_tracker": [], "ent_learning_path": "beginner",
    "ent_certifications": [], "ent_project_journal": [],
    "sub_auth_email": None, "sub_tier": None, "sub_expires": None,
    "sub_trial_used": False, "sub_authenticated": False, "sub_payment_ref": None,
    "pipeline_steps": [], "experiment_log": [], "notebook_cells": [],
    "validation_results": {}, "ab_test_results": {},
    "dashboard_widgets": [], "code_snippets": [],
    "sampling_config": {}, "geo_data": None,
    # Notebook generation state
    "notebook_operations": [],
    "notebook_code_cells": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

init_subscription_state()
init_secure_session()

# ═══════════════ SECURITY CHECKS ═══════════════
# Check session timeout
if check_session_timeout():
    st.warning("⏰ Your session has expired for security. Please refresh the page.")

# Check for security violations
violation = st.session_state.get("_security_violation")
if violation:
    st.markdown(f"""
    <div class="security-banner">
        🚫 <strong>Security Alert:</strong> {sanitise_string(violation)}<br>
        Your session has been reset for security. Please re-authenticate.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════ HELPER FUNCTIONS ═══════════════
def log(action, detail="", level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detail = sanitise_string(str(detail), 200)
    st.session_state["history"].append({"time": ts, "action": action, "detail": detail})
    st.session_state["ent_audit_log"].append({
        "timestamp": ts, "action": action, "detail": detail,
        "role": st.session_state.get("ent_role", "admin"), "level": level,
        "dataset": st.session_state.get("filename", "—"),
        "rows": len(st.session_state.get("df_cleaned", pd.DataFrame())) if st.session_state.get("df_cleaned") is not None else 0,
        "tier": st.session_state.get("sub_tier", "none")
    })
    log_action(action, detail, level)
    # Track for notebook generation
    st.session_state["notebook_operations"].append({"timestamp": ts, "action": action, "detail": detail})


def add_lineage(step, description):
    dfc = st.session_state.get("df_cleaned")
    st.session_state["lineage"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "step": step, "description": description,
        "rows": dfc.shape[0] if dfc is not None else 0,
        "cols": dfc.shape[1] if dfc is not None else 0,
        "role": st.session_state.get("ent_role", "admin")
    })


# ═══════════════ SIDEBAR ═══════════════
with st.sidebar:
    # Brand Identity
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <div style="font-size:2.2rem;">🔬</div>
        <h2 style="margin:4px 0; font-size:1.2rem;">DataScience Flow</h2>
        <div style="font-size:0.78rem; color:var(--secondary); font-weight:700; letter-spacing:1px;">ENTERPRISE v10.0</div>
        <div style="font-size:0.68rem; color:var(--text-secondary); margin-top:6px;">
            by <strong>Adewale Samson Adeagbo</strong><br>
            HMG Concepts · HMG Academy · Lagos, NG
        </div>
        <div style="font-size:0.62rem; color:var(--text-secondary); margin-top:4px;">
            Part of <strong>HMG Academy</strong> Ecosystem<br>
            Subsidiary of <strong>HMG Concepts</strong> (est. 2015)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ecosystem Links
    st.markdown("""
    <div class="brand-bar">
        <a href="https://hmgacademy.pages.dev/" target="_blank">🎓 Academy</a>
        <a href="https://hmgconcepts.pages.dev/" target="_blank">🏢 Concepts</a>
        <a href="https://hmgtechnologies.pages.dev/" target="_blank">💻 Tech</a>
        <a href="https://hmgmedia.pages.dev/" target="_blank">📢 Media</a>
        <a href="https://hmggospel.pages.dev/" target="_blank">✝️ Gospel</a>
    </div>
    """, unsafe_allow_html=True)

    # Subscription
    with st.expander("💳 Subscription", expanded=not st.session_state.get("sub_authenticated")):
        if st.session_state.get("sub_authenticated") and verify_subscription_integrity():
            tier = st.session_state.get("sub_tier", "free_trial")
            expires = st.session_state.get("sub_expires", "")
            try:
                exp_dt = datetime.fromisoformat(expires)
                days_left = max(0, (exp_dt - datetime.now()).days)
                hours_left = max(0, int((exp_dt - datetime.now()).total_seconds() / 3600))
            except Exception:
                days_left = 0
                hours_left = 0

            time_left = f"{days_left} days remaining" if days_left > 0 else f"{hours_left} hours remaining" if hours_left > 0 else "Expiring"
            st.markdown(f"""
            <div style="text-align:center; padding:8px;">
                {tier_badge_html(tier)}
                <div style="margin-top:6px;"><strong>{TIERS.get(tier, {}).get('name', tier.title())}</strong></div>
                <div style="color:var(--text-secondary); font-size:0.82rem;">{time_left}</div>
                <div style="color:var(--text-secondary); font-size:0.72rem; margin-top:4px;">
                    🔒 Secured session — integrity verified
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:8px; color:var(--warning);">
                ⚠️ No active subscription
            </div>
            """, unsafe_allow_html=True)
            trial_email = st.text_input("Your email", placeholder="you@email.com", key="sidebar_trial")
            if st.button("🚀 Start Free Trial", use_container_width=True):
                if not check_rate_limit("subscription"):
                    st.error("⏱️ Rate limited. Please wait a moment.")
                else:
                    result = authenticate_subscription(trial_email, "free_trial")
                    if result["success"]:
                        local_save_subscription(trial_email, "free_trial", st.session_state["sub_expires"])
                        log("Free trial activated", trial_email)
                        st.success("✅ Full access for 24 hours!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

    st.markdown("---")

    # Role & Learning Path
    st.session_state["ent_role"] = st.selectbox(
        "Active Role",
        ["admin", "data_steward", "analyst", "data_scientist", "viewer",
         "compliance_officer", "auditor", "beginner"],
        index=0
    )
    st.session_state["ent_learning_path"] = st.selectbox(
        "Learning Path",
        ["beginner", "intermediate", "advanced", "enterprise"]
    )

    # Security Status
    sec_status = get_security_status()
    with st.expander("🔒 Security Status"):
        st.markdown(f"""
        **Session Age:** {sec_status['session_age_minutes']} min<br>
        **Actions Logged:** {sec_status['total_actions']}<br>
        **Exports This Hour:** {sec_status['exports_this_hour']} / 30<br>
        **Integrity:** {'✅ Verified' if not sec_status['violations'] else '❌ Violation Detected'}
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Links
    st.markdown("### 🔗 Quick Links")
    links = [
        ("🏠 Portfolio", "https://cssadewale.pages.dev/"),
        ("🏢 HMG Concepts", "https://hmgconcepts.pages.dev/"),
        ("🎓 HMG Academy", "https://hmgacademy.pages.dev/"),
        ("💻 HMG Technologies", "https://hmgtechnologies.pages.dev/"),
        ("📢 HMG Media", "https://hmgmedia.pages.dev/"),
        ("✝️ HMG Gospel", "https://hmggospel.pages.dev/"),
        ("🐙 GitHub @cssadewale", "https://github.com/cssadewale"),
        ("💼 LinkedIn", "https://linkedin.com/in/adewalesamsonadeagbo"),
        ("📺 YouTube @hmgconcepts", "https://youtube.com/@hmgconcepts"),
    ]
    for lbl, url in links:
        st.markdown(f'<a href="{url}" target="_blank" style="color:var(--primary); text-decoration:none; font-size:0.82rem; display:block; padding:2px 0;">{lbl}</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📂 Data Sources")
    load_mode = st.radio("Load from", ["📤 Upload File", "📦 Sample Dataset", "🌐 Web/API URL"], horizontal=True)

    if load_mode == "📤 Upload File":
        uploaded = st.file_uploader("CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded:
            # Validate upload
            validation = validate_upload(uploaded.name, uploaded.size, uploaded.type)
            if not validation["valid"]:
                st.error(f"❌ {validation['error']}")
            else:
                try:
                    if not check_rate_limit("upload"):
                        st.error("⏱️ Upload rate limited. Please wait.")
                    else:
                        if uploaded.name.lower().endswith(".csv"):
                            df = pd.read_csv(uploaded)
                        else:
                            df = pd.read_excel(uploaded)
                        st.session_state.update({
                            "df": df, "filename": uploaded.name, "df_cleaned": df.copy(),
                            "history": [], "steps_done": set(), "data_dictionary": {},
                            "bookmarks": [], "lineage": [], "ent_audit_log": [],
                            "ent_workflow_tracker": [], "notebook_operations": [],
                            "notebook_code_cells": [],
                        })
                        log("Dataset loaded", f"{uploaded.name} — {df.shape[0]:,}×{df.shape[1]}")
                        st.success(f"✅ {uploaded.name}")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ {sanitise_string(str(e))}")

    elif load_mode == "🌐 Web/API URL":
        web_url = st.text_input("URL", placeholder="https://example.com/data.csv")
        web_url = sanitise_url(web_url)
        if st.button("📥 Fetch") and web_url:
            try:
                import requests
                resp = requests.get(web_url, timeout=15)
                df = pd.read_csv(io.StringIO(resp.text))
                fname = web_url.split("/")[-1] or "web_data.csv"
                st.session_state.update({
                    "df": df, "filename": fname, "df_cleaned": df.copy(),
                    "history": [], "steps_done": set(), "data_dictionary": {},
                    "bookmarks": [], "lineage": [], "ent_audit_log": [],
                    "ent_workflow_tracker": [], "notebook_operations": [],
                    "notebook_code_cells": [],
                })
                log("Dataset loaded (Web)", fname)
                st.success(f"✅ {fname}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {sanitise_string(str(e))}")
    else:
        from sklearn import datasets as sk_d
        sc = st.selectbox("Choose sample", [
            "🌸 Iris", "🏠 California Housing", "🍷 Wine Quality", "💊 Diabetes",
            "🎯 Breast Cancer", "📝 Digits"
        ])
        if st.button("Load Sample"):
            loaders = {
                "🌸 Iris": sk_d.load_iris,
                "🏠 California Housing": sk_d.fetch_california_housing,
                "🍷 Wine Quality": sk_d.load_wine,
                "💊 Diabetes": sk_d.load_diabetes,
                "🎯 Breast Cancer": sk_d.load_breast_cancer,
                "📝 Digits": sk_d.load_digits,
            }
            df = loaders[sc](as_frame=True).frame
            fname = sc.split(" ", 1)[1].lower().replace(" ", "_") + ".csv"
            st.session_state.update({
                "df": df, "filename": fname, "df_cleaned": df.copy(),
                "history": [], "steps_done": set(), "data_dictionary": {},
                "bookmarks": [], "lineage": [], "ent_audit_log": [],
                "ent_workflow_tracker": [], "notebook_operations": [],
                "notebook_code_cells": [],
            })
            log("Sample loaded", fname)
            st.success(f"✅ {fname}")
            st.rerun()

    # Quick Export
    if st.session_state.get("df") is not None:
        st.markdown("---")
        st.markdown("### ⚡ Quick Export")
        exp_fmt = st.selectbox("Format", ["CSV", "Excel", "JSON", "Parquet", "📓 Jupyter Notebook (.ipynb)"], key="qexp_fmt")
        if st.button("📥 Export Now", use_container_width=True):
            dfc = st.session_state.get("df_cleaned")
            if dfc is not None:
                if not check_export_limit():
                    st.error("⏱️ Export limit reached (30/hour). Please wait.")
                else:
                    try:
                        if exp_fmt == "📓 Jupyter Notebook (.ipynb)":
                            from notebook_generator import generate_full_notebook
                            df_info = {
                                "filename": st.session_state.get("filename", "data"),
                                "rows": len(dfc), "cols": len(dfc.columns)
                            }
                            notebook_json = generate_full_notebook(
                                df_info,
                                st.session_state.get("notebook_operations", []),
                            )
                            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
                            st.download_button(
                                "💾 Download .ipynb", data=notebook_json,
                                file_name=f"{fname}_analysis.ipynb",
                                mime="application/json", use_container_width=True
                            )
                            log("Exported notebook", fname)
                        elif exp_fmt == "CSV":
                            data = dfc.to_csv(index=False).encode()
                            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
                            # Add watermark comment
                            watermark = f"# {BRAND_WATERMARK}\n# {BRAND_FOOTER}\n"
                            data = watermark.encode() + data
                            st.download_button("💾 Download CSV", data=data, file_name=f"{fname}_cleaned.csv", mime="text/csv", use_container_width=True)
                            log("Quick export", "CSV")
                        elif exp_fmt == "Excel":
                            buffer = io.BytesIO()
                            dfc.to_excel(buffer, index=False, engine='openpyxl')
                            data = buffer.getvalue()
                            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
                            st.download_button("💾 Download Excel", data=data, file_name=f"{fname}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                            log("Quick export", "Excel")
                        elif exp_fmt == "JSON":
                            data = dfc.to_json(orient='records', indent=2).encode()
                            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
                            st.download_button("💾 Download JSON", data=data, file_name=f"{fname}_cleaned.json", mime="application/json", use_container_width=True)
                            log("Quick export", "JSON")
                        else:
                            buffer = io.BytesIO()
                            dfc.to_parquet(buffer, index=False)
                            data = buffer.getvalue()
                            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
                            st.download_button("💾 Download Parquet", data=data, file_name=f"{fname}_cleaned.parquet", mime="application/octet-stream", use_container_width=True)
                            log("Quick export", "Parquet")
                    except Exception as e:
                        st.error(f"Export error: {sanitise_string(str(e))}")

    # Workflow State
    if st.session_state.get("df") is not None:
        st.markdown("---")
        st.markdown("### 📊 Workflow State")
        dfc = st.session_state.get("df_cleaned")
        if dfc is not None:
            st.caption(f"Rows: {dfc.shape[0]:,} | Cols: {dfc.shape[1]}")
            st.caption(f"Steps: {len(st.session_state.get('steps_done', set()))}")
            st.caption(f"Audit: {len(st.session_state.get('ent_audit_log', []))}")

# ═══════════════ MAIN CONTENT ═══════════════
st.markdown("""
<div class="hero-section">
    <h1>🔬 DataScience Flow</h1>
    <p><strong>76-Module Complete Data Science Workflow Platform</strong></p>
    <p>From data collection to deployment — every stage of the data science lifecycle, in one platform.<br>
    Part of <strong>HMG Academy</strong> Ecosystem — Subsidiary of <strong>HMG Concepts</strong></p>
    <span class="hero-badge">🎓 HMG Academy</span>
    <span class="hero-badge">🏢 HMG Concepts</span>
    <span class="hero-badge">🔬 For Analysts</span>
    <span class="hero-badge">🏢 For Enterprise</span>
    <span class="hero-badge">🇳🇬 Built in Nigeria</span>
    <span class="hero-badge" style="background:rgba(255,255,255,0.35);">🔒 Secured Platform</span>
    <span class="hero-badge" style="background:rgba(255,255,255,0.35);">No AI API — 100% Free</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════ SUBSCRIPTION GATE ═══════════════
if not st.session_state.get("sub_authenticated") or not verify_subscription_integrity():
    st.warning("### 🔐 Subscription Required — Start your free trial from the sidebar!\n\nNo payment required. Full access to all 76 modules. Secured & verified session.")
    st.markdown("### 💳 Subscription Plans")
    c1, c2, c3, c4 = st.columns(4)
    for i, (tier_key, tier_data) in enumerate(TIERS.items()):
        with [c1, c2, c3, c4][i]:
            featured = " featured" if tier_key == "professional" else ""
            st.markdown(f"""
            <div class="sub-card{featured}">
                <h3>{tier_data["name"]}</h3>
                <div class="price">{tier_data["price"]}</div>
                <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:12px;">{tier_data.get("price_usd", "")}</div>
                <ul>
                    {''.join(f'<li>{f}</li>' for f in tier_data["features"][:6])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 **Start your free trial** by entering your email in the sidebar. One trial per email. Secured session with integrity verification. No credit card needed.")
    st.stop()

# ═══════════════ DATA OVERVIEW ═══════════════
if st.session_state["df"] is None:
    st.markdown("""
    <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:16px; padding:32px; margin:20px 0;">
        <h3>👋 Welcome to DataScience Flow v10.0!</h3>
        <p><strong>Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts</strong></p>
        <ol>
            <li>📤 <strong>Upload</strong> a CSV/Excel file from the sidebar (or pick a sample)</li>
            <li>🔍 <strong>Explore</strong> — Start with Data Exploration</li>
            <li>📊 <strong>Analyse</strong> — Follow the guided workflow</li>
            <li>📓 <strong>Download .ipynb</strong> — Generate a complete Jupyter notebook of your analysis</li>
        </ol>
        <p><strong>Security Features:</strong></p>
        <ul>
            <li>🔒 Integrity-verified subscription sessions</li>
            <li>🛡️ Rate limiting on all actions</li>
            <li>🔐 Input sanitisation & validation</li>
            <li>📝 Full audit trail of all operations</li>
            <li>🏷️ Watermarked exports with HMG Academy branding</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
else:
    dfc = st.session_state["df_cleaned"]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📋 Rows", f"{dfc.shape[0]:,}")
    c2.metric("📐 Cols", f"{dfc.shape[1]}")
    c3.metric("🔢 Numeric", str(len(dfc.select_dtypes(include=np.number).columns)))
    c4.metric("🔤 Categorical", str(len(dfc.select_dtypes(include=["object", "string"]).columns)))
    c5.metric("🕳️ Missing %", f"{dfc.isnull().sum().sum()/(dfc.shape[0]*dfc.shape[1])*100:.1f}%")
    c6.metric("📄 File", (st.session_state.get("filename", "—") or "—")[:14])
    st.dataframe(dfc.head(10), use_container_width=True)

    # Data Dictionary
    with st.expander("📖 Data Dictionary"):
        dict_data = []
        for col in dfc.columns:
            dict_data.append({
                "Column": col, "Type": str(dfc[col].dtype),
                "Non-Null": int(dfc[col].notna().sum()),
                "Null %": f"{dfc[col].isna().mean()*100:.1f}%",
                "Unique": int(dfc[col].nunique()),
                "Sample": str(dfc[col].dropna().iloc[0])[:30] if len(dfc[col].dropna()) > 0 else "—"
            })
        st.dataframe(pd.DataFrame(dict_data), use_container_width=True)

# ═══════════════ MODULE GRID ═══════════════
st.markdown("---")
st.markdown(f"**{len(mods)} modules** across 12 workflow stages — every stage of the data science lifecycle.")
st.markdown("### 🧩 61 Complete Modules — Every Stage of the Data Science Workflow")

mods = [
    # Collection (01-05)
    ("📥", "01 Data Collection Hub", "Multi-source ingestion: CSV, Excel, API, web scraping", "Collection"),
    ("🧪", "02 Data Simulation", "Synthetic data, bootstrap, noise injection", "Collection"),
    ("📥", "03 Data Ingest & Batch", "Multi-file queue, FIFO, checksum dedup", "Collection"),
    ("🌐", "04 Web Data Connector", "Import from URLs & APIs", "Collection"),
    ("🗂️", "05 Sampling Strategies", "Stratified, cluster, systematic sampling", "Collection"),
    # Prep (06-12)
    ("🔍", "06 Data Exploration", "Head/tail, types, anomalies, cross-tab", "Prep"),
    ("🕳️", "07 Missing Values", "6 imputation strategies, co-occurrence", "Prep"),
    ("♻️", "08 Duplicates", "Full-row + partial-key detection", "Prep"),
    ("🎯", "09 Outlier Detection", "IQR / Z-Score / Isolation Forest", "Prep"),
    ("📋", "10 Data Quality Audit", "15-check scorecard, gauge chart", "Prep"),
    ("🗂️", "11 Column Manager", "Rename, reorder, drop, type-cast", "Prep"),
    ("✅", "12 Data Validation", "Schema validation, custom rules", "Prep"),
    # EDA (13-18)
    ("📊", "13 Descriptive Statistics", "Mean/std/IQR, Q-Q plots, normality", "EDA"),
    ("📈", "14 EDA & Visualisation", "12+ chart types, choropleth, treemap", "EDA"),
    ("📉", "15 Advanced Charts", "Gantt, Sankey, Funnel, Radar", "EDA"),
    ("🔬", "16 Advanced Profiling", "Distribution fitting, Sweetviz", "EDA"),
    ("🔗", "17 Correlation Deep Dive", "Pearson/Spearman/Kendall, VIF", "EDA"),
    ("📊", "18 Dataset Diff", "Original vs cleaned, drift detection", "EDA"),
    # Statistics (19-20)
    ("📐", "19 Hypothesis Testing", "T-tests, Chi-square, ANOVA", "Statistics"),
    ("🔬", "20 AB Testing Calculator", "Sample size, significance, power", "Statistics"),
    # Transform (21-22)
    ("🔗", "21 Data Merging", "4 join types, pivot table builder", "Transform"),
    ("⚙️", "22 Data Transformation", "Log/sqrt/Box-Cox, binning", "Transform"),
    # Engineering (23-25)
    ("⚙️", "23 Feature Engineering", "7 encodings + 3 scalers + PCA", "Engineering"),
    ("🧬", "24 Feature Selection", "Variance threshold, RFE, SelectKBest", "Engineering"),
    ("📐", "25 Dimensionality Reduction", "PCA, t-SNE, explained variance", "Engineering"),
    # ML (26-30)
    ("🤖", "26 ML Baseline", "7 algorithms, K-fold CV, ROC/PR", "ML"),
    ("⚖️", "27 Class Imbalance", "SMOTE, over/undersampling", "ML"),
    ("🏆", "28 Model Comparison", "Side-by-side benchmarking", "ML"),
    ("🔍", "29 Model Explainability", "Permutation importance, PDP, ICE", "ML"),
    ("🧪", "30 Hyperparameter Guide", "GridSearch/RandomSearch simulator", "ML"),
    # Analysis (31-36)
    ("📅", "31 Time Series", "STL decomposition, ADF, ACF/PACF", "Analysis"),
    ("📝", "32 Text Analysis", "TF-IDF, N-grams, sentiment", "Analysis"),
    ("🗺️", "33 Geospatial Analysis", "Choropleth, point clustering", "Analysis"),
    ("🔎", "34 Search & Compare", "Full-text search, segment builder", "Analysis"),
    ("📈", "35 What-If Analysis", "Scenario simulator, Monte Carlo", "Analysis"),
    ("📋", "36 SQL Query Console", "DuckDB SQL, window functions", "Query"),
    # Security (37)
    ("🔐", "37 Data Privacy & Masking", "8 masking methods, GDPR/NDPR", "Security"),
    # Governance (38-41)
    ("📜", "38 Data Contracts", "Schema validation, SLAs", "Governance"),
    ("⚖️", "39 Compliance Center", "GDPR/NDPR checklist, DPIA", "Governance"),
    ("📋", "40 Retention Policy Mgr", "Time-based rules, legal holds", "Governance"),
    ("🔗", "41 Data Lineage Tracker", "Column-level lineage, impact analysis", "Governance"),
    # Operations (42-43)
    ("🔔", "42 Data Monitor & Alerts", "10 rule types, dashboard", "Operations"),
    ("🔄", "43 Disaster Recovery", "DR plan, RPO/RTO, runbook", "Operations"),
    # Export (44)
    ("📤", "44 Export & Report", "CSV, Excel, Parquet, .ipynb", "Export"),
    # Reporting (45-47)
    ("📊", "45 Data Storytelling", "Auto narrative, key stats", "Reporting"),
    ("📝", "46 Report Builder", "Custom HTML report", "Reporting"),
    ("📝", "47 Audit & Compliance Rpt", "GDPR/NDPR/SOC 2 mapping", "Reporting"),
    # Enterprise (48-52)
    ("📊", "48 Enterprise KPI Dashboard", "Executive KPIs, gauges", "Enterprise"),
    ("👥", "49 Collaboration Hub", "Team notes, annotations", "Enterprise"),
    ("📡", "50 API Doc Generator", "OpenAPI 3.0 spec", "Enterprise"),
    ("📥", "51 Pipeline Builder", "Visual ETL workflow", "Enterprise"),
    ("📊", "52 Dashboard Builder", "Widget-based dashboards", "Enterprise"),
    # Education (53-61)
    ("🎓", "53 Learning Hub", "Glossary, concepts, quiz", "Education"),
    ("📓", "54 Notebook Playground", "Code cells, .ipynb download", "Education"),
    ("🚀", "55 Deployment Guide", "Streamlit, Docker, cloud", "Education"),
    ("📝", "56 Project Journal", "Experiment tracking, decisions log", "Education"),
    ("🗺️", "57 DS Roadmap", "Learning paths, milestones", "Education"),
    ("🎓", "58 Interactive Tutorials", "Guided lessons, exercises", "Education"),
    ("🚀", "59 Project Ideas", "Real-world projects, datasets", "Education"),
    ("📚", "60 DS Glossary", "200+ terms, definitions", "Education"),
    ("🏆", "61 DS Quiz", "Knowledge test, score tracking", "Education"),
    # V3 Enhanced (62-76)
    ("📚", "62 Curriculum Tracker", "3MTT/LASU-aligned paths, progress tracking", "Education"),
    ("🧩", "63 Code Challenges", "Python exercises by level, instant feedback", "Education"),
    ("🏆", "64 Achievement System", "Badges, milestones, gamified progress", "Education"),
    ("🏷️", "65 Data Catalog", "Metadata registry, business context", "Enterprise"),
    ("📉", "66 Causal Inference", "DAG builder, treatment effects", "Analysis"),
    ("🕸️", "67 Network Analysis", "Graph analysis, centrality, communities", "Analysis"),
    ("🔍", "68 Anomaly Detection", "IQR/Z-Score/Isolation Forest dashboard", "Operations"),
    ("⏳", "69 Survival Analysis", "Kaplan-Meier, hazard rates", "Analysis"),
    ("🏗️", "70 Workflow Scheduler", "Task scheduling, dependencies, templates", "Operations"),
    ("🏷️", "71 Feature Store", "Centralized feature management", "Enterprise"),
    ("💰", "72 Cost Estimator", "ML cost/ROI calculator, tool comparison", "Enterprise"),
    ("🔐", "73 Model Registry", "Model versioning, approval workflows", "Enterprise"),
    ("📜", "74 Audit Trail Viewer", "Complete audit log search/export", "Security"),
    ("🎓", "75 Certificate Generator", "HMG Academy certificates, verification", "Education"),
    ("🏭", "76 Data Factory", "End-to-end pipeline, quality gates, SLAs", "Enterprise"),
]

cat_colors = {
    "Collection": "tag-orange", "Prep": "", "EDA": "tag", "Statistics": "tag",
    "Transform": "tag-orange", "Engineering": "tag", "ML": "tag",
    "Analysis": "tag", "Query": "tag-orange", "Security": "tag-ent",
    "Governance": "tag-ent", "Operations": "tag-ent", "Export": "tag-orange",
    "Reporting": "tag-orange", "Enterprise": "tag-ent", "Education": "tag-new",
}

cols = st.columns(4)
for i, (icon, name, desc, cat) in enumerate(mods):
    is_ent = cat in ["Enterprise", "Governance", "Operations", "Security"]
    card_cls = "feature-card ent-card" if is_ent else "feature-card"
    tag_cls = cat_colors.get(cat, "tag")
    with cols[i % 4]:
        st.markdown(f"""
        <div class="{card_cls}">
            <div style="font-size:1.4rem;">{icon}</div>
            <h4>{name}</h4>
            <span class="{tag_cls}">{cat}</span>
            <p>{desc[:110]}...</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════ NOTEBOOK GENERATOR SECTION ═══════════════
st.markdown("---")
st.markdown("### 📓 Generate Jupyter Notebook (.ipynb)")

st.markdown("""
> **New Feature!** Generate a comprehensive, well-structured Jupyter notebook from your analysis. 
> The notebook includes all code, explanations, and educational content — ready to run locally or in Google Colab.
> Every notebook is watermarked with HMG Academy branding.
""")

col1, col2, col3 = st.columns(3)
with col1:
    include_eda = st.checkbox("📊 Include EDA", value=True, key="nb_eda")
    include_cleaning = st.checkbox("🧹 Include Cleaning", value=True, key="nb_cleaning")
    include_stats = st.checkbox("📐 Include Statistics", value=True, key="nb_stats")
with col2:
    include_viz = st.checkbox("📈 Include Visualisations", value=True, key="nb_viz")
    include_ml = st.checkbox("🤖 Include ML Pipeline", value=True, key="nb_ml")
    include_deploy = st.checkbox("🚀 Include Deployment", value=True, key="nb_deploy")
with col3:
    include_feature_eng = st.checkbox("⚙️ Include Feature Engineering", value=True, key="nb_fe")
    include_explain = st.checkbox("🔍 Include Explainability", value=True, key="nb_explain")
    include_branded = st.checkbox("🏷️ HMG Branding", value=True, key="nb_brand")

if st.button("📓 Generate & Download .ipynb", use_container_width=True):
    if not check_export_limit():
        st.error("⏱️ Export limit reached. Please wait.")
    elif st.session_state.get("df") is None:
        st.warning("Load a dataset first to generate a contextual notebook.")
    else:
        try:
            from notebook_generator import generate_full_notebook
            dfc = st.session_state.get("df_cleaned")
            df_info = {
                "filename": st.session_state.get("filename", "dataset"),
                "rows": len(dfc), "cols": len(dfc.columns)
            }
            options = {
                "include_eda": include_eda,
                "include_cleaning": include_cleaning,
                "include_stats": include_stats,
                "include_visualisation": include_viz,
                "include_ml": include_ml,
                "include_deployment": include_deploy,
            }
            notebook_json = generate_full_notebook(df_info, st.session_state.get("notebook_operations", []), options)
            fname = st.session_state.get("filename", "data").rsplit(".", 1)[0]
            st.download_button(
                "💾 Download Jupyter Notebook (.ipynb)",
                data=notebook_json,
                file_name=f"{fname}_dsflow_analysis.ipynb",
                mime="application/json",
                use_container_width=True
            )
            log("Generated notebook", fname)
            st.success("✅ Notebook generated! Click the download button above.")
        except Exception as e:
            st.error(f"Notebook generation error: {sanitise_string(str(e))}")

# ═══════════════ TABS ═══════════════
st.markdown("---")
tab_guide, tab_builder, tab_brand, tab_tech, tab_security = st.tabs([
    "📖 Platform Guide", "👨‍💻 About the Builder", "🏢 HMG Ecosystem", "💻 Tech Stack", "🔒 Security"
])

with tab_guide:
    st.markdown("""## 📖 How to Use DataScience Flow v10.0

### 🎓 Learning Paths
- **Beginner** (6 phases) — Upload → Explore → Quality → Clean → Visualise → Story
- **Intermediate** (9 phases) — + Hypothesis → SQL → Feature Engineering
- **Advanced** (12 phases) — + ML → Comparison → Explainability
- **Enterprise** (15 phases) — + Contracts → Compliance → DR

### 📓 Jupyter Notebook Generation
1. Load your dataset
2. Perform your analysis using the modules
3. Click "Generate & Download .ipynb" above
4. Open the downloaded notebook in Jupyter, VS Code, or Google Colab
5. Every notebook includes: code, explanations, educational content, and HMG Academy branding

### 💻 Technology Stack (100% Free)
| Component | Technology | Cost |
|-----------|-----------|------|
| Framework | Streamlit 1.32+ | Free |
| ML | Scikit-learn, Imbalanced-learn | Free |
| SQL | DuckDB (in-memory) | Free |
| EDA | Sweetviz | Free |
| Geo | Folium | Free |
| NLP | NLTK, TextBlob | Free |
| Security | HMAC, rate limiting, input sanitisation | Free |
| AI API | **None — 100% rule-based** | **₦0 Forever** |
""")

with tab_builder:
    st.markdown("""## 👨‍💻 About the Builder

**Adewale Samson Adeagbo** — Data Scientist | EdTech Builder | Virtual Tutor | AI-Augmented Solutions Developer

15+ years classroom teaching. B.Sc.(Ed) Computer Science Education (LASU, 2023). 3MTT Data Science (2025). Founder, HMG Concepts (est. 2015).

One identity. Three builder modes:
- 🏫 **EdTech Builder** — CBT Pro, LMS platforms, student analytics
- 📊 **DataTech Builder** — 7 ML models deployed, 11 data-tool simulators
- ✝️ **FaithTech Builder** — Gospel platforms, dramavangelism, techvangelism

**34+ projects deployed** across education, technology, media, and faith.

**HMG Academy** is a subsidiary of **HMG Concepts** — the education arm providing virtual tutoring, CBT systems, LMS platforms, and data science training.

[🌐 Portfolio](https://cssadewale.pages.dev/) · [🏢 HMG Concepts](https://hmgconcepts.pages.dev/) · [🎓 HMG Academy](https://hmgacademy.pages.dev/)
[💻 HMG Technologies](https://hmgtechnologies.pages.dev/) · [📢 HMG Media](https://hmgmedia.pages.dev/) · [✝️ HMG Gospel](https://hmggospel.pages.dev/)
📧 adeagboadewalesamson@gmail.com · 📞 +234 810 086 6322 · 📍 Lagos, Nigeria
""")

with tab_brand:
    st.markdown("""## 🏢 HMG Ecosystem — His Marvellous Grace

**HMG Concepts** (est. 2015) is a Nigerian education and technology brand. One brand with four living missions.

**DataScience Flow is part of the HMG Academy ecosystem** — the education and training arm.

### 🎓 HMG Academy — Home of DataScience Flow
A full-service, strictly virtual learning institution. The data science training arm of HMG Concepts.
- WAEC · NECO · GCE · UTME prep
- IGCSE · IELTS · JUPEB · SAT preparation
- Free CBT Pro platform & lesson notes
- **DataScience Flow** — the flagship data science workflow platform
- [Visit HMG Academy →](https://hmgacademy.pages.dev/)

### 💻 HMG Technologies
The innovation arm — AI-augmented tools, CBT systems, ML models, simulators.
- [Visit HMG Technologies →](https://hmgtechnologies.pages.dev/)

### 📢 HMG Media
The content and visibility arm — purpose-led media.
- [Visit HMG Media →](https://hmgmedia.pages.dev/)

### ✝️ HMG Gospel
The faith arm — Christ-centred digital outreach.
- [Visit HMG Gospel →](https://hmggospel.pages.dev/)

### 🏢 HMG Concepts (Parent)
The umbrella brand. [Visit HMG Concepts →](https://hmgconcepts.pages.dev/)
""")

with tab_tech:
    st.markdown("""## 💻 Technology Stack — 100% Free, Open Source

| Component | Technology | Purpose | Cost |
|-----------|-----------|---------|------|
| Framework | Streamlit 1.32+ | Interactive web app | Free |
| Data | Pandas, NumPy | Manipulation & computation | Free |
| ML | Scikit-learn | Machine learning | Free |
| Security | HMAC-SHA256 | Subscription integrity verification | Free |
| Rate Limiting | Custom module | Anti-abuse protection | Free |
| Input Safety | Regex sanitisation | XSS & injection prevention | Free |
| SQL | DuckDB | In-memory SQL engine | Free |
| Viz | Plotly, Matplotlib, Seaborn | Charts & visualisations | Free |
| Profiling | Sweetviz | Auto EDA reports | Free |
| Stats | SciPy, Statsmodels | Statistical tests | Free |
| Geo | Folium | Maps & geospatial | Free |
| NLP | NLTK, TextBlob | Text & sentiment | Free |
| Notebook | nbformat JSON | .ipynb generation | Free |
| AI API | **None** | **100% rule-based** | **₦0** |
""")

with tab_security:
    st.markdown("""## 🔒 Security Features

### Authentication & Subscription Security
- **HMAC-SHA256 Token Verification**: Every subscription session is verified with a tamper-proof token. Any modification to session state invalidates the token.
- **Email Reuse Prevention**: Each email can only activate one free trial per 24-hour period.
- **Trial Duration Enforcement**: Trial expiry is validated server-side — cannot be extended beyond 24h.
- **Session Integrity Checks**: Every page load verifies subscription integrity.

### Anti-Bypass Measures
- **Rate Limiting**: Maximum 60 actions per minute, 30 exports per hour.
- **Upload Validation**: File type, size, and content-type checks.
- **Input Sanitisation**: All user inputs are sanitised for XSS, SQL injection, and HTML injection.
- **Session Timeout**: Sessions expire after 2 hours of inactivity.

### Anti-Forking Protection
- **Source Code Watermarking**: Every file contains copyright notices and builder identification.
- **License File**: Custom license restricting forking and redistribution.
- **GitHub Repo Settings**: Set to prevent forking (configure in repo settings).
- **Export Watermarking**: All exports (CSV, .ipynb, reports) contain HMG Academy branding.

### Data Security
- **No Persistent Storage**: All data stays in the browser session only.
- **No External API Calls**: Zero data leaves the platform.
- **No Tracking**: `gatherUsageStats = false`
- **SQL Injection Prevention**: Dangerous SQL commands are blocked.
- **URL Validation**: Only http/https URLs allowed for web data import.
""")

# ═══════════════ FOOTER ═══════════════
st.markdown(f"""
<div class="footer-section">
    <p style="margin-bottom:8px;"><strong>Adewale Samson Adeagbo</strong></p>
    <p style="font-size:0.85rem; color:var(--text-secondary);">
        Data Scientist · EdTech Builder · Virtual Tutor · AI-Augmented Solutions Developer<br>
        Founder, <strong>HMG Concepts</strong> (est. 2015) — <strong>HMG Academy</strong> · HMG Technologies · HMG Media · HMG Gospel
    </p>
    <p style="font-size:0.85rem; margin-top:8px;">
        <a href="https://cssadewale.pages.dev/" target="_blank">🌐 Portfolio</a> ·
        <a href="https://hmgconcepts.pages.dev/" target="_blank">🏢 HMG Concepts</a> ·
        <a href="https://hmgacademy.pages.dev/" target="_blank">🎓 HMG Academy</a> ·
        <a href="https://hmgtechnologies.pages.dev/" target="_blank">💻 HMG Technologies</a> ·
        <a href="https://hmgmedia.pages.dev/" target="_blank">📢 HMG Media</a> ·
        <a href="https://hmggospel.pages.dev/" target="_blank">✝️ HMG Gospel</a>
    </p>
    <p style="font-size:0.82rem; color:var(--text-secondary);">
        📧 adeagboadewalesamson@gmail.com · 📞 +234 810 086 6322 · 📍 Lagos, Nigeria
    </p>
    <p style="font-size:0.78rem; color:var(--text-secondary); margin-top:12px;">
        DataScience Flow v10.0 — 76-Modules — Part of HMG Academy Ecosystem<br>
        Subsidiary of HMG Concepts (est. 2015) — His Marvellous Grace<br>
        100% Free Tools · No AI API · 🔒 Secured Platform<br>
        © 2015-2026 HMG Concepts — All Rights Reserved
    </p>
</div>
""", unsafe_allow_html=True)
