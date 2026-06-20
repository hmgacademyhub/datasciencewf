"""
Module 11: Column Manager — DataScience Flow v9.5
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



st.set_page_config(page_title="Column Manager | DataScience Flow", page_icon="🗂️", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🗂️ COLUMN MANAGER</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Rename, reorder, drop columns. Bulk type-casting. 6 header-cleaning presets (lowercase, snake_case, trim, etc.). Duplicate-content column detection.

**🎯 Why you need it:** Clean column names make your data self-documenting. Consistent naming prevents errors in joins, merges, and shared analysis.

**📖 How to use it:** Select operation → choose columns → review changes → apply.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


op = st.selectbox("Operation", ["Bulk Rename", "Reorder Columns", "Drop Columns", "Change Data Type", "Clean Headers"])

if op == "Bulk Rename":
    st.markdown("### Rename Columns")
    col_map = {}
    for col in dfc.columns:
        new_name = st.text_input(f"'{col}' →", value=col, key=f"rn_{col}")
        if new_name != col: col_map[col] = new_name
    if col_map and st.button("✅ Apply Renames"):
        st.session_state["df_cleaned"] = dfc.rename(columns=col_map)
        st.success(f"Renamed {len(col_map)} columns."); st.rerun()

elif op == "Reorder Columns":
    new_order = st.multiselect("Drag to reorder", dfc.columns.tolist(), default=dfc.columns.tolist())
    if len(new_order) == len(dfc.columns) and st.button("✅ Apply Order"):
        st.session_state["df_cleaned"] = dfc[new_order]
        st.success("Reordered."); st.rerun()

elif op == "Drop Columns":
    to_drop = st.multiselect("Columns to drop", dfc.columns.tolist())
    if to_drop and st.button("🗑️ Drop Selected"):
        st.session_state["df_cleaned"] = dfc.drop(columns=to_drop)
        st.success(f"Dropped {len(to_drop)} columns."); st.rerun()

elif op == "Change Data Type":
    col = st.selectbox("Column", dfc.columns.tolist())
    new_type = st.selectbox("New type", ["int", "float", "str", "category", "datetime"])
    if st.button("✅ Change Type"):
        new_df = dfc.copy()
        try:
            if new_type == "int": new_df[col] = pd.to_numeric(new_df[col], errors="coerce").astype("Int64")
            elif new_type == "float": new_df[col] = pd.to_numeric(new_df[col], errors="coerce")
            elif new_type == "str": new_df[col] = new_df[col].astype(str)
            elif new_type == "category": new_df[col] = new_df[col].astype("category")
            elif new_type == "datetime": new_df[col] = pd.to_datetime(new_df[col], errors="coerce")
            st.session_state["df_cleaned"] = new_df
            st.success(f"Changed {col} to {new_type}"); st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

elif op == "Clean Headers":
    presets = st.multiselect("Presets", ["lowercase", "snake_case", "trim whitespace", "replace spaces with _", "remove special chars", "title case"])
    if presets and st.button("✅ Clean Headers"):
        new_df = dfc.copy()
        new_cols = new_df.columns.tolist()
        for i, c in enumerate(new_cols):
            if "lowercase" in presets: c = c.lower()
            if "snake_case" in presets: c = c.lower().replace(" ", "_").replace("-", "_")
            if "trim whitespace" in presets: c = c.strip()
            if "replace spaces with _" in presets: c = c.replace(" ", "_")
            if "remove special chars" in presets: c = "".join(e for e in c if e.isalnum() or e == "_")
            if "title case" in presets: c = c.title()
            new_cols[i] = c
        new_df.columns = new_cols
        st.session_state["df_cleaned"] = new_df
        st.success("Headers cleaned."); st.rerun()

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
