"""
Module 29: Model Explainability — DataScience Flow v9.5
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


st.set_page_config(page_title="Model Explainability | DataScience Flow", page_icon="🔍", layout="wide")


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
## 🔍 Model Explainability — Module 29

> **What is Model Explainability?** Explainability (or interpretability) is the ability to understand and 
> explain WHY a model makes certain predictions. A model that predicts well but cannot be explained is a 
> "black box" — dangerous in healthcare, finance, and any domain where decisions affect people.

### 🎓 Why Explainability Matters
- **Trust**: Stakeholders trust models they can understand
- **Debugging**: Understanding features helps fix model errors
- **Fairness**: Detecting if a model relies on biased features
- **Compliance**: GDPR "right to explanation" requires interpretable models
- **Domain Knowledge**: Models should align with what domain experts know

### 📐 Explainability Methods (No AI API Required!)
| Method | How It Works | What It Shows |
|--------|-------------|---------------|
| Permutation Importance | Shuffle each feature, measure performance drop | Which features matter most |
| Partial Dependence Plot | Average predictions across feature values | How a feature affects predictions |
| Feature Interactions | How predictions change with two features together | How features work together |
| ICE Plots | Individual prediction paths | Per-sample feature effects |
| Global Feature Importance | Model-specific importance (e.g., tree-based) | Built-in feature ranking |

### 🇳🇬 Nigerian Context
In Nigeria, model explainability is critical for:
- **CBT systems**: Why was a student flagged?
- **Loan applications**: Why was a customer rejected?
- **Healthcare**: Why did the model recommend this treatment?
- **Insurance**: Why was a claim classified as fraudulent?
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

tab_perm, tab_pdp, tab_feature_imp, tab_ice = st.tabs([
    "📊 Permutation Importance", "📈 Partial Dependence", "🌲 Feature Importance", "🧊 ICE Plots"
])

with tab_perm:
    st.markdown("### 📊 Permutation Importance")
    st.info("""**How it works:** For each feature, randomly shuffle its values and measure how much the 
    model's performance drops. A large drop means the feature is important. No drop means the feature 
    is not useful.
    
    **Advantage:** Model-agnostic — works with any model type. No AI API needed.""")
    
    target_col = st.selectbox("Target variable", df.columns.tolist(), key="perm_target")
    feature_cols = st.multiselect("Feature columns",
                                   [c for c in df.columns if c != target_col],
                                   default=[c for c in df.columns if c != target_col][:5],
                                   key="perm_features")
    
    if st.button("🔍 Compute Permutation Importance", key="perm_btn"):
        if feature_cols:
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            from sklearn.inspection import permutation_importance
            from sklearn.preprocessing import LabelEncoder
            from sklearn.impute import SimpleImputer
            
            X = df[feature_cols].copy()
            y = df[target_col].copy()
            
            cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
            if cat_cols:
                X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
            
            imputer = SimpleImputer(strategy='mean')
            X_imp = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
            
            is_classification = y.dtype == 'object' or y.nunique() <= 20
            if is_classification:
                le = LabelEncoder()
                y_enc = le.fit_transform(y.astype(str))
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                y_enc = y.values
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            X_train, X_test, y_train, y_test = train_test_split(X_imp, y_enc, test_size=0.2, random_state=42)
            model.fit(X_train, y_train)
            
            result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
            
            importance_df = pd.DataFrame({
                "Feature": X_imp.columns,
                "Importance Mean": result.importances_mean,
                "Importance Std": result.importances_std,
            }).sort_values("Importance Mean", ascending=False)
            
            st.dataframe(importance_df.round(4), use_container_width=True)
            
            import plotly.express as px
            fig = px.bar(importance_df.head(15), x="Importance Mean", y="Feature",
                        error_x="Importance Std", orientation='h',
                        title="Permutation Feature Importance (Top 15)")
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

with tab_pdp:
    st.markdown("### 📈 Partial Dependence Plots")
    st.info("""**What is a PDP?** A Partial Dependence Plot shows the average predicted outcome as a function 
    of one (or two) feature values, marginalizing over the other features. It answers: "On average, how does 
    changing this feature affect the prediction?"
    
    **Limitation:** PDPs show average effects and may hide heterogeneous effects. Use ICE plots for per-sample analysis.""")
    
    target_col = st.selectbox("Target variable", df.columns.tolist(), key="pdp_target")
    feature_cols = st.multiselect("Feature columns",
                                   [c for c in df.columns if c != target_col],
                                   default=[c for c in df.columns if c != target_col][:5],
                                   key="pdp_features")
    
    if feature_cols:
        numeric_features = df[feature_cols].select_dtypes(include=np.number).columns.tolist()
        if numeric_features:
            pdp_feature = st.selectbox("Feature to plot PDP for", numeric_features, key="pdp_feat")
            
            if st.button("📈 Generate PDP", key="pdp_btn"):
                from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
                from sklearn.impute import SimpleImputer
                from sklearn.model_selection import train_test_split
                
                X = df[feature_cols].copy()
                y = df[target_col].copy()
                
                cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
                if cat_cols:
                    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
                
                imputer = SimpleImputer(strategy='mean')
                X_imp = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
                
                is_classification = y.dtype == 'object' or y.nunique() <= 20
                if is_classification:
                    le = LabelEncoder()
                    y_enc = le.fit_transform(y.astype(str))
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    y_enc = y.values
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                model.fit(X_imp, y_enc)
                
                # Manual PDP computation
                feat_idx = list(X_imp.columns).index(pdp_feature)
                feat_values = X_imp[pdp_feature]
                grid = np.linspace(feat_values.min(), feat_values.max(), 50)
                
                preds = []
                X_temp = X_imp.copy()
                for val in grid:
                    X_temp[pdp_feature] = val
                    pred = model.predict(X_temp).mean()
                    preds.append(pred)
                
                import plotly.express as px
                fig = px.line(x=grid, y=preds,
                             labels={'x': pdp_feature, 'y': 'Average Prediction'},
                             title=f'Partial Dependence Plot: {pdp_feature}')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need at least one numeric feature for PDP.")

with tab_feature_imp:
    st.markdown("### 🌲 Built-in Feature Importance (Tree Models)")
    st.info("Tree-based models (Random Forest, Gradient Boosting) provide built-in feature importance based on how much each feature reduces impurity.")
    
    target_col = st.selectbox("Target variable", df.columns.tolist(), key="fi_target")
    feature_cols = st.multiselect("Feature columns",
                                   [c for c in df.columns if c != target_col],
                                   default=[c for c in df.columns if c != target_col][:5],
                                   key="fi_features")
    
    if st.button("🌲 Compute Feature Importance", key="fi_btn") and feature_cols:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.preprocessing import LabelEncoder
        
        X = df[feature_cols].copy()
        y = df[target_col].copy()
        
        cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
        
        imputer = SimpleImputer(strategy='mean')
        X_imp = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
        
        is_classification = y.dtype == 'object' or y.nunique() <= 20
        if is_classification:
            le = LabelEncoder()
            y_enc = le.fit_transform(y.astype(str))
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            y_enc = y.values
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X_imp, y_enc)
        
        importance_df = pd.DataFrame({
            "Feature": X_imp.columns,
            "Importance": model.feature_importances_
        }).sort_values("Importance", ascending=False)
        
        st.dataframe(importance_df.round(4), use_container_width=True)
        
        import plotly.express as px
        fig = px.bar(importance_df.head(15), x="Importance", y="Feature", orientation='h',
                    title="Feature Importance (Random Forest)")
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

with tab_ice:
    st.markdown("### 🧊 Individual Conditional Expectation (ICE) Plots")
    st.info("""**What is an ICE Plot?** Unlike PDPs which show the average effect, ICE plots show the 
    prediction curve for each individual sample. This reveals if the feature effect is consistent across 
    all samples, or if there are subgroups with different patterns.
    
    **How to read:** Each line represents one sample. The x-axis is the feature value, and the y-axis is 
    the predicted outcome. If all lines move in the same direction, the effect is consistent. If lines cross 
    or diverge, different samples respond differently.""")
    
    st.info("This feature trains a model on your data and generates ICE curves. Select your configuration below.")
    
    target_col = st.selectbox("Target variable", df.columns.tolist(), key="ice_target")
    feature_cols = st.multiselect("Feature columns",
                                   [c for c in df.columns if c != target_col],
                                   default=[c for c in df.columns if c != target_col][:5],
                                   key="ice_features")
    
    if feature_cols:
        numeric_features = df[feature_cols].select_dtypes(include=np.number).columns.tolist()
        if numeric_features:
            ice_feature = st.selectbox("Feature for ICE", numeric_features, key="ice_feat")
            n_samples = st.slider("Number of ICE samples", 10, 200, 50)
            
            if st.button("🧊 Generate ICE Plot", key="ice_btn"):
                from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
                from sklearn.impute import SimpleImputer
                
                X = df[feature_cols].copy()
                y = df[target_col].copy()
                
                cat_cols = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
                if cat_cols:
                    X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
                
                imputer = SimpleImputer(strategy='mean')
                X_imp = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
                
                is_classification = y.dtype == 'object' or y.nunique() <= 20
                if is_classification:
                    le = LabelEncoder()
                    y_enc = le.fit_transform(y.astype(str))
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    y_enc = y.values
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                
                model.fit(X_imp, y_enc)
                
                # ICE computation
                sample_idx = np.random.choice(len(X_imp), min(n_samples, len(X_imp)), replace=False)
                X_sample = X_imp.iloc[sample_idx].copy()
                
                feat_values = X_imp[ice_feature]
                grid = np.linspace(feat_values.min(), feat_values.max(), 30)
                
                ice_lines = []
                for i, (idx, row) in enumerate(X_sample.iterrows()):
                    X_temp = pd.DataFrame([row] * len(grid), columns=X_imp.columns)
                    X_temp[ice_feature] = grid
                    preds = model.predict(X_temp)
                    for j, val in enumerate(grid):
                        ice_lines.append({"Feature Value": val, "Prediction": preds[j], "Sample": i})
                
                ice_df = pd.DataFrame(ice_lines)
                import plotly.express as px
                fig = px.line(ice_df, x="Feature Value", y="Prediction", color="Sample",
                             title=f"ICE Plot: {ice_feature}",
                             color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Model explainability is not optional — it is essential for building trustworthy AI. 
Use Permutation Importance for a quick overview, PDPs for average effects, and ICE plots for individual-level insights.

📚 **Next Steps:** After understanding your model, use Module 29 (Deployment Guide) to deploy it responsibly.
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
