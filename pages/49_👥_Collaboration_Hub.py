"""
Module 49: Collaboration Hub — DataScience Flow v9.5
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



st.set_page_config(page_title="Collaboration Hub | DataScience Flow", page_icon="👥", layout="wide")
st.markdown('<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D9A7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">👥 COLLABORATION HUB</div>', unsafe_allow_html=True)
st.markdown("""**🧠 What this module does:** Team session notes with author/tags/timestamps. Column-level annotations that integrate with Data Dictionary. Shared query library (from SQL Console). Team findings log. Collaboration summary report.

**🎯 Why you need it:** Data work is rarely solo. This module creates a shared context for teams — notes, annotations, and findings in one place.

**📖 How to use it:** Add notes → annotate columns → browse shared queries → export collaboration report.""")
if st.session_state.get("df") is None:
    st.warning("⚠️ No dataset loaded.")
    st.stop()
dfc = st.session_state["df_cleaned"]


st.markdown("### 👥 Team Collaboration Hub")

tab1, tab2, tab3 = st.tabs(["📝 Session Notes", "🏷️ Column Annotations", "📊 Team Findings Report"])

with tab1:
    author = st.text_input("Your name", st.session_state.get("sub_auth_email", "Anonymous"))
    tags = st.text_input("Tags (comma-separated)", "")
    note = st.text_area("Note", placeholder="Share your observation...")
    if st.button("📝 Add Note") and note:
        st.session_state["ent_collab_notes"].append({
            "author": author, "tags": tags, "note": note,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "dataset": st.session_state.get("filename", "Unknown")
        })
        st.success("Note added!")
        st.rerun()
    
    notes = st.session_state.get("ent_collab_notes", [])
    if notes:
        st.markdown(f"### {len(notes)} Team Notes")
        for n in reversed(notes[-10:]):
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:0.8rem;margin-bottom:0.5rem;">
                <strong>{n['author']}</strong> · <span style="color:#8b949e;">{n['timestamp']}</span>
                {f' · <span style="color:#00d9a7;">{n["tags"]}</span>' if n['tags'] else ''}<br>
                {n['note']}
            </div>
            """, unsafe_allow_html=True)

with tab2:
    col = st.selectbox("Column to annotate", dfc.columns.tolist())
    existing = st.session_state.get("data_dictionary", {}).get(col, {}).get("notes", "")
    annotation = st.text_area("Annotation", existing, help="This will be added to the Data Dictionary.")
    if st.button("🏷️ Save Annotation") and annotation:
        dd = st.session_state.get("data_dictionary", {})
        if col not in dd: dd[col] = {}
        dd[col]["notes"] = annotation
        st.session_state["data_dictionary"] = dd
        st.success(f"✅ Annotation saved for {col}")

with tab3:
    st.markdown("### 📊 Collaboration Summary Report")
    if st.button("📝 Generate Team Report"):
        notes = st.session_state.get("ent_collab_notes", [])
        report = f"""# Team Collaboration Report
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Dataset: {st.session_state.get('filename', 'N/A')}

## Team Notes ({len(notes)} total)
"""
        for n in notes:
            report += f"
- **{n['author']}** ({n['timestamp']}): {n['note']}"
        
        report += f"

## Column Annotations
"
        dd = st.session_state.get("data_dictionary", {})
        for col, info in dd.items():
            if info.get("notes"):
                report += f"
- **{col}**: {info['notes']}"
        
        report += f"

## Saved Queries ({len(st.session_state.get('sql_saved_queries', []))} total)
"
        for q in st.session_state.get("sql_saved_queries", [])[-5:]:
            report += f"
- {q.get('time', '')}: `{q.get('sql', '')[:100]}`"
        
        report += "

---
Generated by DataScience Flow Suite | HMG Concepts"
        st.download_button("⬇️ Download Team Report", report.encode(), "collaboration_report.md", "text/markdown")

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
