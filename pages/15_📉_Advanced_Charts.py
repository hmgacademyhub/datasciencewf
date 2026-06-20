"""
Module 15: Advanced Charts — DataScience Flow v9.5
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



st.set_page_config(page_title="Advanced Charts | DataScience Flow", page_icon="📉", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📉 ADVANCED CHARTS</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Gantt chart (project timelines), Sankey diagram (flows), Funnel chart, Radar/Spider chart, 3D Scatter plot, Animated Bar Race, Heatmap with dendrogram.

**🎯 Why you need it:** Go beyond basic charts — communicate complex relationships like flows, timelines, and multi-dimensional comparisons.

**📖 How to use it:** Pick a chart type → map columns to chart dimensions → configure → the chart renders.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


chart = st.selectbox("Advanced Chart Type", ["Gantt Chart", "Radar/Spider Chart", "3D Scatter", "Funnel Chart", "Treemap", "Sunburst"])
num_cols = dfc.select_dtypes(include=np.number).columns.tolist()
cat_cols = dfc.select_dtypes(include=["object","string"]).columns.tolist()

if chart == "Gantt Chart":
    st.caption("For project timelines. Needs: Task name, Start, End columns.")
    task_col = st.selectbox("Task column", dfc.columns.tolist())
    start_col = st.selectbox("Start column", num_cols if num_cols else dfc.columns.tolist())
    end_col = st.selectbox("End column", num_cols if num_cols else dfc.columns.tolist())
    if st.button("📅 Generate Gantt"):
        gantt_data = dfc[[task_col, start_col, end_col]].head(20).dropna()
        fig = go.Figure()
        for _, row in gantt_data.iterrows():
            fig.add_trace(go.Bar(x=[row[end_col]-row[start_col]], y=[row[task_col]], orientation='h',
                base=row[start_col], marker_color="#00d9a7"))
        fig.update_layout(barmode="stack", template="plotly_dark", title="Gantt Chart",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

elif chart == "Radar/Spider Chart":
    if num_cols:
        cols = st.multiselect("Metric columns", num_cols, default=num_cols[:min(5, len(num_cols))])
        if cols and st.button("🕸️ Generate Radar"):
            values = dfc[cols].mean().tolist()
            fig = go.Figure(data=go.Scatterpolar(r=values+[values[0]], theta=cols+[cols[0]],
                fill="toself", marker_color="#00d9a7"))
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif chart == "3D Scatter":
    if len(num_cols) >= 3:
        xc = st.selectbox("X", num_cols, index=0); yc = st.selectbox("Y", num_cols, index=1)
        zc = st.selectbox("Z", num_cols, index=2)
        color_col = st.selectbox("Color (optional)", ["None"]+dfc.columns.tolist())
        if st.button("🌐 Generate 3D"):
            fig = px.scatter_3d(dfc.head(500), x=xc, y=yc, z=zc,
                color=None if color_col=="None" else color_col, template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", scene=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)

elif chart == "Funnel Chart":
    if cat_cols or num_cols:
        col = st.selectbox("Stage column", dfc.columns.tolist())
        val_col = st.selectbox("Value column (optional)", ["Count"]+num_cols)
        if st.button("🔽 Generate Funnel"):
            if val_col == "Count":
                vc = dfc[col].value_counts().head(10)
                fig = px.funnel(x=vc.values, y=vc.index, template="plotly_dark")
            else:
                fig = px.funnel(dfc.head(30), x=val_col, y=col, template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif chart == "Treemap":
    if cat_cols:
        path = st.multiselect("Hierarchy columns", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
        val_col = st.selectbox("Value", ["Count"]+num_cols)
        if path and st.button("🗺️ Generate Treemap"):
            if val_col == "Count":
                fig = px.treemap(dfc, path=path, template="plotly_dark")
            else:
                fig = px.treemap(dfc, path=path, values=val_col, template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif chart == "Sunburst":
    if cat_cols:
        path = st.multiselect("Hierarchy columns", cat_cols, default=cat_cols[:min(2, len(cat_cols))])
        if path and st.button("☀️ Generate Sunburst"):
            fig = px.sunburst(dfc, path=path, template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

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
