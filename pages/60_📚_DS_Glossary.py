"""
Module 60: DS Glossary — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
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


st.set_page_config(page_title="Glossary | DataFlow v9.0", page_icon="📚", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📚 DATA SCIENCE GLOSSARY — 80+ Terms Explained Simply</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** A searchable, categorized library of 80+ data science terms — every concept explained in plain English with examples. No jargon. No assumptions. Built by a teacher.

**🎯 Why you need it:** Data science has a vocabulary problem. Terms like "heteroscedasticity" and "eigendecomposition" scare beginners away. This glossary makes every concept accessible.

**📖 How to use it:** Search any term, browse by category, or read through like a textbook. Each definition includes a simple example.
""")

glossary_db = {
    "Fundamentals": [
        ("Dataset", "A collection of data organized in rows (records) and columns (features). Like an Excel spreadsheet. Example: A dataset of 150 flowers with columns for petal length, petal width, and species."),
        ("Row / Record / Observation", "One entry in a dataset. Each row is one thing you're studying. Example: Row 1 = Flower #1 with all its measurements."),
        ("Column / Feature / Variable", "One attribute measured for every row. Example: 'petal_length' is a column containing the petal length of every flower."),
        ("Target / Label / Dependent Variable", "The column you're trying to predict. Example: In Iris, 'species' is the target — you want to predict which species a flower belongs to."),
        ("Feature / Independent Variable / Predictor", "Columns used to make predictions. Example: Petal length and width are features used to predict the species."),
        ("Data Type (dtype)", "What kind of data is in a column: numeric (numbers), categorical (labels), boolean (true/false), datetime (dates). Knowing types is crucial for choosing the right analysis."),
        ("Missing Value (NaN / NULL)", "A cell with no data. Represented as NaN in Python. Can occur from errors, non-response, or data pipeline issues. Must be handled before ML."),
        ("Outlier", "An extreme value far from the rest. Example: If most houses cost $200K-$500K but one costs $50M, that's an outlier. Can distort means and mislead models."),
    ],
    "Statistics": [
        ("Mean (Average)", "Sum all values, divide by count. The 'center' of your data. Best for symmetric data without outliers. Example: Mean of [2,4,6,8,100] = 24 — pulled up by the outlier!"),
        ("Median", "The middle value when sorted. Better than mean when data has outliers. Example: Median of [2,4,6,8,100] = 6 — not affected by the outlier."),
        ("Mode", "The most frequent value. Works for both numbers and categories. Example: Mode of [A,A,B,C,A] = A."),
        ("Standard Deviation (Std)", "How spread out your data is. Small std = values cluster near the mean. Large std = values are scattered. Roughly 68% of data falls within ±1 std of the mean in a normal distribution."),
        ("Variance", "Standard deviation squared. Measures spread. Less intuitive than std but mathematically convenient."),
        ("IQR (Interquartile Range)", "Q3 minus Q1 — the range of the middle 50% of data. Robust to outliers. Used in box plots and outlier detection (IQR method)."),
        ("Percentile", "The value below which a given percentage falls. Example: The 90th percentile income means 90% of people earn less than that amount."),
        ("Skewness", "How asymmetric your distribution is. Positive skew = tail to the right (most values low, few very high — like income). Negative skew = tail to the left."),
        ("Kurtosis", "How 'peaked' or 'flat' your distribution is compared to normal. High kurtosis = more extreme outliers (heavy tails)."),
        ("Normal Distribution (Bell Curve)", "The most important distribution in statistics. Symmetric, bell-shaped. 68-95-99.7 rule: 68% within 1σ, 95% within 2σ, 99.7% within 3σ."),
        ("P-value", "The probability of seeing your result (or more extreme) if nothing is actually happening (null hypothesis is true). p < 0.05 is traditionally called 'significant'. Smaller p = stronger evidence of a real effect."),
        ("Confidence Interval (CI)", "A range likely to contain the true population value. A 95% CI means: if you repeated the study 100 times, 95 of the intervals would contain the true value."),
        ("Correlation (r)", "Strength and direction of a linear relationship between two variables. Ranges from -1 (perfect negative) to +1 (perfect positive). r=0 means no linear relationship. Correlation ≠ causation!"),
        ("Null Hypothesis (H₀)", "The 'nothing is happening' hypothesis. Example: 'There is no difference in petal length between setosa and versicolor.' We test against this."),
        ("Type I Error (False Positive)", "Rejecting the null hypothesis when it's actually true. 'Crying wolf.' Controlled by significance level α (usually 0.05)."),
        ("Type II Error (False Negative)", "Failing to reject the null hypothesis when it's actually false. 'Missing the signal.' Controlled by statistical power."),
    ],
    "Machine Learning": [
        ("Supervised Learning", "Training a model with labeled data (you know the answers). Example: You have flower measurements AND the species — model learns to predict species from measurements."),
        ("Unsupervised Learning", "Finding patterns in unlabeled data (you don't know the answers). Example: Grouping customers into segments without knowing the 'right' segments."),
        ("Classification", "Predicting a category. Example: Is this email spam or not? What species is this flower? Binary (2 classes) or multiclass (3+)."),
        ("Regression", "Predicting a number. Example: What will this house sell for? How many units will we sell next month?"),
        ("Training Set", "The data used to teach the model. Typically 70-80% of your data. The model 'sees' this data during learning."),
        ("Test Set", "The data used to evaluate the model. Typically 20-30% of your data. The model never sees this during training — it's the final exam."),
        ("Cross-Validation (K-fold CV)", "A technique to get a more reliable performance estimate. Split data into K folds, train on K-1, test on the remaining 1. Repeat K times. Prevents overfitting."),
        ("Overfitting", "The model memorizes training data (including noise) but fails on new data. Like a student who memorizes answers but doesn't understand the subject. Fix with cross-validation, simpler models, or more data."),
        ("Underfitting", "The model is too simple to capture patterns. Like trying to fit a straight line to a curve. Fix with more complex models or better features."),
        ("Accuracy", "Percent of correct predictions. Simple but misleading for imbalanced data. Example: If 95% of emails are not spam, a model that always says 'not spam' has 95% accuracy but is useless."),
        ("Precision", "Of all items predicted positive, how many are actually positive? Important when false positives are costly. High precision = few false alarms."),
        ("Recall (Sensitivity)", "Of all actual positives, how many did you find? Important when false negatives are costly. High recall = you catch most cases."),
        ("F1 Score", "Harmonic mean of precision and recall. Best single metric for imbalanced data. Ranges 0-1, higher is better."),
        ("ROC Curve", "Plots True Positive Rate vs False Positive Rate at different thresholds. AUC (Area Under Curve) summarizes it: 1.0 = perfect, 0.5 = random guessing."),
        ("Feature Engineering", "Creating new features or transforming existing ones to help the model learn better. Often more impactful than choosing a fancy algorithm."),
        ("Feature Scaling", "Putting all features on similar scales. Essential for distance-based models (KNN, SVM) and gradient descent. Methods: StandardScaler (z-score), MinMaxScaler (0-1)."),
    ],
    "Data Quality & Governance": [
        ("Data Quality", "How fit your data is for its intended use. Dimensions: completeness, uniqueness, timeliness, validity, accuracy, consistency."),
        ("GDPR", "General Data Protection Regulation — EU law on data protection and privacy. Applies to any organization handling EU residents' data."),
        ("NDPR", "Nigeria Data Protection Regulation — Nigerian implementation of data protection principles. Similar to GDPR. Enforced by NDPB."),
        ("PII", "Personally Identifiable Information — data that can identify a specific person: name, email, phone, address, ID numbers. Must be protected under GDPR/NDPR."),
        ("Data Masking / Anonymization", "Techniques to hide or replace sensitive data: hashing, pseudonymization, tokenization, noise addition. Allows analysis while protecting privacy."),
        ("Data Contract", "A formal agreement about what data should look like: required columns, expected types, value ranges, freshness SLAs. Validated automatically."),
        ("RPO (Recovery Point Objective)", "Maximum acceptable data loss measured in time. RPO of 24 hours means you can lose up to 24 hours of data in a disaster."),
        ("RTO (Recovery Time Objective)", "Maximum acceptable time to restore operations after a disaster. RTO of 4 hours means systems must be back within 4 hours."),
    ],
}

search = st.text_input("🔍 Search the glossary (80+ terms)", placeholder="Type any term...")

if search:
    st.markdown(f"### Results for '{search}':")
    found = False
    for category, terms in glossary_db.items():
        for term, definition in terms:
            if search.lower() in term.lower() or search.lower() in definition.lower():
                found = True
                with st.expander(f"**{term}** — {category}", expanded=True):
                    st.markdown(definition)
    if not found:
        st.info(f"No terms found for '{search}'. Try a different search or browse below.")

st.markdown("---")
for category, terms in glossary_db.items():
    with st.expander(f"### 📂 {category} ({len(terms)} terms)", expanded=False):
        for term, definition in terms:
            st.markdown(f"**{term}**")
            st.markdown(f"<span style='color:#8b949e;'>{definition}</span>", unsafe_allow_html=True)
            st.markdown("---")

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
