"""
Module 61: DS Quiz — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
from datetime import datetime
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


st.set_page_config(page_title="Quiz | DataFlow v9.0", page_icon="🏆", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🏆 DATA SCIENCE QUIZ — Test Your Knowledge</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** A comprehensive 20-question quiz covering data fundamentals, statistics, machine learning, and data governance. Earn a certificate of completion!

**🎯 Why you need it:** Testing yourself is the best way to identify knowledge gaps. This quiz helps you verify what you've learned and discover what to study next.

**📖 How to use it:** Answer all 20 questions → submit → see your score → review explanations → earn your certificate.
""")

# Initialize quiz state
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

questions = [
    {"q": "What is the main difference between supervised and unsupervised learning?", "opts": ["Supervised uses labeled data; unsupervised doesn't", "Supervised is faster", "Unsupervised uses more data", "There is no difference"], "ans": 0, "exp": "Supervised learning uses labeled training data (you know the answers). Unsupervised learning finds patterns without labels."},
    {"q": "If your data has extreme outliers, which measure of central tendency should you use?", "opts": ["Mean", "Median", "Mode", "Range"], "ans": 1, "exp": "The median is robust to outliers — a few extreme values don't affect it. The mean can be significantly skewed by outliers."},
    {"q": "What does a p-value of 0.02 indicate?", "opts": ["The result is 98% true", "There's a 2% chance of seeing this result if the null hypothesis is true", "The data is 2% wrong", "The model is 98% accurate"], "ans": 1, "exp": "A p-value is the probability of observing your result (or more extreme) assuming the null hypothesis is true. p=0.02 means only a 2% chance of seeing this by random chance."},
    {"q": "What is overfitting in machine learning?", "opts": ["The model is too simple to capture patterns", "The model memorizes training data but fails on new data", "The model trains too slowly", "The model uses too many rows"], "ans": 1, "exp": "Overfitting means the model learns the noise in the training data instead of the underlying pattern. It performs well on training data but poorly on new, unseen data."},
    {"q": "Which imputation method is best for time series data?", "opts": ["Mean imputation", "Forward-fill (last observation carried forward)", "Random imputation", "Always delete the row"], "ans": 1, "exp": "Forward-fill uses the most recent known value, which makes sense for time series where values tend to be similar to the previous observation."},
    {"q": "What library powers the SQL Console in DataFlow?", "opts": ["MySQL", "PostgreSQL", "DuckDB", "SQLite"], "ans": 2, "exp": "DuckDB is an in-memory analytical SQL engine — fast, embedded, and perfect for data analysis without a database server."},
    {"q": "What technique helps prevent overfitting during model evaluation?", "opts": ["Using more features", "K-fold cross-validation", "Training on the test set", "Using only one algorithm"], "ans": 1, "exp": "K-fold CV splits data into K parts, trains on K-1 and tests on the remaining part, repeating K times. This gives a more reliable estimate of true model performance."},
    {"q": "In the IQR method, a value is an outlier if it falls below:", "opts": ["Q3 + 1.5×IQR", "Q1 - 1.5×IQR", "The median", "The mean ± 1 std"], "ans": 1, "exp": "The IQR method defines outliers as values below Q1 - 1.5×IQR or above Q3 + 1.5×IQR. The IQR is Q3 - Q1."},
    {"q": "What does 'No AI API' mean for DataScience Flow Suite?", "opts": ["The platform doesn't work", "All analysis uses free, local, open-source libraries — no paid external APIs", "AI is not used at all", "Only premium users get AI"], "ans": 1, "exp": "DataFlow performs all analysis locally using open-source Python libraries (scikit-learn, SciPy, etc.). No data is sent to OpenAI, Google, or any external service — keeping costs at ₦0."},
    {"q": "Which Nigerian regulation governs data protection?", "opts": ["GDPR", "NDPR", "CCPA", "FOIA"], "ans": 1, "exp": "NDPR (Nigeria Data Protection Regulation) is the Nigerian data protection law, enforced by the Nigeria Data Protection Bureau (NDPB). It's similar to the EU's GDPR."},
    {"q": "What is the primary purpose of feature scaling?", "opts": ["To make the model run faster", "To put all features on similar scales for fair comparison", "To reduce the number of features", "To create new features"], "ans": 1, "exp": "Features on different scales (e.g., age 0-100 vs income 0-1,000,000) can bias distance-based algorithms. Scaling puts everything on comparable footing."},
    {"q": "What is correlation?", "opts": ["Causation", "A measure of the linear relationship between two variables", "The average of two variables", "The maximum value in a column"], "ans": 1, "exp": "Correlation (r) measures the strength and direction of a linear relationship between two variables. Important: correlation does NOT imply causation!"},
    {"q": "What does SMOTE do?", "opts": ["Deletes outliers", "Creates synthetic examples of minority classes", "Scales features", "Selects the best features"], "ans": 1, "exp": "SMOTE (Synthetic Minority Oversampling Technique) creates synthetic data points for underrepresented classes, helping ML models learn from imbalanced datasets."},
    {"q": "Which module should you use FIRST when exploring a new dataset?", "opts": ["ML Baseline (Module 13)", "Data Exploration (Module 1)", "Export & Report (Module 8)", "Feature Engineering (Module 7)"], "ans": 1, "exp": "Always explore first! Module 1 (Data Exploration) gives you a complete structural overview — data types, shapes, anomalies — before any cleaning or analysis."},
    {"q": "What is the 68-95-99.7 rule?", "opts": ["A rule for data cleaning", "For normal distributions: 68% within 1σ, 95% within 2σ, 99.7% within 3σ", "A rule for feature selection", "A rule for choosing algorithms"], "ans": 1, "exp": "The empirical rule: in a normal distribution, approximately 68% of data falls within ±1 standard deviation of the mean, 95% within ±2σ, and 99.7% within ±3σ."},
    {"q": "What is the main advantage of using Parquet format?", "opts": ["It's human-readable", "Columnar storage — faster queries and smaller file size", "It's the only format Excel can read", "It's required for ML"], "ans": 1, "exp": "Parquet is a columnar storage format — it stores data by column rather than row. This means faster queries (read only needed columns) and better compression."},
    {"q": "In DataFlow, what does the Data Dictionary do?", "opts": ["Translates data to other languages", "Documents every column: meaning, type, allowed values, classification level", "Stores passwords", "Checks for spelling errors"], "ans": 1, "exp": "The Data Dictionary is structured documentation for every column: what it means, its data type, allowed values, classification (Public/Internal/Confidential/Restricted), and quality notes."},
    {"q": "What is PII?", "opts": ["Python Intelligence Interface", "Personally Identifiable Information", "Predictive Input Indicator", "Public Internet Information"], "ans": 1, "exp": "PII is any data that can identify a specific person: names, emails, phone numbers, addresses, ID numbers. Must be protected under privacy regulations."},
    {"q": "Which module helps you define what your data SHOULD look like?", "opts": ["Data Exploration (Module 1)", "Data Contracts (Module 32)", "Missing Values (Module 2)", "SQL Console (Module 23)"], "ans": 1, "exp": "Module 32 (Data Contracts) lets you define column-level schemas — required columns, types, value ranges, freshness/completeness/volume SLAs — and validate your data against them."},
    {"q": "Who built DataScience Flow Suite?", "opts": ["A large tech company", "Adewale Samson Adeagbo — a teacher and data scientist from Lagos, Nigeria", "A team of Silicon Valley engineers", "An AI company"], "ans": 1, "exp": "DataScience Flow Suite was built by Adewale Samson Adeagbo — a data scientist and educator with 17+ years of classroom teaching experience, founder of HMG Concepts in Lagos, Nigeria."},
]

