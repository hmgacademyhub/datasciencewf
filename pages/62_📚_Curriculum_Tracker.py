"""
Module 62: Curriculum Tracker — DataScience Flow v10.0
Structured learning paths aligned with 3MTT, LASU CS, and industry standards
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Curriculum Tracker | DataScience Flow", page_icon="📚", layout="wide")

from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription, has_curriculum_access
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

st.markdown("""
## 📚 Curriculum Tracker — Module 62

> **What is a Curriculum Tracker?** A structured learning path that guides you through the data science 
> workflow from beginner to enterprise level. Aligned with Nigeria's 3MTT programme, LASU Computer Science 
> Education standards, and global industry requirements.

### 🎓 HMG Academy Learning Philosophy

At HMG Academy, we believe in **"His Marvellous Grace"** — that everyone deserves access to quality 
education regardless of their background. Our curriculum is designed by **Adewale Samson Adeagbo**, 
a B.Sc.(Ed) Computer Science Education graduate from LASU (2023) and 3MTT Data Science fellow (2025), 
who brings 15+ years of classroom teaching experience to data science education.

### 📐 Learning Paths by Level

| Level | Target Audience | Duration | Modules | Prerequisites |
|-------|----------------|----------|---------|---------------|
| 🟢 Beginner | Students, career changers | 4-6 weeks | 01-12, 53 | None |
| 🟡 Intermediate | Junior analysts, 200-level students | 6-8 weeks | 13-25, 54-56 | Beginner complete |
| 🔴 Advanced | Data scientists, 400-level students | 8-12 weeks | 26-36, 57-60 | Intermediate complete |
| 🟣 Enterprise | Team leads, organizations | 4-6 weeks | 37-52, 61-76 | Advanced complete |

### 🏗️ Curriculum Alignment

