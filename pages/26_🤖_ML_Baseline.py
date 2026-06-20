"""
Module 26: ML Baseline — DataScience Flow v9.5
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



st.set_page_config(page_title="ML Baseline | DataScience Flow", page_icon="🤖", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🤖 ML BASELINE</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Train 7 ML algorithms: Logistic Regression, Decision Tree, Random Forest, SVM, KNN, Gradient Boosting, Naive Bayes. K-fold cross-validation. Confusion matrix. ROC & PR curves. Learning curves. Classification threshold tuner. Pickle model download.

**🎯 Why you need it:** Quickly benchmark multiple algorithms to find what works best for your data. No code needed — select target, features, and click train.

**📖 How to use it:** Select target column → select feature columns → choose algorithms → train → compare results → download best model.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]
st.session_state.get("steps_done", set()).add("model")

st.markdown("### 🤖 Machine Learning Baseline Trainer")

num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
all_cols = dfc.columns.tolist()
if not num_cols:
    st.warning("Need numeric columns.")
    st.stop()

target = st.selectbox("Target column", all_cols)
feature_cols = st.multiselect("Feature columns", [c for c in all_cols if c != target], 
    default=[c for c in num_cols if c != target][:min(5, len(num_cols)-1)])

if feature_cols and target:
    algos = st.multiselect("Algorithms to train", 
        ["Logistic Regression", "Decision Tree", "Random Forest", "SVM", "KNN", "Gradient Boosting", "Naive Bayes"],
        default=["Random Forest", "Logistic Regression"])
    test_size = st.slider("Test set %", 10, 40, 20)
    cv_folds = st.slider("K-fold CV", 2, 10, 5)
    
    if st.button("🚀 Train Models"):
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
        
        X = dfc[feature_cols].copy()
        for c in X.select_dtypes(include=["object","string"]).columns:
            X[c] = LabelEncoder().fit_transform(X[c].astype(str))
        X = X.fillna(0)
        y = dfc[target]
        if y.dtype == object:
            y = LabelEncoder().fit_transform(y.astype(str))
        X = StandardScaler().fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size/100, random_state=42)
        
        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Decision Tree": DecisionTreeClassifier(max_depth=10),
            "Random Forest": RandomForestClassifier(n_estimators=100),
            "SVM": SVC(probability=True),
            "KNN": KNeighborsClassifier(n_neighbors=5),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=100),
            "Naive Bayes": GaussianNB(),
        }
        
        results = []
        for name in algos:
            if name in models:
                model = models[name]
                try:
                    cv_scores = cross_val_score(model, X_train, y_train, cv=min(cv_folds, len(set(y_train))), scoring='accuracy')
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    acc = accuracy_score(y_test, y_pred)
                    results.append({"Algorithm": name, "CV Mean Accuracy": cv_scores.mean(), 
                        "CV Std": cv_scores.std(), "Test Accuracy": acc})
                except Exception as e:
                    results.append({"Algorithm": name, "CV Mean Accuracy": 0, "CV Std": 0, "Test Accuracy": 0, "Error": str(e)})
        
        if results:
            res_df = pd.DataFrame(results).sort_values("Test Accuracy", ascending=False)
            st.markdown("### 🏆 Results")
            st.dataframe(res_df.style.background_gradient(subset=["Test Accuracy", "CV Mean Accuracy"], cmap="RdYlGn"), use_container_width=True)
            
            best = res_df.iloc[0]
            st.success(f"🏆 Best: **{best['Algorithm']}** — Test Accuracy: {best['Test Accuracy']:.4f}")
            
            # Confusion Matrix for best
            best_model = models.get(best['Algorithm'])
            if best_model:
                try:
                    best_model.fit(X_train, y_train)
                    y_pred = best_model.predict(X_test)
                    cm = confusion_matrix(y_test, y_pred)
                    fig = go.Figure(data=go.Heatmap(z=cm, text=cm, texttemplate="%{text}",
                        colorscale="teal", x=[f"Pred {i}" for i in range(cm.shape[0])], 
                        y=[f"True {i}" for i in range(cm.shape[0])]))
                    fig.update_layout(title=f"Confusion Matrix — {best['Algorithm']}", 
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    import io, pickle
                    buf = io.BytesIO()
                    pickle.dump(best_model, buf)
                    st.download_button("⬇️ Download Best Model (.pkl)", buf.getvalue(), 
                        f"model_{best['Algorithm'].lower().replace(' ','_')}.pkl", "application/octet-stream")
                except Exception as e:
                    st.error(f"CM error: {e}")

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
