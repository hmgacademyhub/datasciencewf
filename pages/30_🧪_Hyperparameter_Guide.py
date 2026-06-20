"""
Module 30: Hyperparameter Guide — DataScience Flow v9.5
GridSearch, RandomSearch, best practices, interactive learning
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Hyperparameter Guide | DataScience Flow", page_icon="🧪", layout="wide")

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

st.markdown("""
## 🧪 Hyperparameter Guide — Module 30

> **What are Hyperparameters?** Hyperparameters are configuration settings of a machine learning algorithm 
> that are set BEFORE training begins — they control how the model learns. Unlike model parameters (like weights 
> and biases), hyperparameters cannot be learned from the data directly.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| Hyperparameter | Setting chosen before training | Controls learning behaviour |
| Grid Search | Try all combinations | Exhaustive but slow |
| Random Search | Try random combinations | Often finds good params faster |
| Cross-Validation | Evaluate each config on multiple splits | Prevents overfitting to validation set |
| Bias-Variance Tradeoff | Simple vs complex models | Hyperparameters control this balance |
| Overfitting | Model memorizes training data | Needs regularization hyperparameters |

### 📐 Grid Search vs Random Search vs Bayesian
| Method | How It Works | Pros | Cons | When to Use |
|--------|-------------|------|------|-------------|
| Grid Search | Exhaustive: try every combination | Guarantees finding best in grid | Very slow with many params | Small param space (< 4 params) |
| Random Search | Random samples from distributions | Faster, often finds good params | May miss the optimum | Large param space |
| Bayesian Optimisation | Uses past results to guide search | Most efficient | Complex to implement | Expensive training, many iterations |
| Halving Search | Starts many configs, eliminates poor ones early | Very efficient | Needs scikit-learn >= 0.24 | Large-scale search |
""")

tab_learn, tab_ref, tab_sim, tab_practice = st.tabs([
    "📖 Learn", "📋 Reference", "🎮 Simulator", "🧪 Practice"
])

with tab_learn:
    st.markdown("### 📖 Understanding Hyperparameters")
    
    st.markdown("""
#### 🔑 The Difference: Parameters vs Hyperparameters
    
| Aspect | Parameters | Hyperparameters |
|--------|-----------|-----------------|
| **What** | Model weights, biases | Learning rate, depth, regularization |
| **When** | Learned during training | Set before training |
| **How** | Optimised by algorithm | Set by data scientist |
| **Examples** | Linear regression coefficients | Max depth of decision tree |
| **Impact** | Directly from data | Controls learning process |
    
