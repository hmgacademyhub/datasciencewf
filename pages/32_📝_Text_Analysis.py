"""
Module 32: Text Analysis — DataScience Flow v9.5
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



st.set_page_config(page_title="Text Analysis | DataScience Flow", page_icon="📝", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📝 TEXT ANALYSIS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Word frequency analysis with stop-word filtering. N-grams (bigrams, trigrams, 4-grams). TF-IDF scoring. Rule-based sentiment (positive/negative word counts). Readability scores (Flesch-Kincaid). **100% rule-based — no AI API!**

**🎯 Why you need it:** Understand text data without expensive AI APIs. Extract keywords, sentiment, and readability — all locally computed.

**📖 How to use it:** Select text column → configure analysis → view word frequencies → TF-IDF → sentiment → readability.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📝 Text Analysis (100% Rule-Based)")
cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()
if not cat_cols:
    st.warning("No text/categorical columns.")
    st.stop()

text_col = st.selectbox("Text column to analyze", cat_cols)
text_data = dfc[text_col].dropna().astype(str)

tab1,tab2,tab3 = st.tabs(["📊 Word Frequency", "📈 TF-IDF Scoring", "😊 Sentiment & Readability"])

with tab1:
    ngram = st.selectbox("N-gram type", ["Words", "Bigrams", "Trigrams"])
    top_n = st.slider("Show top", 10, 50, 20)
    stop_words = set(["the","a","an","is","are","was","were","be","been","being","have","has","had","do","does","did","but","and","or","if","of","to","in","on","at","for","with","from","by","as","not","no","so","it","its","that","this","these","those"])
    
    if st.button("📊 Generate Word Frequencies"):
        from collections import Counter
        if ngram == "Words":
            all_words = []
            for text in text_data:
                words = [w.lower().strip(".,!?;:'"()[]{}") for w in text.split() if w.lower().strip(".,!?;:'"()[]{}") not in stop_words and len(w) > 1]
                all_words.extend(words)
            counter = Counter(all_words)
        elif ngram == "Bigrams":
            all_ngrams = []
            for text in text_data:
                words = [w.lower().strip(".,!?;:'"()[]{}") for w in text.split() if w.lower().strip(".,!?;:'"()[]{}") not in stop_words and len(w) > 1]
                all_ngrams.extend([" ".join(words[i:i+2]) for i in range(len(words)-1)])
            counter = Counter(all_ngrams)
        else:
            all_ngrams = []
            for text in text_data:
                words = [w.lower().strip(".,!?;:'"()[]{}") for w in text.split() if w.lower().strip(".,!?;:'"()[]{}") not in stop_words and len(w) > 1]
                all_ngrams.extend([" ".join(words[i:i+3]) for i in range(len(words)-2)])
            counter = Counter(all_ngrams)
        
        freq_df = pd.DataFrame(counter.most_common(top_n), columns=["Term", "Count"])
        fig = px.bar(freq_df, x="Term", y="Count", template="plotly_dark", color_discrete_sequence=["#00d9a7"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(freq_df, use_container_width=True)

with tab2:
    st.markdown("#### TF-IDF Scoring")
    st.caption("Measures how important each word is — higher = more distinctive.")
    if st.button("📈 Compute TF-IDF"):
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf = TfidfVectorizer(max_features=20, stop_words="english")
        try:
            tfidf_matrix = tfidf.fit_transform(text_data)
            tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
            st.markdown("**Top 20 TF-IDF terms (first 10 documents):**")
            st.dataframe(tfidf_df.head(10).round(3), use_container_width=True)
            means = tfidf_df.mean().sort_values(ascending=False)
            fig = px.bar(x=means.index, y=means.values, template="plotly_dark", color_discrete_sequence=["#4f8ef7"])
            fig.update_layout(title="Average TF-IDF Score by Term", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"TF-IDF error: {e}")

with tab3:
    st.markdown("#### 😊 Rule-Based Sentiment")
    st.caption("Counts positive vs negative words. 100% rule-based — no AI API!")
    
    positive_words = {"good","great","excellent","amazing","wonderful","fantastic","happy","love","best","beautiful","perfect","nice","awesome","outstanding","brilliant","superb","positive","success","win","winning","joy","blessed","thankful","grateful","pleasant","delightful"}
    negative_words = {"bad","terrible","awful","horrible","worst","poor","sad","hate","ugly","negative","fail","failure","lose","losing","angry","upset","disappointing","disgusting","nasty","wrong","broken","waste","useless","worthless","painful"}
    
    if st.button("😊 Analyze Sentiment"):
        sentiment_results = []
        for text in text_data.head(100):
            words = set(text.lower().split())
            pos = len(words & positive_words)
            neg = len(words & negative_words)
            score = pos - neg
            if score > 0: label = "😊 Positive"
            elif score < 0: label = "😟 Negative"
            else: label = "😐 Neutral"
            sentiment_results.append({"Text": text[:100], "Pos Words": pos, "Neg Words": neg, "Score": score, "Sentiment": label})
        
        sent_df = pd.DataFrame(sentiment_results)
        st.dataframe(sent_df, use_container_width=True)
        dist = sent_df["Sentiment"].value_counts()
        fig = px.pie(values=dist.values, names=dist.index, template="plotly_dark", title="Sentiment Distribution")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### 📖 Readability")
    st.caption("Flesch-Kincaid readability estimate.")
    if st.button("📖 Calculate Readability"):
        scores = []
        for text in text_data.head(50):
            sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
            words = max(1, len(text.split()))
            syllables = sum(text.lower().count(v) for v in "aeiou") + 1
            try:
                fk = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
                if fk > 90: level = "Very Easy (5th grade)"
                elif fk > 80: level = "Easy (6th grade)"
                elif fk > 70: level = "Fairly Easy (7th grade)"
                elif fk > 60: level = "Standard (8th-9th grade)"
                elif fk > 50: level = "Fairly Difficult (10th-12th grade)"
                elif fk > 30: level = "Difficult (College)"
                else: level = "Very Difficult (College Graduate)"
                scores.append({"Text": text[:60] + "...", "Flesch-Kincaid": round(fk, 1), "Level": level})
            except:
                pass
        if scores:
            st.dataframe(pd.DataFrame(scores), use_container_width=True)
            avg_fk = sum(s["Flesch-Kincaid"] for s in scores) / len(scores)
            st.metric("Average Readability", f"{avg_fk:.1f}")

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
