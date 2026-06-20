"""
Module 52: Dashboard Builder — DataScience Flow v9.5
Drag-and-drop dashboard creation, widget library, templates
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Dashboard Builder | DataScience Flow", page_icon="📊", layout="wide")

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
## 📊 Dashboard Builder — Module 52

> **What is a Data Dashboard?** A dashboard is a visual display of key metrics, charts, and indicators 
> arranged on a single page for quick monitoring and decision-making. Good dashboards tell a story with data.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| KPI | Key Performance Indicator | The most important number to track |
| Widget | A single visual element (chart, metric, table) | Building blocks of dashboards |
| Layout | Arrangement of widgets | Guides the viewer's attention |
| Interactivity | Filters, drill-downs, selectors | Lets users explore their own questions |
| Real-time | Auto-updating data | For monitoring live systems |

### 📐 Dashboard Design Principles
| Principle | Description | Example |
|-----------|-------------|---------|
| Start with KPIs | Most important numbers at the top | Total revenue, conversion rate |
| 5-second rule | Viewer should get the story in 5 seconds | Clear title, obvious highlights |
| Progressive detail | Summary → Details → Raw data | Metric → Chart → Table |
| Consistent colors | Same metric = same color across charts | Revenue always blue |
| Minimal text | Let the data speak | Remove unnecessary labels |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

if "dashboard_widgets" not in st.session_state:
    st.session_state["dashboard_widgets"] = []

tab_build, tab_preview, tab_templates = st.tabs(["🛠️ Build", "👁️ Preview", "📋 Templates"])

with tab_build:
    st.markdown("### 🛠️ Add Widgets to Your Dashboard")
    
    widget_types = {
        "📊 Metric Card": "Single KPI with trend indicator",
        "📈 Bar Chart": "Compare categories or show trends",
        "📉 Line Chart": "Show trends over time or categories",
        "🥧 Pie/Donut Chart": "Show proportions of a whole",
        "🗺️ Scatter Plot": "Show relationship between two variables",
        "📊 Histogram": "Show distribution of a variable",
        "📋 Data Table": "Show raw data in a table",
        "📊 Correlation Heatmap": "Show correlations between numeric columns",
        "📦 Box Plot": "Show distribution statistics",
        "📊 Summary Stats": "Descriptive statistics panel",
    }
    
    c1, c2 = st.columns([1, 2])
    with c1:
        widget_type = st.selectbox("Widget type", list(widget_types.keys()), key="widget_type")
    with c2:
        st.caption(widget_types[widget_type])
    
    widget_config = {"type": widget_type}
    
    # Configuration per widget type
    if widget_type == "📊 Metric Card":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        metric_col = st.selectbox("Metric column", num_cols, key="metric_col")
        agg = st.selectbox("Aggregation", ["sum", "mean", "median", "count", "min", "max", "std"], key="metric_agg")
        label = st.text_input("Custom label", metric_col, key="metric_label")
        widget_config["config"] = {"column": metric_col, "aggregation": agg, "label": label}
        
    elif widget_type in ["📈 Bar Chart", "📉 Line Chart"]:
        all_cols = df.columns.tolist()
        x_col = st.selectbox("X-axis", all_cols, key="bar_x")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        y_col = st.selectbox("Y-axis", num_cols if num_cols else all_cols, key="bar_y")
        color_col = st.selectbox("Color by", ["None"] + all_cols, key="bar_color")
        widget_config["config"] = {"x": x_col, "y": y_col, "color": color_col if color_col != "None" else None}
        
    elif widget_type == "🥧 Pie/Donut Chart":
        all_cols = df.columns.tolist()
        names_col = st.selectbox("Category column", all_cols, key="pie_names")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        values_col = st.selectbox("Values column", ["Count"] + num_cols, key="pie_values")
        widget_config["config"] = {"names": names_col, "values": values_col}
        
    elif widget_type == "🗺️ Scatter Plot":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if len(num_cols) >= 2:
            x_col = st.selectbox("X-axis", num_cols, key="scatter_x")
            y_col = st.selectbox("Y-axis", [c for c in num_cols if c != x_col], key="scatter_y")
            color_col = st.selectbox("Color by", ["None"] + df.columns.tolist(), key="scatter_color")
            widget_config["config"] = {"x": x_col, "y": y_col, "color": color_col if color_col != "None" else None}
        else:
            st.warning("Need at least 2 numeric columns.")
            
    elif widget_type == "📊 Histogram":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        col = st.selectbox("Column", num_cols, key="hist_col")
        bins = st.slider("Number of bins", 10, 100, 30, key="hist_bins")
        widget_config["config"] = {"column": col, "bins": bins}
        
    elif widget_type == "📋 Data Table":
        widget_config["config"] = {"max_rows": st.slider("Max rows", 5, 50, 10, key="table_rows")}
        
    elif widget_type == "📊 Correlation Heatmap":
        widget_config["config"] = {}
        
    elif widget_type == "📦 Box Plot":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        col = st.selectbox("Column", num_cols, key="box_col")
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        group_col = st.selectbox("Group by", ["None"] + cat_cols, key="box_group")
        widget_config["config"] = {"column": col, "group": group_col if group_col != "None" else None}
        
    elif widget_type == "📊 Summary Stats":
        widget_config["config"] = {}
    
    widget_config["title"] = st.text_input("Widget title", widget_type, key="widget_title")
    
    if st.button("➕ Add Widget", key="add_widget"):
        st.session_state["dashboard_widgets"].append(widget_config)
        st.success(f"✅ Added: {widget_type}")
        st.rerun()
    
    # Current widgets
    if st.session_state["dashboard_widgets"]:
        st.markdown("---")
        st.markdown(f"### 📋 Dashboard Layout ({len(st.session_state['dashboard_widgets'])} widgets)")
        
        for i, w in enumerate(st.session_state["dashboard_widgets"]):
            c1, c2, c3 = st.columns([0.85, 0.1, 0.05])
            with c1:
                st.markdown(f"**{i+1}. {w.get('title', w['type'])}** — {w['type']}")
            with c2:
                if st.button("⬆️", key=f"up_{i}") and i > 0:
                    st.session_state["dashboard_widgets"][i], st.session_state["dashboard_widgets"][i-1] = \
                        st.session_state["dashboard_widgets"][i-1], st.session_state["dashboard_widgets"][i]
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_w_{i}"):
                    st.session_state["dashboard_widgets"].pop(i)
                    st.rerun()
        
        if st.button("🗑️ Clear All Widgets"):
            st.session_state["dashboard_widgets"] = []
            st.rerun()

with tab_preview:
    st.markdown("### 👁️ Dashboard Preview")
    
    if not st.session_state["dashboard_widgets"]:
        st.info("No widgets added yet. Go to Build tab to add widgets.")
    else:
        # Global filters
        with st.expander("🎛️ Global Filters", expanded=False):
            all_cols = df.columns.tolist()
            filter_col = st.selectbox("Filter by column", ["None"] + all_cols, key="global_filter")
            if filter_col != "None":
                unique_vals = df[filter_col].unique().tolist()
                selected_vals = st.multiselect("Select values", unique_vals, default=unique_vals, key="global_filter_vals")
                filtered_df = df[df[filter_col].isin(selected_vals)]
            else:
                filtered_df = df
        
        # Render widgets
        for i, w in enumerate(st.session_state["dashboard_widgets"]):
            config = w.get("config", {})
            
            if w["type"] == "📊 Metric Card":
                col_name = config.get("column", "")
                if col_name in filtered_df.columns:
                    agg = config.get("aggregation", "mean")
                    val = filtered_df[col_name].agg(agg)
                    st.metric(w.get("title", col_name), f"{val:,.2f}" if isinstance(val, float) else f"{val:,}")
            
            elif w["type"] == "📈 Bar Chart":
                fig = px.bar(filtered_df, x=config.get("x"), y=config.get("y"), 
                            color=config.get("color"), title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "📉 Line Chart":
                fig = px.line(filtered_df, x=config.get("x"), y=config.get("y"),
                             color=config.get("color"), title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "🥧 Pie/Donut Chart":
                names = config.get("names")
                values = config.get("values")
                if values == "Count":
                    pie_data = filtered_df[names].value_counts().reset_index()
                    pie_data.columns = [names, "count"]
                    fig = px.pie(pie_data, names=names, values="count", title=w.get("title"))
                else:
                    fig = px.pie(filtered_df, names=names, values=values, title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "🗺️ Scatter Plot":
                fig = px.scatter(filtered_df, x=config.get("x"), y=config.get("y"),
                                color=config.get("color"), title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "📊 Histogram":
                fig = px.histogram(filtered_df, x=config.get("column"), nbins=config.get("bins", 30), title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "📋 Data Table":
                st.markdown(f"**{w.get('title', 'Data Table')}**")
                st.dataframe(filtered_df.head(config.get("max_rows", 10)), use_container_width=True)
            
            elif w["type"] == "📊 Correlation Heatmap":
                num_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
                if len(num_cols) >= 2:
                    corr = filtered_df[num_cols].corr()
                    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns,
                                                    colorscale="RdBu_r", zmin=-1, zmax=1))
                    fig.update_layout(title=w.get("title", "Correlation"), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "📦 Box Plot":
                fig = px.box(filtered_df, y=config.get("column"), 
                            x=config.get("group"), title=w.get("title"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            
            elif w["type"] == "📊 Summary Stats":
                st.markdown(f"**{w.get('title', 'Summary Statistics')}**")
                st.dataframe(filtered_df.describe(), use_container_width=True)

with tab_templates:
    st.markdown("### 📋 Dashboard Templates")
    
    templates = {
        "📈 Sales Dashboard": [
            {"type": "📊 Metric Card", "title": "Total Revenue", "config": {"column": "Sales", "aggregation": "sum", "label": "Revenue"}},
            {"type": "📊 Metric Card", "title": "Avg Order Value", "config": {"column": "Sales", "aggregation": "mean", "label": "Avg Value"}},
            {"type": "📈 Bar Chart", "title": "Sales by Category", "config": {"x": "Category", "y": "Sales", "color": None}},
            {"type": "🥧 Pie/Donut Chart", "title": "Region Split", "config": {"names": "Region", "values": "Count"}},
        ],
        "📊 Data Overview": [
            {"type": "📊 Summary Stats", "title": "Quick Stats", "config": {}},
            {"type": "📊 Histogram", "title": "Distribution", "config": {"column": "auto", "bins": 30}},
            {"type": "📊 Correlation Heatmap", "title": "Correlations", "config": {}},
            {"type": "📋 Data Table", "title": "Data Preview", "config": {"max_rows": 20}},
        ],
    }
    
    for name, widgets in templates.items():
        with st.expander(name):
            for i, w in enumerate(widgets):
                st.markdown(f"{i+1}. {w['type']} — {w.get('title', '')}")
            if st.button(f"📋 Use Template", key=f"dash_template_{name}"):
                st.session_state["dashboard_widgets"] = widgets.copy()
                st.success("✅ Template loaded! Go to Preview tab to see your dashboard.")
                st.rerun()

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** A great dashboard answers questions at a glance. Start with your key metrics, 
support them with visualizations, and let users drill down for details. Keep it simple — 
the best dashboards are the ones people actually use.

📚 **Next Steps:** Use Module 53 (Learning Hub) to learn more about data visualization best practices.
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