if not st.session_state.quiz_started:
    st.markdown("### Ready to Test Your Knowledge?")
    st.markdown("- **20 questions** covering fundamentals, statistics, ML, and governance")
    st.markdown("- **No time limit** — take your time, learn as you go")
    st.markdown("- **Detailed explanations** for every answer")
    st.markdown("- **Earn a certificate** when you score 70% or above!")
    if st.button("🚀 Start Quiz"):
        st.session_state.quiz_started = True
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.rerun()

elif not st.session_state.quiz_submitted:
    st.markdown(f"### 📝 Question {len(st.session_state.quiz_answers)+1} of {len(questions)}")
    i = len(st.session_state.quiz_answers)
    q = questions[i]
    st.markdown(f"**{q['q']}**")
    ans = st.radio("Choose your answer:", q['opts'], key=f"q{i}")
    if st.button("Next →" if i < len(questions)-1 else "📤 Submit Quiz"):
        st.session_state.quiz_answers[i] = q['opts'].index(ans) if ans else 0
        if i == len(questions)-1:
            st.session_state.quiz_submitted = True
        st.rerun()

else:
    score = 0
    for i, q in enumerate(questions):
        if st.session_state.quiz_answers.get(i) == q['ans']:
            score += 1

    pct = score / len(questions) * 100
    
    st.markdown(f"## 🏆 Your Score: {score}/{len(questions)} ({pct:.0f}%)")
    
    if pct >= 90:
        st.balloons()
        st.success("🌟 **Outstanding!** You're a Data Science Champion! Deep understanding across all topics.")
    elif pct >= 70:
        st.success("✅ **Great job!** You have solid data science knowledge. Keep learning!")
    elif pct >= 50:
        st.warning("📚 **Good start!** Review the topics you missed and try again.")
    else:
        st.info("🌱 **You're learning!** Don't be discouraged — revisit the tutorials and glossary, then retake the quiz.")

    # Show certificate
    if pct >= 70:
        st.markdown("---")
        st.markdown("### 🎓 Your Certificate of Completion")
        cert_html = f"""
        <div style="background:linear-gradient(135deg,#161b22,#1c2129);border:4px solid #00d9a7;border-radius:20px;padding:3rem;text-align:center;max-width:700px;margin:0 auto;">
            <div style="font-size:1rem;color:#8b949e;letter-spacing:3px;">DATAFLOW ENTERPRISE SUITE v9.0</div>
            <div style="font-size:2rem;font-weight:900;color:#00d9a7;margin:1rem 0;">CERTIFICATE OF COMPLETION</div>
            <div style="font-size:1rem;color:#e6edf3;">This certifies that</div>
            <div style="font-size:1.5rem;font-weight:700;color:#00d9a7;margin:1rem 0;">{st.session_state.get('sub_auth_email', 'Data Science Learner')}</div>
            <div style="font-size:1rem;color:#e6edf3;">successfully completed the DataScience Flow Suite Knowledge Assessment</div>
            <div style="font-size:2.5rem;font-weight:900;color:#d4a843;margin:1rem 0;">{score}/{len(questions)} — {pct:.0f}%</div>
            <div style="font-size:0.8rem;color:#484f58;margin-top:1rem;">Date: {datetime.now().strftime('%B %d, %Y')}</div>
            <div style="font-size:0.8rem;color:#484f58;">Issued by: Adewale Samson Adeagbo | HMG Concepts | DataScience Flow Suite</div>
            <div style="font-size:0.7rem;color:#30363d;margin-top:0.5rem;">Verify at: dataflow.hmgconcepts.com</div>
        </div>
        """
        st.markdown(cert_html, unsafe_allow_html=True)

    # Review answers
    st.markdown("---")
    st.markdown("### 📋 Answer Review")
    for i, q in enumerate(questions):
        user_ans = st.session_state.quiz_answers.get(i)
        correct = user_ans == q['ans']
        icon = "✅" if correct else "❌"
        with st.expander(f"{icon} Q{i+1}: {q['q'][:80]}..."):
            st.markdown(f"**Your answer:** {q['opts'][user_ans] if user_ans is not None else 'Not answered'}")
            if not correct:
                st.markdown(f"**Correct answer:** {q['opts'][q['ans']]}")
            st.markdown(f"**Explanation:** {q['exp']}")

    if st.button("🔄 Retake Quiz"):
        st.session_state.quiz_started = False
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
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
