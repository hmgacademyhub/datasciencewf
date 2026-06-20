"""
Module 28: Model Comparison — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription

from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)


st.set_page_config(page_title="Model Comparison | DataScience Flow", page_icon="🏆", layout="wide")


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
## 🏆 Model Comparison — Module 28

> **Why Compare Models?** No single algorithm is best for every dataset. Different models have different 
> biases, and the only way to know which works best for YOUR data is to compare them systematically.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| Baseline | Simplest model (e.g., logistic regression) | Reference point for improvement |
| Cross-validation | Multiple train/test splits | Reduces variance of performance estimates |
| Overfitting | Model memorizes training data | Fails on new data |
| Bias-Variance Tradeoff | Simple vs complex models | Balance underfitting and overfitting |
| Metric Selection | Accuracy, F1, AUC, etc. | Different metrics for different goals |

### 📐 Choosing the Right Metric
| Problem Type | Recommended Metric | When to Use |
|-------------|-------------------|-------------|
| Balanced Classification | Accuracy | Equal class sizes |
| Imbalanced Classification | F1-Score, AUC-ROC | Unequal class sizes |
| Regression | RMSE, R² | Continuous target |
| Ranking | NDCG, MAP | Ordered predictions |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

tab_setup, tab_results, tab_ranking = st.tabs(["⚙️ Setup & Train", "📊 Results", "🏆 Ranking"])

with tab_setup:
    target_col = st.selectbox("Target variable", df.columns.tolist())
    task_type = st.selectbox("Task type", ["Classification", "Regression"])
    
    feature_cols = st.multiselect("Feature columns", 
                                   [c for c in df.columns if c != target_col],
                                   default=[c for c in df.columns if c != target_col][:5])
    
    if task_type == "Classification":
        models_to_train = st.multiselect("Models to compare", [
            "Logistic Regression", "Decision Tree", "Random Forest",
            "K-Nearest Neighbors", "Gradient Boosting", "SVM (Linear)",
            "Naive Bayes"
        ], default=["Logistic Regression", "Decision Tree", "Random Forest", "K-Nearest Neighbors"])
    else:
        models_to_train = st.multiselect("Models to compare", [
            "Linear Regression", "Ridge Regression", "Lasso Regression",
            "Decision Tree Regressor", "Random Forest Regressor",
            "Gradient Boosting Regressor", "KNN Regressor"
        ], default=["Linear Regression", "Decision Tree Regressor", "Random Forest Regressor"])
    
    cv_folds = st.slider("Cross-validation folds", 2, 10, 5)
    test_size = st.slider("Test set size (%)", 10, 40, 20)
    
    if st.button("🚀 Run Comparison") and feature_cols and models_to_train:
        from sklearn.model_selection import cross_validate, train_test_split
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        
        # Prepare data
        X = df[feature_cols].copy()
        y = df[target_col].copy()
        
        # Handle categorical features
        cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
        
        # Handle missing values
        imputer = SimpleImputer(strategy='mean')
        X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
        
        # Encode target for classification
        if task_type == "Classification":
            le = LabelEncoder()
            y_encoded = le.fit_transform(y.astype(str))
        else:
            y_encoded = y.values
        
        # Model definitions
        model_defs = {}
        if task_type == "Classification":
            from sklearn.linear_model import LogisticRegression
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.svm import LinearSVC
            from sklearn.naive_bayes import GaussianNB
            
            model_defs = {
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
                "Decision Tree": DecisionTreeClassifier(random_state=42),
                "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "K-Nearest Neighbors": KNeighborsClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
                "SVM (Linear)": LinearSVC(max_iter=2000, random_state=42),
                "Naive Bayes": GaussianNB(),
            }
        else:
            from sklearn.linear_model import LinearRegression, Ridge, Lasso
            from sklearn.tree import DecisionTreeRegressor
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.neighbors import KNeighborsRegressor
            
            model_defs = {
                "Linear Regression": LinearRegression(),
                "Ridge Regression": Ridge(random_state=42),
                "Lasso Regression": Lasso(random_state=42),
                "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
                "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
                "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, random_state=42),
                "KNN Regressor": KNeighborsRegressor(),
            }
        
        # Scoring
        if task_type == "Classification":
            scoring = ['accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted', 'roc_auc_ovr_weighted']
        else:
            scoring = ['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error']
        
        progress = st.progress(0)
        results = []
        
        for idx, name in enumerate(models_to_train):
            if name in model_defs:
                model = model_defs[name]
                try:
                    pipe = Pipeline([
                        ('scaler', StandardScaler()),
                        ('model', model)
                    ])
                    cv_results = cross_validate(pipe, X_imputed, y_encoded, cv=cv_folds, scoring=scoring)
                    
                    result = {"Model": name}
                    for metric in scoring:
                        scores = cv_results[f'test_{metric}']
                        result[metric] = scores.mean()
                        result[f"{metric}_std"] = scores.std()
                    result['fit_time'] = cv_results['fit_time'].mean()
                    results.append(result)
                except Exception as e:
                    results.append({"Model": name, "Error": str(e)})
            
            progress.progress((idx + 1) / len(models_to_train))
        
        st.session_state["model_comparison_results"] = results
        st.success("✅ Comparison complete! View results in the Results tab.")

with tab_results:
    results = st.session_state.get("model_comparison_results", [])
    if results:
        results_df = pd.DataFrame(results)
        if "Error" not in results_df.columns or results_df["Error"].isna().all():
            # Format display
            display_cols = [c for c in results_df.columns if not c.endswith("_std") and c != "Error"]
            st.dataframe(results_df[display_cols].round(4), use_container_width=True)
        else:
            st.dataframe(results_df, use_container_width=True)
    else:
        st.info("Run a comparison first in the Setup tab.")

with tab_ranking:
    results = st.session_state.get("model_comparison_results", [])
    if results:
        results_df = pd.DataFrame(results)
        metric_cols = [c for c in results_df.columns if not c.endswith("_std") and c not in ["Model", "Error", "fit_time"]]
        
        if metric_cols:
            primary_metric = st.selectbox("Primary ranking metric", metric_cols)
            ascending = primary_metric.startswith("neg_") if task_type == "Regression" else False
            
            ranked = results_df.sort_values(primary_metric, ascending=ascending).reset_index(drop=True)
            ranked.index += 1
            ranked.insert(0, "Rank", ranked.index)
            
            st.markdown("### 🏆 Model Rankings")
            st.dataframe(ranked, use_container_width=True)
            
            best = ranked.iloc[0]["Model"]
            st.success(f"**🏆 Best Model by {primary_metric}: {best}**")
            
            st.info(f"""**Recommendation:** Based on {primary_metric}, the **{best}** model performs best.
            
**Before deploying, consider:**
1. Is the performance difference practically significant?
2. Is the best model interpretable enough for your stakeholders?
3. Does the best model have acceptable training/inference time?
4. Would an ensemble of the top models perform even better?
""")
    else:
        st.info("Run a comparison first in the Setup tab.")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Always compare multiple models — never rely on a single algorithm. 
Use cross-validation to get reliable performance estimates. Choose the model that balances 
performance, interpretability, and computational cost for your specific use case.

📚 **Next Steps:** After identifying the best model, use Module 28 (Model Explainability) to understand its predictions.
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
