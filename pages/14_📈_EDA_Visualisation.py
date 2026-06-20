"""
Module 14: EDA & Visualisation — DataScience Flow v9.5
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




st.set_page_config(page_title="EDA & Visualisation | DataScience Flow", page_icon="📈", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📈 EDA & VISUALISATION</div>', unsafe_allow_html=True)
st.markdown("""
**🧠 What this module does:** Creates 12+ chart types — histogram, box, scatter, line, bar, pie, heatmap (correlation), violin, density, word cloud, treemap, sunburst, and more.

**🎯 Why you need it:** Visualisation is the fastest way to understand your data. Patterns that hide in tables jump out in charts. This module is your visual exploration sandbox.

**📖 How to use it:** Pick a chart type → select columns → adjust parameters → the chart updates instantly.
""")

if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded. Please upload a file from the Home page sidebar.")
    st.stop()

dfc = st.session_state["df_cleaned"]
st.session_state.get("steps_done", set()).add("eda")


chart_type = st.selectbox("Chart type", [
    "📊 Histogram", "📦 Box Plot", "🎯 Scatter Plot", "📈 Line Chart",
    "📊 Bar Chart", "🥧 Pie Chart", "🔥 Correlation Heatmap",
    "🎻 Violin Plot", "📉 Density Plot", "☁️ Word Cloud"
])

numeric_cols = dfc.select_dtypes(include=np.number).columns.tolist()
cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()

if chart_type == "📊 Histogram":
    col = st.selectbox("Column", numeric_cols)
    bins = st.slider("Bins", 5, 100, 30)
    fig = px.histogram(dfc, x=col, nbins=bins, template="plotly_dark",
        color_discrete_sequence=["#00d9a7"], title=f"Histogram — {col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "📦 Box Plot":
    y_col = st.selectbox("Value (Y)", numeric_cols)
    x_col = st.selectbox("Group (X) — optional", ["None"] + cat_cols)
    fig = px.box(dfc, y=y_col, x=None if x_col == "None" else x_col, template="plotly_dark",
        color_discrete_sequence=["#00d9a7"], title=f"Box Plot — {y_col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "🎯 Scatter Plot":
    x_col = st.selectbox("X-axis", numeric_cols, index=0)
    y_col = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1))
    color_col = st.selectbox("Color (optional)", ["None"] + dfc.columns.tolist())
    fig = px.scatter(dfc, x=x_col, y=y_col, color=None if color_col == "None" else color_col,
        template="plotly_dark", title=f"Scatter: {x_col} vs {y_col}",
        color_continuous_scale="teal" if color_col != "None" and color_col in numeric_cols else None)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "📈 Line Chart":
    x_col = st.selectbox("X-axis", dfc.columns.tolist())
    y_col = st.selectbox("Y-axis", numeric_cols)
    fig = px.line(dfc, x=x_col, y=y_col, template="plotly_dark",
        color_discrete_sequence=["#4f8ef7"], title=f"Line Chart — {y_col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "📊 Bar Chart":
    x_col = st.selectbox("Category (X)", cat_cols if cat_cols else dfc.columns.tolist())
    y_col = st.selectbox("Value (Y) — optional", ["Count"] + numeric_cols)
    if y_col == "Count":
        vc = dfc[x_col].value_counts().head(30).reset_index()
        vc.columns = [x_col, "Count"]
        fig = px.bar(vc, x=x_col, y="Count", template="plotly_dark",
            color_discrete_sequence=["#00d9a7"], title=f"Bar Chart — {x_col}")
    else:
        fig = px.bar(dfc.head(50), x=x_col, y=y_col, template="plotly_dark",
            color_discrete_sequence=["#00d9a7"], title=f"Bar: {x_col} vs {y_col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "🥧 Pie Chart":
    col = st.selectbox("Category column", cat_cols if cat_cols else dfc.columns.tolist())
    vc = dfc[col].value_counts().head(10)
    fig = px.pie(values=vc.values, names=vc.index, template="plotly_dark",
        title=f"Pie Chart — {col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "🔥 Correlation Heatmap":
    if len(numeric_cols) > 1:
        corr = dfc[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1, text=corr.values.round(2), texttemplate="%{text}"))
        fig.update_layout(title="Correlation Heatmap", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=max(400, 20*len(numeric_cols)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Need at least 2 numeric columns for correlation heatmap.")

elif chart_type == "🎻 Violin Plot":
    y_col = st.selectbox("Value (Y)", numeric_cols)
    x_col = st.selectbox("Group (X)", cat_cols if cat_cols else dfc.columns.tolist())
    fig = px.violin(dfc, y=y_col, x=x_col, box=True, template="plotly_dark",
        color_discrete_sequence=["#00d9a7"], title=f"Violin Plot — {y_col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "📉 Density Plot":
    col = st.selectbox("Column", numeric_cols)
    fig = px.density_contour(dfc, x=col, template="plotly_dark",
        color_discrete_sequence=["#00d9a7"], title=f"Density — {col}")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "☁️ Word Cloud":
    col = st.selectbox("Text column", cat_cols if cat_cols else dfc.columns.tolist())
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        text = " ".join(dfc[col].dropna().astype(str).tolist())
        if text:
            wc = WordCloud(width=800, height=400, background_color="#0d1117",
                colormap="viridis", max_words=100).generate(text)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            fig.patch.set_facecolor("#0d1117")
            st.pyplot(fig)
        else:
            st.warning("No text data to generate word cloud.")
    except ImportError:
        st.warning("WordCloud library not available. Install with: pip install wordcloud")

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
