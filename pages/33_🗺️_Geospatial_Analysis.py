"""
Module 33: Geospatial Analysis — DataScience Flow v9.5
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


st.set_page_config(page_title="Geospatial Analysis | DataScience Flow", page_icon="🗺️", layout="wide")


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
## 🗺️ Geospatial Analysis — Module 33

> **What is Geospatial Analysis?** Geospatial analysis examines data that has a geographic or spatial component — 
> coordinates, regions, postal codes, countries, or any location-based attribute. It reveals patterns that 
> traditional analysis cannot, such as clusters, spatial trends, and regional variations.

### 🎓 Why Geospatial Analysis Matters
- **Visual insight**: Maps reveal patterns invisible in tables and charts
- **Regional trends**: Sales, diseases, and demographics vary by location
- **Resource allocation**: Where to place stores, hospitals, or infrastructure
- **Risk assessment**: Flood zones, crime hotspots, climate vulnerability

### 📐 Common Geospatial Techniques
| Technique | What It Shows | When to Use |
|-----------|--------------|-------------|
| Choropleth | Colour-coded regions | Regional comparisons (e.g., revenue by state) |
| Point Map | Individual locations | Store locations, incidents |
| Heatmap | Density of points | Crime density, customer concentration |
| Bubble Map | Sized markers | Volume by location (e.g., sales per city) |

### 🇳🇬 Nigerian Context
- **State-level analysis**: 36 states + FCT Abuja
- **Common use cases**: WAEC performance by state, health indicators by region, market analysis by city
- **GeoJSON**: Nigerian state boundaries are widely available
- **Coordinates**: Latitude (4°N–14°N), Longitude (3°E–15°E)
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

tab_choropleth, tab_point, tab_coord = st.tabs(["🗺️ Choropleth Map", "📍 Point Map", "📐 Coordinate Analysis"])

with tab_choropleth:
    st.markdown("### 🗺️ Choropleth Map")
    st.info("Colour-code regions on a map based on a numeric value. Requires a column with region names (e.g., state, country).")
    
    location_col = st.selectbox("Location column (region names)", df.columns.tolist(), key="choro_loc")
    value_col = st.selectbox("Value column (numeric)", 
                              df.select_dtypes(include=np.number).columns.tolist(), key="choro_val")
    location_mode = st.selectbox("Location mode", ["country names", "USA states", "Nigerian states"])
    
    if st.button("🗺️ Generate Choropleth"):
        import plotly.express as px
        
        # Aggregate by location
        map_data = df.groupby(location_col)[value_col].mean().reset_index()
        
        if location_mode == "country names":
            fig = px.choropleth(map_data, locations=location_col, locationmode="country names",
                               color=value_col, title=f"Choropleth: {value_col} by {location_col}",
                               color_continuous_scale="Viridis")
        elif location_mode == "USA states":
            fig = px.choropleth(map_data, locations=location_col, locationmode="USA-states",
                               color=value_col, title=f"Choropleth: {value_col} by {location_col}",
                               color_continuous_scale="Viridis", scope="usa")
        else:
            # Nigerian states - use country name + state names
            fig = px.choropleth(map_data, locations=location_col, locationmode="country names",
                               color=value_col, title=f"Map: {value_col} by {location_col}",
                               color_continuous_scale="Viridis", scope="africa")
        
        st.plotly_chart(fig, use_container_width=True)

with tab_point:
    st.markdown("### 📍 Point Map")
    st.info("Plot individual data points on a map. Requires latitude and longitude columns.")
    
    lat_col = st.selectbox("Latitude column", df.columns.tolist(), key="point_lat")
    lon_col = st.selectbox("Longitude column", df.columns.tolist(), key="point_lon")
    size_col = st.selectbox("Size column (optional)", ["None"] + df.select_dtypes(include=np.number).columns.tolist(), key="point_size")
    color_col = st.selectbox("Color column (optional)", ["None"] + df.columns.tolist(), key="point_color")
    
    if st.button("📍 Generate Point Map"):
        import plotly.express as px
        
        # Filter valid coordinates
        valid = df[[lat_col, lon_col]].dropna()
        if len(valid) > 0:
            plot_kwargs = {
                "lat": lat_col, "lon": lon_col,
                "title": f"Point Map: {lat_col} x {lon_col}",
                "zoom": 5, "height": 600
            }
            if size_col != "None":
                plot_kwargs["size"] = size_col
            if color_col != "None":
                plot_kwargs["color"] = color_col
            
            fig = px.scatter_mapbox(df, **plot_kwargs, mapbox_style="carto-darkmatter", opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid coordinates found.")

with tab_coord:
    st.markdown("### 📐 Coordinate Analysis")
    st.info("Analyze the distribution and statistics of geographic coordinates.")
    
    coord_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['lat', 'lon', 'lng', 'latitude', 'longitude', 'x', 'y'])]
    
    if coord_cols:
        st.write("**Detected coordinate columns:**", coord_cols)
        for col in coord_cols:
            st.markdown(f"#### {col}")
            st.write(f"Min: {df[col].min():.4f}, Max: {df[col].max():.4f}")
            st.write(f"Mean: {df[col].mean():.4f}, Std: {df[col].std():.4f}")
    else:
        st.info("No obvious coordinate columns detected. Look for columns containing 'lat', 'lon', 'latitude', or 'longitude'.")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Maps reveal patterns that tables cannot. Even a simple choropleth can show 
regional disparities that would be invisible in a spreadsheet. Always consider the spatial dimension of your data.

📚 **Next Steps:** Use geospatial insights with Module 33 (What-If Analysis) to model location-based scenarios.
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