| Standard | Alignment |
|----------|-----------|
| **3MTT Nigeria** | Data Science track — all competencies covered |
| **LASU CS Education** | B.Sc.(Ed) practical requirements |
| **Google Data Analytics** | Process: Ask→Prepare→Process→Analyze→Share→Act |
| **IBM Data Science** | Methodology: Business→Data→Model→Deploy→Feedback |
| **Nigeria NDPR** | Data governance and compliance modules |
| **GDPR** | Privacy, masking, consent modules |
""")

# Initialize progress tracking
if "curriculum_progress" not in st.session_state:
    st.session_state["curriculum_progress"] = {}

tab_beginner, tab_intermediate, tab_advanced, tab_enterprise, tab_progress = st.tabs([
    "🟢 Beginner", "🟡 Intermediate", "🔴 Advanced", "🟣 Enterprise", "📊 My Progress"
])

BEGINNER_MODULES = {
    "Week 1: Data Collection & Understanding": [
        {"id": "01", "name": "Data Collection Hub", "desc": "Learn to import data from multiple sources", "skills": ["File handling", "Data formats", "Web scraping"]},
        {"id": "02", "name": "Data Simulation", "desc": "Generate synthetic data for practice", "skills": ["Random sampling", "Distributions", "Data generation"]},
        {"id": "06", "name": "Data Exploration", "desc": "Understand your dataset's structure", "skills": ["Head/tail", "dtypes", "describe()", "info()"]},
    ],
    "Week 2: Data Cleaning Essentials": [
        {"id": "07", "name": "Missing Values", "desc": "Find and handle missing data", "skills": ["isnull()", "fillna()", "Imputation strategies"]},
        {"id": "08", "name": "Duplicates", "desc": "Detect and remove duplicate records", "skills": ["duplicated()", "drop_duplicates()"]},
        {"id": "09", "name": "Outlier Detection", "desc": "Identify statistical outliers", "skills": ["IQR", "Z-Score", "Box plots"]},
    ],
    "Week 3: Data Quality & Validation": [
        {"id": "10", "name": "Data Quality Audit", "desc": "Score your data quality", "skills": ["Completeness", "Consistency", "Accuracy"]},
        {"id": "11", "name": "Column Manager", "desc": "Organize your columns", "skills": ["Rename", "Reorder", "Type casting"]},
        {"id": "12", "name": "Data Validation", "desc": "Enforce data rules", "skills": ["Schema validation", "Range checks", "Custom rules"]},
    ],
    "Week 4: Introduction to EDA": [
        {"id": "13", "name": "Descriptive Statistics", "desc": "Summarize your data numerically", "skills": ["Mean", "Median", "Std", "Q-Q plots"]},
        {"id": "14", "name": "EDA & Visualisation", "desc": "Create your first charts", "skills": ["Bar", "Line", "Scatter", "Histogram"]},
        {"id": "53", "name": "Learning Hub", "desc": "Review key concepts and quiz yourself", "skills": ["Glossary", "Concepts", "Quiz"]},
    ],
}

INTERMEDIATE_MODULES = {
    "Week 5-6: Advanced EDA & Statistics": [
        {"id": "15", "name": "Advanced Charts", "desc": "Master complex visualizations", "skills": ["Gantt", "Sankey", "Funnel", "Radar"]},
        {"id": "16", "name": "Advanced Profiling", "desc": "Automated EDA reports", "skills": ["Sweetviz", "Distribution fitting", "Correlation maps"]},
        {"id": "17", "name": "Correlation Deep Dive", "desc": "Understand variable relationships", "skills": ["Pearson", "Spearman", "VIF", "Multicollinearity"]},
        {"id": "19", "name": "Hypothesis Testing", "desc": "Test statistical claims", "skills": ["T-tests", "Chi-square", "ANOVA", "P-values"]},
        {"id": "20", "name": "AB Testing", "desc": "Design and analyze experiments", "skills": ["Sample size", "Power analysis", "Statistical significance"]},
    ],
    "Week 7-8: Data Transformation & Engineering": [
        {"id": "21", "name": "Data Merging", "desc": "Combine datasets effectively", "skills": ["Joins", "Merge", "Pivot tables"]},
        {"id": "22", "name": "Data Transformation", "desc": "Transform distributions and scales", "skills": ["Log transform", "Box-Cox", "Binning"]},
        {"id": "23", "name": "Feature Engineering", "desc": "Create powerful features", "skills": ["Encoding", "Scaling", "PCA", "Polynomial"]},
        {"id": "24", "name": "Feature Selection", "desc": "Choose the right features", "skills": ["Variance threshold", "RFE", "SelectKBest"]},
        {"id": "25", "name": "Dimensionality Reduction", "desc": "Reduce complexity", "skills": ["PCA", "t-SNE", "Explained variance"]},
    ],
    "Week 9-10: Applied Skills": [
        {"id": "54", "name": "Notebook Playground", "desc": "Write and test Python code", "skills": ["Python", "Pandas", "Code cells"]},
        {"id": "55", "name": "Deployment Guide", "desc": "Deploy your first app", "skills": ["Streamlit", "Docker", "Cloud"]},
        {"id": "56", "name": "Project Journal", "desc": "Track your experiments", "skills": ["Documentation", "Experiment tracking"]},
    ],
}

ADVANCED_MODULES = {
    "Week 11-13: Machine Learning Pipeline": [
        {"id": "26", "name": "ML Baseline", "desc": "Train your first ML models", "skills": ["Logistic Regression", "Random Forest", "SVM", "Cross-validation"]},
        {"id": "27", "name": "Class Imbalance", "desc": "Handle imbalanced datasets", "skills": ["SMOTE", "Oversampling", "Class weights"]},
        {"id": "28", "name": "Model Comparison", "desc": "Compare model performance", "skills": ["Metrics", "Ranking", "Best model selection"]},
        {"id": "29", "name": "Model Explainability", "desc": "Understand model predictions", "skills": ["Permutation importance", "PDP", "ICE plots"]},
        {"id": "30", "name": "Hyperparameter Guide", "desc": "Optimize model performance", "skills": ["GridSearch", "RandomSearch", "Cross-validation"]},
    ],
    "Week 14-16: Specialized Analysis": [
        {"id": "31", "name": "Time Series", "desc": "Analyze temporal data", "skills": ["Decomposition", "ADF test", "ACF/PACF"]},
        {"id": "32", "name": "Text Analysis", "desc": "Process and analyze text data", "skills": ["TF-IDF", "Sentiment", "N-grams"]},
        {"id": "33", "name": "Geospatial Analysis", "desc": "Work with geographic data", "skills": ["Choropleth", "Point clustering", "Maps"]},
        {"id": "34", "name": "Search & Compare", "desc": "Advanced data querying", "skills": ["Full-text search", "Segment builder"]},
        {"id": "35", "name": "What-If Analysis", "desc": "Scenario modeling", "skills": ["Sensitivity", "Monte Carlo", "Tornado charts"]},
        {"id": "36", "name": "SQL Query Console", "desc": "Query data with SQL", "skills": ["DuckDB", "Window functions", "CTEs"]},
    ],
    "Week 17-18: Capstone & Portfolio": [
        {"id": "57", "name": "DS Roadmap", "desc": "Plan your career path", "skills": ["Career planning", "Skill gaps"]},
        {"id": "58", "name": "Interactive Tutorials", "desc": "Hands-on guided lessons", "skills": ["Practice", "Exercises"]},
        {"id": "59", "name": "Project Ideas", "desc": "Build your portfolio", "skills": ["Real-world projects", "Datasets"]},
        {"id": "60", "name": "DS Glossary", "desc": "Master the terminology", "skills": ["200+ terms", "Definitions"]},
        {"id": "61", "name": "DS Quiz", "desc": "Test your knowledge", "skills": ["Assessment", "Score tracking"]},
    ],
}

ENTERPRISE_MODULES = {
    "Week 19-20: Security & Governance": [
        {"id": "37", "name": "Data Privacy & Masking", "desc": "Protect sensitive data", "skills": ["PII detection", "8 masking methods", "GDPR/NDPR"]},
        {"id": "38", "name": "Data Contracts", "desc": "Enforce data agreements", "skills": ["Schema validation", "SLAs", "Type enforcement"]},
        {"id": "39", "name": "Compliance Center", "desc": "Meet regulatory requirements", "skills": ["GDPR checklist", "DPIA", "Consent log"]},
        {"id": "40", "name": "Retention Policy Mgr", "desc": "Manage data lifecycle", "skills": ["Time-based rules", "Legal holds"]},
        {"id": "41", "name": "Data Lineage Tracker", "desc": "Track data provenance", "skills": ["Column lineage", "Impact analysis"]},
    ],
    "Week 21-22: Operations & Reporting": [
        {"id": "42", "name": "Data Monitor & Alerts", "desc": "Real-time data monitoring", "skills": ["Rules engine", "Dashboard", "Alerts"]},
        {"id": "43", "name": "Disaster Recovery", "desc": "Prepare for data disasters", "skills": ["RPO/RTO", "Backup plans", "Runbooks"]},
        {"id": "44", "name": "Export & Report", "desc": "Multi-format data export", "skills": ["CSV", "Parquet", "HTML", "ipynb"]},
        {"id": "45", "name": "Data Storytelling", "desc": "Communicate insights effectively", "skills": ["Narrative", "Key stats", "Correlation highlights"]},
        {"id": "46", "name": "Report Builder", "desc": "Build professional reports", "skills": ["Multi-section", "HTML", "Professional output"]},
        {"id": "47", "name": "Audit & Compliance Rpt", "desc": "Generate audit evidence", "skills": ["GDPR/NDPR/SOC 2", "Evidence bundles"]},
    ],
    "Week 23-24: Enterprise Tools": [
        {"id": "48", "name": "Enterprise KPI Dashboard", "desc": "Executive data dashboards", "skills": ["KPIs", "Gauges", "Radar charts"]},
        {"id": "49", "name": "Collaboration Hub", "desc": "Team collaboration features", "skills": ["Notes", "Annotations", "Shared queries"]},
        {"id": "50", "name": "API Doc Generator", "desc": "Document your data APIs", "skills": ["OpenAPI 3.0", "cURL", "Markdown"]},
        {"id": "51", "name": "Pipeline Builder", "desc": "Build data pipelines", "skills": ["ETL", "Visual builder", "Templates"]},
        {"id": "52", "name": "Dashboard Builder", "desc": "Create custom dashboards", "skills": ["Widgets", "Layout", "Interactivity"]},
    ],
}

def render_modules(modules_dict, level_name, level_color):
    """Render a curriculum level's modules with progress tracking."""
    progress = st.session_state.get("curriculum_progress", {})
    total = sum(len(mods) for mods in modules_dict.values())
    completed = sum(1 for m in modules_dict.values() for mod in m if progress.get(mod["id"], False))
    
    st.metric(f"{level_name} Progress", f"{completed}/{total} modules ({completed/total*100:.0f}%)" if total > 0 else "0%")
    
    if total > 0:
        st.progress(completed / total)
    
    for week, mods in modules_dict.items():
        st.markdown(f"### {week}")
        for mod in mods:
            is_done = progress.get(mod["id"], False)
            icon = "✅" if is_done else "⬜"
            with st.expander(f"{icon} Module {mod['id']}: {mod['name']}", expanded=not is_done):
                st.markdown(f"**Description:** {mod['desc']}")
                st.markdown("**Skills you'll learn:**")
                for skill in mod["skills"]:
                    st.markdown(f"- `{skill}`")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"{'✅ Completed' if is_done else '☐ Mark Complete'}", key=f"prog_{mod['id']}"):
                        st.session_state["curriculum_progress"][mod["id"]] = not is_done
                        st.rerun()
                with c2:
                    if is_done:
                        st.success("Module completed! 🎉")