#### 🎯 Common Hyperparameters by Algorithm
""")
    
    algo = st.selectbox("Choose an algorithm to explore:", [
        "🌲 Random Forest", "🤖 Support Vector Machine", "📊 Gradient Boosting",
        "🔵 K-Nearest Neighbors", "📈 Logistic Regression", "🌳 Decision Tree",
        "🧠 Neural Network (MLP)"
    ], key="algo_select")
    
    algo_params = {
        "🌲 Random Forest": {
            "n_estimators": ("Number of trees", "100-1000", "More trees = better but slower. Diminishing returns after ~500"),
            "max_depth": ("Maximum tree depth", "5-30 or None", "None = full depth (risk of overfitting). Start with 10-20"),
            "min_samples_split": ("Min samples to split node", "2-20", "Higher = more regularized. Try 2, 5, 10"),
            "min_samples_leaf": ("Min samples at leaf", "1-10", "Higher = smoother. Try 1, 2, 4"),
            "max_features": ("Features per split", "'sqrt', 'log2', 0.3-1.0", "'sqrt' for classification, 0.3-0.5 good default"),
            "bootstrap": ("Bootstrap sampling", "True/False", "True = bagging (default). False = use whole dataset per tree"),
        },
        "🤖 Support Vector Machine": {
            "C": ("Regularization parameter", "0.01-100", "Low C = more regularization. Try 0.1, 1, 10"),
            "kernel": ("Kernel type", "'rbf', 'linear', 'poly'", "'rbf' is default and works well. 'linear' for high-dim text data"),
            "gamma": ("Kernel coefficient", "'scale', 'auto', 0.01-10", "'scale' = 1/(n_features * X.var). Small gamma = far influence"),
            "degree": ("Poly kernel degree", "2-5", "Only for 'poly' kernel. 3 is typical"),
        },
        "📊 Gradient Boosting": {
            "n_estimators": ("Number of boosting stages", "100-1000", "More = better but slower. Use with early stopping"),
            "learning_rate": ("Step size shrinkage", "0.01-0.3", "Lower = slower but better. 0.1 is default"),
            "max_depth": ("Individual tree depth", "3-8", "Shallow trees (3-5) work best for boosting"),
            "subsample": ("Fraction of samples per tree", "0.5-1.0", "< 1.0 = stochastic boosting (more regularization)"),
            "min_samples_leaf": ("Min samples at leaf", "1-20", "Higher = more regularized"),
        },
        "🔵 K-Nearest Neighbors": {
            "n_neighbors": ("Number of neighbors", "3-50", "Odd numbers for 2-class. More = smoother. Try 3, 5, 7, 11"),
            "weights": ("Weight function", "'uniform', 'distance'", "'distance' weights closer neighbors more — usually better"),
            "metric": ("Distance metric", "'minkowski', 'euclidean', 'manhattan'", "'euclidean' for continuous, 'manhattan' for mixed types"),
            "p": ("Minkowski power parameter", "1 or 2", "1 = Manhattan, 2 = Euclidean"),
        },
        "📈 Logistic Regression": {
            "C": ("Inverse regularization", "0.01-100", "Low C = strong regularization. Try 0.01, 0.1, 1, 10"),
            "penalty": ("Regularization type", "'l1', 'l2', 'elasticnet'", "'l2' is default. 'l1' for feature selection. 'elasticnet' for both"),
            "solver": ("Optimization algorithm", "'lbfgs', 'liblinear', 'saga'", "'lbfgs' for multiclass. 'liblinear' for small datasets"),
            "max_iter": ("Maximum iterations", "100-1000", "Increase if convergence warning"),
        },
        "🌳 Decision Tree": {
            "max_depth": ("Maximum depth", "3-30 or None", "Most important! Start with 5-10. None = overfitting risk"),
            "min_samples_split": ("Min samples to split", "2-20", "Higher = more regularized"),
            "min_samples_leaf": ("Min samples at leaf", "1-10", "Higher = smoother predictions"),
            "criterion": ("Split quality measure", "'gini', 'entropy'", "Similar performance. 'entropy' slightly slower"),
            "max_features": ("Features per split", "'sqrt', 'log2', None", "Fewer features = less overfitting"),
        },
        "🧠 Neural Network (MLP)": {
            "hidden_layer_sizes": ("Layer architecture", "(100,), (50,50), (100,50,25)", "Start simple. Deeper = more capacity but harder to train"),
            "activation": ("Activation function", "'relu', 'tanh', 'logistic'", "'relu' is default and usually best"),
            "alpha": ("L2 regularization", "0.0001-0.1", "Higher = more regularization. 0.001 good starting point"),
            "learning_rate_init": ("Initial learning rate", "0.001-0.1", "0.001 is default. Try 0.01 for faster convergence"),
            "batch_size": ("Mini-batch size", "32-256", "64 or 128 are good defaults. Smaller = more noise in updates"),
        },
    }
    
    if algo in algo_params:
        st.markdown(f"#### {algo} — Key Hyperparameters")
        for param, (desc, values, tip) in algo_params[algo].items():
            with st.expander(f"🎯 `{param}` — {desc}"):
                st.markdown(f"""
                - **Typical values:** `{values}`
                - **💡 Tip:** {tip}
                """)
    
    st.markdown("""
    #### 🚦 When to Tune Hyperparameters
    
    | Situation | Action |
    |-----------|--------|
    | Model is overfitting | Increase regularization, reduce depth, increase min_samples |
    | Model is underfitting | Reduce regularization, increase depth, add features |
    | Training is too slow | Reduce n_estimators, use fewer features, subsample |
    | Inconsistent results | Set random_state, use cross-validation |
    """)

with tab_ref:
    st.markdown("### 📋 Hyperparameter Quick Reference Card")
    
    st.markdown("""
    #### 🎯 Best Practices
    
    1. **Start simple** — Use default parameters first, then tune one at a time
    2. **Use cross-validation** — Always evaluate with k-fold CV (k=5 or 10)
    3. **Log your experiments** — Track what you tried and the results
    4. **Don't over-tune** — Small improvements (< 1%) may not be worth the complexity
    5. **Random search first** — Often finds good parameters much faster than grid search
    6. **Check for overfitting** — Compare train vs validation scores
    
    #### 🔢 Recommended Search Spaces
    """)
    
    search_spaces = pd.DataFrame({
        "Algorithm": ["Random Forest", "Random Forest", "Random Forest", "Random Forest",
                       "Gradient Boosting", "Gradient Boosting", "Gradient Boosting",
                       "SVM", "SVM", "SVM",
                       "KNN", "KNN",
                       "Logistic Regression", "Logistic Regression"],
        "Parameter": ["n_estimators", "max_depth", "min_samples_split", "max_features",
                       "n_estimators", "learning_rate", "max_depth",
                       "C", "gamma", "kernel",
                       "n_neighbors", "weights",
                       "C", "penalty"],
        "Search Type": ["Choice", "Choice/Range", "Choice", "Choice",
                         "Choice", "Log Uniform", "Choice",
                         "Log Uniform", "Choice", "Choice",
                         "Choice", "Choice",
                         "Log Uniform", "Choice"],
        "Values to Try": ["[100, 200, 500]", "[5, 10, 15, 20, None]", "[2, 5, 10]", "['sqrt', 'log2', 0.5]",
                           "[100, 200, 500]", "[0.01, 0.05, 0.1, 0.2]", "[3, 5, 7, 10]",
                           "[0.01, 0.1, 1, 10, 100]", "['scale', 'auto']", "['rbf', 'linear', 'poly']",
                           "[3, 5, 7, 11, 21]", "['uniform', 'distance']",
                           "[0.01, 0.1, 1, 10]", "['l1', 'l2']"],
    })
    st.dataframe(search_spaces, use_container_width=True, hide_index=True)
    
    st.markdown("""
    #### ⚡ Speed Tips
    
    | Tip | How | Impact |
    |-----|-----|--------|
    | Use `n_jobs=-1` | Parallelize search | 2-8x faster on multi-core |
    | Start with RandomSearch | Sample randomly | 90% of result with 10% of effort |
    | Use `HalvingGridSearchCV` | Eliminate poor configs early | 3-10x faster |
    | Reduce CV folds | Use 3-fold instead of 5-fold | 40% faster per config |
    | Subsample data | Train on 50% for search | 2x faster per config |
    """)

with tab_sim:
    st.markdown("### 🎮 Hyperparameter Search Simulator")
    st.caption("See how Grid Search and Random Search explore parameter space differently.")
    
    if st.session_state.get("df_cleaned") is not None:
        df = st.session_state["df_cleaned"]
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        if len(num_cols) >= 2:
            target_col = st.selectbox("Target column", num_cols, key="sim_target")
            feature_cols = st.multiselect("Feature columns", [c for c in num_cols if c != target_col], 
                                           default=[c for c in num_cols if c != target_col][:3], key="sim_features")
            
            if len(feature_cols) >= 1:
                from sklearn.model_selection import cross_val_score
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.preprocessing import LabelEncoder
                
                X = df[feature_cols].dropna()
                y = df.loc[X.index, target_col]
                
                # Encode target if needed
                if y.dtype == 'object' or y.nunique() <= 10:
                    le = LabelEncoder()
                    y = le.fit_transform(y.astype(str))
                
                st.markdown("#### Configure Search")
                c1, c2 = st.columns(2)
                with c1:
                    n_estimators_range = st.slider("n_estimators range", 50, 500, (50, 300), key="sim_n_est")
                    max_depth_range = st.slider("max_depth range", 2, 20, (2, 15), key="sim_depth")
                with c2:
                    n_grid_points = st.slider("Grid points per param", 3, 10, 5, key="sim_grid_pts")
                    n_random_trials = st.slider("Random search trials", 10, 50, 20, key="sim_random_trials")
                
                if st.button("🚀 Run Search Comparison", key="run_sim"):
                    # Grid Search
                    with st.spinner("Running Grid Search..."):
                        n_est_list = list(range(n_estimators_range[0], n_estimators_range[1]+1, 
                                                 max(1, (n_estimators_range[1]-n_estimators_range[0])//n_grid_points)))
                        depth_list = list(range(max_depth_range[0], max_depth_range[1]+1, 
                                                max(1, (max_depth_range[1]-max_depth_range[0])//n_grid_points)))
                        
                        grid_results = []
                        grid_total = len(n_est_list) * len(depth_list)
                        grid_bar = st.progress(0, text=f"Grid Search: 0/{grid_total} configs")
                        
                        for i, ne in enumerate(n_est_list):
                            for j, md in enumerate(depth_list):
                                try:
                                    model = RandomForestClassifier(n_estimators=ne, max_depth=md, random_state=42, n_jobs=-1)
                                    scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
                                    grid_results.append({
                                        'n_estimators': ne, 'max_depth': md,
                                        'mean_score': scores.mean(), 'std_score': scores.std()
                                    })
                                except:
                                    grid_results.append({
                                        'n_estimators': ne, 'max_depth': md,
                                        'mean_score': 0, 'std_score': 0
                                    })
                            grid_bar.progress((i+1)/len(n_est_list), text=f"Grid Search: {(i+1)*len(depth_list)}/{grid_total} configs")
                    
                    # Random Search
                    with st.spinner("Running Random Search..."):
                        np.random.seed(42)
                        random_results = []
                        rand_bar = st.progress(0, text=f"Random Search: 0/{n_random_trials} trials")
                        
                        for i in range(n_random_trials):
                            ne = np.random.randint(n_estimators_range[0], n_estimators_range[1]+1)
                            md = np.random.randint(max_depth_range[0], max_depth_range[1]+1)
                            try:
                                model = RandomForestClassifier(n_estimators=ne, max_depth=md, random_state=42, n_jobs=-1)
                                scores = cross_val_score(model, X, y, cv=3, scoring='accuracy')
                                random_results.append({
                                    'n_estimators': ne, 'max_depth': md,
                                    'mean_score': scores.mean(), 'std_score': scores.std()
                                })
                            except:
                                random_results.append({
                                    'n_estimators': ne, 'max_depth': md,
                                    'mean_score': 0, 'std_score': 0
                                })
                            rand_bar.progress((i+1)/n_random_trials, text=f"Random Search: {i+1}/{n_random_trials} trials")
                    
                    # Compare
                    grid_df = pd.DataFrame(grid_results)
                    random_df = pd.DataFrame(random_results)
                    
                    grid_best = grid_df.loc[grid_df['mean_score'].idxmax()]
                    random_best = random_df.loc[random_df['mean_score'].idxmax()]
                    
                    st.markdown("### 📊 Results Comparison")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Grid Search - Best Score", f"{grid_best['mean_score']:.4f}")
                        st.caption(f"n_estimators={int(grid_best['n_estimators'])}, max_depth={int(grid_best['max_depth'])}")
                        st.caption(f"Total evaluations: {len(grid_results)}")
                    with c2:
                        st.metric("Random Search - Best Score", f"{random_best['mean_score']:.4f}")
                        st.caption(f"n_estimators={int(random_best['n_estimators'])}, max_depth={int(random_best['max_depth'])}")
                        st.caption(f"Total evaluations: {len(random_results)}")
                    
                    efficiency = len(grid_results) / len(random_results)
                    st.info(f"⚡ Random Search achieved similar results with **{efficiency:.1f}x fewer** evaluations!")
                    
                    # Visualize
                    try:
                        import plotly.express as px
                        import plotly.graph_objects as go
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=grid_df['n_estimators'], y=grid_df['max_depth'],
                            mode='markers', marker=dict(size=8, color=grid_df['mean_score'], 
                            colorscale='Viridis', showscale=True, colorbar=dict(title="Accuracy")),
                            name='Grid Search', text=[f"Score: {s:.3f}" for s in grid_df['mean_score']]
                        ))
                        fig.add_trace(go.Scatter(
                            x=random_df['n_estimators'], y=random_df['max_depth'],
                            mode='markers', marker=dict(size=10, color=random_df['mean_score'],
                            colorscale='Viridis', symbol='diamond', showscale=False),
                            name='Random Search', text=[f"Score: {s:.3f}" for s in random_df['mean_score']]
                        ))
                        fig.update_layout(title="Parameter Space Exploration",
                                         xaxis_title="n_estimators", yaxis_title="max_depth",
                                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                    except:
                        pass
        else:
            st.info("Need at least 2 numeric columns for the simulator.")
    else:
        st.info("📥 Please load a dataset first.")

with tab_practice:
    st.markdown("### 🧪 Practice: Build Your Own Search Space")
    st.caption("Define your own hyperparameter search space and see the recommended strategy.")
    
    algos = {
        "Random Forest": ["n_estimators", "max_depth", "min_samples_split", "min_samples_leaf", "max_features", "bootstrap"],
        "Gradient Boosting": ["n_estimators", "learning_rate", "max_depth", "subsample", "min_samples_leaf"],
        "SVM": ["C", "kernel", "gamma", "degree"],
        "KNN": ["n_neighbors", "weights", "metric", "p"],
        "Logistic Regression": ["C", "penalty", "solver", "max_iter"],
    }
    
    selected_algo = st.selectbox("Algorithm", list(algos.keys()), key="practice_algo")
    available_params = algos[selected_algo]
    selected_params = st.multiselect("Select hyperparameters to tune", available_params, default=available_params[:2], key="practice_params")
    
    if selected_params:
        total_combos = 1
        param_details = []
        for p in selected_params:
            vals = st.text_input(f"Values for {p} (comma-separated)", key=f"practice_{p}")
            if vals:
                val_list = [v.strip() for v in vals.split(',')]
                total_combos *= len(val_list)
                param_details.append({"Parameter": p, "Values": vals, "N Values": len(val_list)})
        
        if param_details:
            st.dataframe(pd.DataFrame(param_details), use_container_width=True, hide_index=True)
            st.metric("Total Combinations", f"{total_combos:,}")
            
            if total_combos <= 20:
                st.success("✅ **Grid Search recommended** — Small search space, exhaustive search is feasible.")
            elif total_combos <= 100:
                st.warning("⚠️ **Random Search recommended** — Medium search space. Try 30-50 random trials first.")
            else:
                st.error("🔴 **Bayesian Optimisation recommended** — Large search space. Grid/Random will be too slow. Consider scikit-optimize or Optuna.")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Hyperparameter tuning is essential for getting the best model performance, 
but don't overdo it. Start with defaults, understand what each parameter does, and use Random Search 
before Grid Search. The most impactful parameters are usually `max_depth` and `n_estimators` for tree models, 
and `C` for linear models.

📚 **Next Steps:** After tuning, use Module 29 (Model Explainability) to understand your best model's predictions.
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
