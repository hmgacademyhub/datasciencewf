"""
Module 36: SQL Query Console — DataScience Flow v9.5
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



st.set_page_config(page_title="SQL Query Console | DataScience Flow", page_icon="📋", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📋 SQL QUERY CONSOLE</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** DuckDB-powered in-memory SQL engine. Write SELECT, GROUP BY, JOINs, window functions, CTEs. Quick templates. Save and re-run queries. Download results as CSV.

**🎯 Why you need it:** SQL is the universal language of data. Query your loaded dataset with full SQL power — no database setup needed.

**📖 How to use it:** Write SQL → execute → view results → save query → download results.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📋 SQL Query Console (DuckDB)")
st.caption("Query your loaded data with full SQL. The table is named 'data'.")
try:
    import duckdb

    st.code("SELECT * FROM data LIMIT 5;", language="sql")
    st.markdown("**Your columns:** " + ", ".join(dfc.columns.tolist()[:20]))

    query_templates = {
        "SELECT * LIMIT 10": "SELECT * FROM data LIMIT 10;",
        "GROUP BY with COUNT": "SELECT {col}, COUNT(*) as cnt FROM data GROUP BY {col} ORDER BY cnt DESC LIMIT 10;",
        "Basic Aggregation": "SELECT AVG({num}) as avg_val, MIN({num}) as min_val, MAX({num}) as max_val FROM data;",
        "WHERE filter": "SELECT * FROM data WHERE {col} > 0 LIMIT 20;",
        "Window Function (ROW_NUMBER)": "SELECT *, ROW_NUMBER() OVER (ORDER BY {num} DESC) as rank FROM data LIMIT 20;",
    }

    template = st.selectbox("Quick templates", ["Custom SQL"] + list(query_templates.keys()))
    if template != "Custom SQL":
        sql = st.text_area("SQL Query", query_templates[template], height=100, key="sql_main")
    else:
        sql = st.text_area("SQL Query", "SELECT * FROM data LIMIT 10;", height=100, key="sql_custom")

    if st.button("▶️ Execute SQL"):
        if sql.strip():
            try:
                result = duckdb.query("data", dfc, sql).to_df()
                st.success(f"✅ {result.shape[0]:,} rows × {result.shape[1]} cols")
                st.dataframe(result, use_container_width=True)
                st.download_button("⬇️ Download Results", result.to_csv(index=False).encode(), "sql_results.csv", "text/csv")
                # Save query
                st.session_state["sql_saved_queries"].append({"sql": sql, "time": pd.Timestamp.now().strftime("%H:%M")})
            except Exception as e:
                st.error(f"SQL Error: {e}")

    # Saved queries
    if st.session_state.get("sql_saved_queries"):
        st.markdown("### 💾 Saved Queries")
        for i, q in enumerate(st.session_state["sql_saved_queries"][-5:]):
            st.markdown(f"**{q['time']}:** `{q['sql'][:80]}`")
except ImportError:
    st.warning("DuckDB not installed. Install with: pip install duckdb")

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