with tab_beginner:
    render_modules(BEGINNER_MODULES, "🟢 Beginner", "#4f8ef7")
    st.markdown("""
    ---
    ### 🎯 Beginner Learning Outcomes
    After completing the Beginner path, you will be able to:
    - ✅ Load and inspect datasets of various formats
    - ✅ Identify and handle missing values, duplicates, and outliers
    - ✅ Perform basic data quality assessments
    - ✅ Create summary statistics and basic visualizations
    - ✅ Understand the data science workflow from Collection → EDA
    
    **Aligned with:** 3MTT Data Science — Data Collection & Cleaning competencies
    """)

with tab_intermediate:
    render_modules(INTERMEDIATE_MODULES, "🟡 Intermediate", "#FFB74D")
    st.markdown("""
    ---
    ### 🎯 Intermediate Learning Outcomes
    After completing the Intermediate path, you will be able to:
    - ✅ Create advanced visualizations and automated EDA reports
    - ✅ Perform hypothesis tests and design AB experiments
    - ✅ Engineer features and select the most important ones
    - ✅ Apply dimensionality reduction techniques
    - ✅ Write and deploy Jupyter notebooks
    
    **Aligned with:** 3MTT Data Science — Feature Engineering & Analysis competencies
    """)

with tab_advanced:
    render_modules(ADVANCED_MODULES, "🔴 Advanced", "#FF6B6B")
    st.markdown("""
    ---
    ### 🎯 Advanced Learning Outcomes
    After completing the Advanced path, you will be able to:
    - ✅ Train, compare, and optimize ML models
    - ✅ Handle imbalanced datasets and explain model predictions
    - ✅ Analyze time series, text, and geospatial data
    - ✅ Write SQL queries for data analysis
    - ✅ Build a data science portfolio with real projects
    
    **Aligned with:** 3MTT Data Science — ML & Specialized Analysis competencies
    """)

