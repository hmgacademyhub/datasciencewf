"""
Module 25: Dimensionality Reduction — DataScience Flow v9.5
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


st.set_page_config(page_title="Dimensionality Reduction | DataScience Flow", page_icon="📐", layout="wide")


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
## 📐 Dimensionality Reduction — Module 25

> **What is Dimensionality Reduction?** Dimensionality reduction transforms high-dimensional data into fewer 
> dimensions while preserving as much information as possible. This is essential for visualisation, noise 
> reduction, and avoiding the "curse of dimensionality."

### 🎓 Why Reduce Dimensions?
| Reason | Explanation |
|--------|-------------|
| **Visualisation** | Humans can only see 2-3 dimensions |
| **Noise Reduction** | Removing dimensions often removes noise |
| **Speed** | Fewer features = faster training |
| **Multicollinearity** | PCA creates uncorrelated components |
| **Overfitting Prevention** | Fewer features reduce model complexity |

### 📐 Methods Compared
| Method | Type | Preserves | Best For |
|--------|------|-----------|----------|
| PCA | Linear | Global variance | Feature compression, understanding variance |
| t-SNE | Non-linear | Local structure | Visualising clusters in 2D |
| UMAP | Non-linear | Both local & global | Better cluster visualisation than t-SNE |
| Truncated SVD | Linear | Variance (sparse data) | Text data, sparse matrices |

### ⚠️ Key Warnings
- **PCA is linear**: It cannot capture non-linear relationships
- **t-SNE is stochastic**: Different runs can give different results
- **t-SNE distances are not meaningful**: Cluster size and distance between clusters are not reliable
- **Always scale your data first**: PCA is sensitive to feature scales
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()

if len(num_cols) < 2:
    st.warning("Need at least 2 numeric columns for dimensionality reduction.")
    st.stop()

tab_pca, tab_tsne, tab_analysis = st.tabs(["📊 PCA", "🌀 t-SNE", "📐 Component Analysis"])

with tab_pca:
    st.markdown("### 📊 Principal Component Analysis (PCA)")
    
    feature_cols = st.multiselect("Features for PCA", num_cols, default=num_cols[:min(10, len(num_cols))], key="pca_feats")
    n_components = st.slider("Number of components", 2, min(len(feature_cols), 20), min(2, len(feature_cols)))
    
    if st.button("📊 Run PCA") and len(feature_cols) >= 2:
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA
        
        X = df[feature_cols].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(X_scaled)
        
        # Explained variance
        st.markdown("#### Explained Variance")
        ev_df = pd.DataFrame({
            "Component": [f"PC{i+1}" for i in range(n_components)],
            "Explained Variance %": (pca.explained_variance_ratio_ * 100).round(2),
            "Cumulative %": (pca.explained_variance_ratio_.cumsum() * 100).round(2)
        })
        st.dataframe(ev_df, use_container_width=True)
        
        import plotly.express as px
        fig = px.bar(ev_df, x="Component", y="Explained Variance %",
                    title="Scree Plot — Explained Variance by Component")
        st.plotly_chart(fig, use_container_width=True)
        
        fig_cum = px.line(ev_df, x="Component", y="Cumulative %",
                         title="Cumulative Explained Variance", markers=True)
        fig_cum.add_hline(y=90, line_dash="dash", annotation_text="90% threshold")
        st.plotly_chart(fig_cum, use_container_width=True)
        
        # 2D Scatter
        if n_components >= 2:
            pca_df = pd.DataFrame(components[:, :2], columns=["PC1", "PC2"])
            # Try to use a categorical column for coloring
            cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
            color_col = None
            if cat_cols:
                color_col = st.selectbox("Color by", ["None"] + cat_cols, key="pca_color")
                if color_col != "None":
                    pca_df[color_col] = df[color_col].dropna().values[:len(pca_df)]
            
            fig_scatter = px.scatter(pca_df, x="PC1", y="PC2", color=color_col if color_col != "None" else None,
                                    title="PCA — First Two Components", opacity=0.6)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Loadings
        st.markdown("#### Feature Loadings")
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f"PC{i+1}" for i in range(n_components)],
            index=feature_cols
        )
        st.dataframe(loadings.round(3), use_container_width=True)

with tab_tsne:
    st.markdown("### 🌀 t-SNE Visualisation")
    st.info("""**t-SNE** (t-Distributed Stochastic Neighbor Embedding) is a non-linear dimensionality 
    reduction technique specifically designed for visualisation. It excels at revealing cluster structure 
    in 2D plots.
    
    **Parameters:**
    - **Perplexity** (5-50): Roughly the number of nearest neighbors considered. Lower = more local structure.
    - **Learning Rate** (10-1000): Step size for optimization.
    - **Iterations** (250-1000+): More iterations = more stable result.
    
    **Note:** t-SNE is computationally expensive. For large datasets, consider running PCA first to reduce to ~50 dimensions, then t-SNE.
    """)
    
    feature_cols = st.multiselect("Features for t-SNE", num_cols, default=num_cols[:min(10, len(num_cols))], key="tsne_feats")
    perplexity = st.slider("Perplexity", 5, 50, 30, key="tsne_perp")
    n_iter = st.slider("Iterations", 250, 1000, 500, key="tsne_iter")
    
    max_samples = st.slider("Max samples (for speed)", 100, 10000, 2000, key="tsne_max")
    
    if st.button("🌀 Run t-SNE") and len(feature_cols) >= 2:
        from sklearn.preprocessing import StandardScaler
        from sklearn.manifold import TSNE
        
        X = df[feature_cols].dropna()
        if len(X) > max_samples:
            X = X.sample(n=max_samples, random_state=42)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        with st.spinner("Running t-SNE (this may take a moment)..."):
            tsne = TSNE(n_components=2, perplexity=perplexity, n_iter=n_iter, random_state=42)
            embedding = tsne.fit_transform(X_scaled)
        
        tsne_df = pd.DataFrame(embedding, columns=["t-SNE 1", "t-SNE 2"])
        
        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        color_col = None
        if cat_cols:
            color_col = st.selectbox("Color by", ["None"] + cat_cols, key="tsne_color")
            if color_col != "None":
                tsne_df[color_col] = df.loc[X.index, color_col].values
        
        import plotly.express as px
        fig = px.scatter(tsne_df, x="t-SNE 1", y="t-SNE 2",
                        color=color_col if color_col != "None" else None,
                        title="t-SNE Visualisation", opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)

with tab_analysis:
    st.markdown("### 📐 Component Analysis Guide")
    st.markdown("""
    ### 🎓 How to Interpret PCA Results
    
    **1. Scree Plot (Explained Variance)**
    - Look for the "elbow" — the point where adding more components gives diminishing returns
    - Aim for 80-95% cumulative explained variance
    - If the first 2-3 components explain 90%+ of variance, your data has strong structure
    
    **2. Feature Loadings**
    - High absolute loading (close to ±1) means the feature strongly influences that component
    - Features with similar loadings on the same component are correlated
    - Name your components based on which features load heavily on them
    
    **3. Scatter Plots**
    - Clear clusters → natural groupings in your data
    - Gradients → continuous variation
    - Random scatter → no clear structure (or need more components)
    
    ### 🇳🇬 Practical Example
    Imagine you have customer data with 20 features:
    - PC1 (40% variance): High loadings from income, spend, credit_score → "Financial Capacity"
    - PC2 (25% variance): High loadings from age, tenure → "Customer Maturity"
    - PC3 (15% variance): High loadings from web_visits, app_usage → "Digital Engagement"
    
    Now you understand your customers in 3 meaningful dimensions instead of 20 raw features!
    
    ### ⚠️ Common Mistakes
    1. **Not scaling first**: Features with larger scales dominate PCA
    2. **Interpreting t-SNE distances**: Cluster size ≠ data density in t-SNE
    3. **Too many components**: If you keep all components, you haven't reduced anything
    4. **Ignoring loadings**: Without understanding what components mean, they're useless
    """)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** PCA is your workhorse for feature compression and understanding variance structure. 
t-SNE is for beautiful cluster visualisation. Always scale before PCA, and interpret loadings to name your components.

📚 **Next Steps:** Use PCA components as features in Module 25 (ML Baseline) for potentially better model performance.
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
