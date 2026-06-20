"""
Module 58: Interactive Tutorials — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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


st.set_page_config(page_title="Tutorials | DataFlow v9.0", page_icon="🎓", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🎓 INTERACTIVE TUTORIALS — Learn by Doing</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** 12 hands-on, step-by-step tutorials that teach core data science concepts using real datasets. Each tutorial is a complete mini-lesson — no prior experience needed.

**🎯 Why you need it:** The best way to learn data science is by doing. These tutorials walk you through every click, explain every result, and build your confidence one concept at a time.

**📖 How to use it:** Pick a tutorial → follow the steps → see results instantly → apply what you learned to your own data.
""")

# Tutorial database
tutorials_db = {
    "T1: Your First Data Analysis (Beginner)": {
        "level": "🟢 Beginner",
        "time": "15 min",
        "concept": "Load → Explore → Visualize → Understand",
        "steps": [
            "📥 **Step 1:** Load the Iris dataset from the sidebar (📦 Sample Dataset → 🌸 Iris)",
            "🔍 **Step 2:** Go to Module 1 (Data Exploration). Look at the first 5 rows (HEAD). Notice the column names: sepal length, sepal width, petal length, petal width, species.",
            "📊 **Step 3:** Check the Column Info tab. How many rows? How many columns? Any missing values?",
            "📈 **Step 4:** In Module 5 (EDA), create a scatter plot of petal_length vs petal_width, colored by species. Notice how the species separate?",
            "🎯 **Insight:** The three iris species form distinct clusters based on petal measurements. This is why Iris is the classic ML classification dataset!",
        ],
        "quiz": "What separates the three iris species most clearly?",
        "quiz_options": ["Sepal measurements", "Petal measurements", "The color of the flower", "The country of origin"],
        "quiz_answer": 1,
    },
    "T2: Understanding Missing Data (Beginner)": {
        "level": "🟢 Beginner",
        "time": "12 min",
        "concept": "Find, understand, and handle missing values",
        "steps": [
            "📥 **Step 1:** Load the California Housing dataset (📦 Sample Dataset → 🏠 California Housing)",
            "🕳️ **Step 2:** In Module 2 (Missing Values), check the Missing Overview tab. See any missing data?",
            "📊 **Step 3:** California Housing has no missing values! Let's create some: Go to Module 18 (Data Simulation) → Add Noise → add Gaussian noise at 10%.",
            "🔧 **Step 4:** Now go back to Module 2. Try different imputation strategies: mean, median, forward-fill. Compare before/after.",
            "🎯 **Insight:** There's no single 'right' way to handle missing data. Mean works for normal distributions, median for skewed data, forward-fill for time series.",
        ],
        "quiz": "Which imputation method is best for skewed data with outliers?",
        "quiz_options": ["Mean", "Median", "Mode", "Always drop missing rows"],
        "quiz_answer": 1,
    },
    "T3: Finding Stories with Charts (Beginner)": {
        "level": "🟢 Beginner",
        "time": "18 min",
        "concept": "Choose the right chart for your question",
        "steps": [
            "📥 **Step 1:** Load the Iris dataset",
            "📊 **Step 2:** In Module 5, create a Histogram of sepal_length. Is it normally distributed? (Look for a bell shape)",
            "📦 **Step 3:** Create a Box Plot of petal_width grouped by species. See the differences? Setosa has much narrower petals.",
            "🔥 **Step 4:** Create a Correlation Heatmap of all numeric columns. Which two features are most correlated?",
            "🥧 **Step 5:** Create a Pie Chart of species. Are the classes balanced? (Yes — 50 each!)",
            "🎯 **Insight:** Different chart types answer different questions. Histograms show distribution, box plots compare groups, heatmaps show relationships.",
        ],
        "quiz": "Which chart type is best for comparing a numeric variable across categories?",
        "quiz_options": ["Pie Chart", "Box Plot", "Line Chart", "Scatter Plot"],
        "quiz_answer": 1,
    },
    "T4: Hypothesis Testing Made Simple (Intermediate)": {
        "level": "🟡 Intermediate",
        "time": "20 min",
        "concept": "Use statistics to make data-driven decisions",
        "steps": [
            "📥 **Step 1:** Load the Iris dataset",
            "📐 **Step 2:** Go to Module 11 (Hypothesis Testing). Select 'Independent T-test'.",
            "🔢 **Step 3:** Choose petal_length as numeric column, species as group. Compare 'setosa' vs 'versicolor'.",
            "📊 **Step 4:** Run the test. Look at the p-value. Is it less than 0.05? (Spoiler: p ≈ 0.0000 — highly significant!)",
            "🎯 **Insight:** A tiny p-value means the difference in petal length between setosa and versicolor is almost certainly real, not random chance.",
        ],
        "quiz": "A p-value of 0.03 means:",
        "quiz_options": ["The result is 97% true", "There's a 3% chance of seeing this result if nothing is really happening", "The data is 3% wrong", "The model is 97% accurate"],
        "quiz_answer": 1,
    },
    "T5: Your First Machine Learning Model (Intermediate)": {
        "level": "🟡 Intermediate",
        "time": "25 min",
        "concept": "Train, evaluate, and understand ML models",
        "steps": [
            "📥 **Step 1:** Load the Iris dataset",
            "🤖 **Step 2:** Go to Module 13 (ML Baseline). Select 'species' as target. Select all numeric columns as features.",
            "🧪 **Step 3:** Choose 'Random Forest' and 'Logistic Regression'. Set test size to 20%, K-fold CV to 5.",
            "🚀 **Step 4:** Click 'Train Models'. Compare the results. Which algorithm performed better?",
            "📊 **Step 5:** Look at the confusion matrix. Where did the model make mistakes? Which species was hardest to classify?",
            "🎯 **Insight:** Even with simple models, you can get >95% accuracy on Iris. The real learning is understanding WHY a model works (or doesn't).",
        ],
        "quiz": "What does K-fold cross-validation protect against?",
        "quiz_options": ["Missing data", "Overfitting", "Slow training", "Too many features"],
        "quiz_answer": 1,
    },
    "T6: PII Detection & Privacy (Intermediate)": {
        "level": "🟡 Intermediate",
        "time": "15 min",
        "concept": "Protect sensitive information in datasets",
        "steps": [
            "🔐 **Step 1:** Go to Module 26 (Data Privacy & Masking) — this one works without data loaded",
            "🔍 **Step 2:** Read about the 8 masking methods: SHA-256, pseudonymization, tokenization, Gaussian noise...",
            "📋 **Step 3:** If you have a dataset with emails or names, load it and run the PII scan",
            "🔒 **Step 4:** Try different masking methods and see the results",
            "🎯 **Insight:** Data privacy isn't optional — it's a legal requirement under GDPR and NDPR. Always mask PII before sharing!",
        ],
        "quiz": "Which Nigerian regulation governs data protection?",
        "quiz_options": ["GDPR", "NDPR", "CCPA", "None — Nigeria has no data laws"],
        "quiz_answer": 1,
    },
}

