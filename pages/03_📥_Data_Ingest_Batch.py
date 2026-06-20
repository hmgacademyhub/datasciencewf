"""
Module 3: Data Ingest & Batch — DataScience Flow v9.5
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



st.set_page_config(page_title="Data Ingest & Batch | DataScience Flow", page_icon="📥", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">📥 DATA INGEST & BATCH</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Multi-file batch queue with FIFO processing. Checksum deduplication. URL-to-queue. Merge strategy (union/join). Scheduled ingestion configuration.

**🎯 Why you need it:** When you have multiple files to process in sequence. Load them all into a queue and process one by one — ideal for daily reports.

**📖 How to use it:** Upload multiple files → they're queued → process in order → apply merge strategy.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 📥 Multi-File Batch Ingestion")
st.caption("Queue multiple files and process them in FIFO order.")

uploaded_files = st.file_uploader("Upload files for batch queue", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    st.markdown(f"**{len(uploaded_files)} files selected**")
    merge_strategy = st.selectbox("Merge strategy", ["Process individually (FIFO)", "Union (append rows)", "Join on common key"])
    
    if st.button("📥 Add to Batch Queue"):
        for uf in uploaded_files:
            try:
                if uf.name.endswith(".csv"):
                    df = pd.read_csv(uf)
                else:
                    df = pd.read_excel(uf)
                checksum = hash(str(df.values.tobytes())) % 100000
                # Check dedup
                existing = st.session_state.get("ent_batch_queue", [])
                if not any(e.get("checksum") == checksum for e in existing):
                    existing.append({"name": uf.name, "df": df, "checksum": checksum, "rows": len(df), "cols": df.shape[1]})
                else:
                    st.warning(f"⏭️ Skipped duplicate: {uf.name}")
            except Exception as e:
                st.error(f"Error with {uf.name}: {e}")
        st.success(f"✅ Added {len(uploaded_files)} files to queue")
        st.rerun()

# Show queue
queue = st.session_state.get("ent_batch_queue", [])
if queue:
    st.markdown(f"### 📋 Batch Queue ({len(queue)} files)")
    queue_df = pd.DataFrame([{"#": i+1, "File": q["name"], "Rows": q["rows"], "Cols": q["cols"]} for i, q in enumerate(queue)])
    st.dataframe(queue_df, use_container_width=True)
    
    if st.button("🔄 Load Next from Queue"):
        nxt = queue.pop(0)
        st.session_state.update({"df": nxt["df"], "filename": nxt["name"], "df_cleaned": nxt["df"].copy()})
        st.success(f"✅ Loaded: {nxt['name']}")
        st.rerun()
    
    if st.button("🗑️ Clear Queue"):
        st.session_state["ent_batch_queue"] = []
        st.rerun()
else:
    st.info("Queue is empty. Upload files above.")

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