with tab_enterprise:
    render_modules(ENTERPRISE_MODULES, "🟣 Enterprise", "#8b5cf6")
    st.markdown("""
    ---
    ### 🎯 Enterprise Learning Outcomes
    After completing the Enterprise path, you will be able to:
    - ✅ Implement data governance and compliance programs
    - ✅ Set up data monitoring and disaster recovery
    - ✅ Build data pipelines and dashboards
    - ✅ Generate audit reports and API documentation
    - ✅ Lead data teams with proper collaboration workflows
    
    **Aligned with:** GDPR/NDPR compliance, SOC 2, Enterprise Data Management
    """)

with tab_progress:
    st.markdown("### 📊 My Learning Progress")
    progress = st.session_state.get("curriculum_progress", {})
    
    all_modules = []
    for modules_dict in [BEGINNER_MODULES, INTERMEDIATE_MODULES, ADVANCED_MODULES, ENTERPRISE_MODULES]:
        for week, mods in modules_dict.items():
            for mod in mods:
                all_modules.append({
                    "Module": mod["id"],
                    "Name": mod["name"],
                    "Week": week,
                    "Completed": "✅" if progress.get(mod["id"], False) else "⬜",
                })
    
    if all_modules:
        df = pd.DataFrame(all_modules)
        completed = len([m for m in all_modules if m["Completed"] == "✅"])
        total = len(all_modules)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Modules Completed", f"{completed}/{total}")
        c2.metric("Completion Rate", f"{completed/total*100:.1f}%")
        c3.metric("Remaining", f"{total - completed}")
        
        st.progress(completed / total)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export progress
        if st.button("📥 Export Progress Report"):
            report = json.dumps({
                "platform": "DataScience Flow v10.0",
                "user": st.session_state.get("sub_auth_email", "anonymous"),
                "date": datetime.now().isoformat(),
                "total_modules": total,
                "completed": completed,
                "rate": f"{completed/total*100:.1f}%",
                "progress": progress,
            }, indent=2)
            st.download_button("💾 Download Progress (JSON)", report, "curriculum_progress.json", "application/json")
    
    st.markdown("""
    ---
    💡 **Key Takeaway:** Consistency beats intensity. Spend 30 minutes daily on the curriculum rather than 
    cramming on weekends. Each module builds on the previous one — don't skip ahead.
    
    🏗️ **HMG Academy Vision:** Education is the most powerful weapon you can use to change the world. 
    DataScience Flow embodies HMG Concepts' founding conviction — "His Marvellous Grace" — ensuring 
    that quality data science education is accessible to every Nigerian student and professional.
    """)

# ═══════════════════════════════════════════════════════════════
# BRAND FOOTER — DataScience Flow v10.0 | HMG Academy
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:16px 0; font-size:0.82rem; color:#A0A8B8;">
<b>DataScience Flow</b> v10.0 — Part of <b>HMG Academy</b> Ecosystem — Subsidiary of <b>HMG Concepts</b> (est. 2015)<br>
Built by <b>Adewale Samson Adeagbo</b> | 🔒 Secured Platform | "His Marvellous Grace"<br>
🏗️ HMG Academy · HMG Technologies · HMG Media · HMG Gospel<br>
<a href="https://hmgacademy.pages.dev" style="color:#6C63FF;">hmgacademy.pages.dev</a> ·
<a href="https://hmgconcepts.pages.dev" style="color:#6C63FF;">hmgconcepts.pages.dev</a> ·
<a href="https://cssadewale.pages.dev" style="color:#6C63FF;">cssadewale.pages.dev</a>
</div>
""", unsafe_allow_html=True)