# Display tutorials
tutorial_choice = st.selectbox("Choose a tutorial", list(tutorials_db.keys()))
tut = tutorials_db[tutorial_choice]

col1, col2, col3 = st.columns(3)
col1.metric("Level", tut['level'])
col2.metric("Time", tut['time'])
col3.metric("Concept", tut['concept'])

st.markdown("---")
st.markdown("### 📖 Step-by-Step Instructions")
for step in tut['steps']:
    st.markdown(step)
    st.markdown("---")

st.markdown("### 📝 Knowledge Check")
quiz = st.radio(tut['quiz'], tut['quiz_options'], key="tut_quiz")
if st.button("✅ Check Answer"):
    if tut['quiz_options'].index(quiz) == tut['quiz_answer']:
        st.success("✅ Correct! You're learning fast. 🎉")
        st.balloons()
    else:
        st.error(f"❌ Not quite. The correct answer is: **{tut['quiz_options'][tut['quiz_answer']]}**")
        st.info("💡 No worries — this is how we learn. Review the steps above and try again!")

st.markdown("---")
st.markdown("### 🎯 What's Next?")
st.markdown("- Try this tutorial with **your own dataset** — the steps work the same way!")
st.markdown("- Explore the **Data Science Roadmap** (Module 41) for a complete learning path")
st.markdown("- Check the **Learning Hub** (Module 22) for 50+ glossary terms")
st.markdown("- Take the **Data Science Quiz** (Module 22) to test your knowledge")

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
