"""
Module 67: Network Analysis - DataScience Flow v10.0
Part of HMG Academy Ecosystem - Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
st.set_page_config(page_title="Network Analysis | DataScience Flow", page_icon="N", layout="wide")
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription
from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)

init_secure_session()
if not st.session_state.get('sub_authenticated'):
    st.warning('Subscription required.')
    st.stop()
if not verify_subscription_integrity():
    st.error('Session integrity failed.')
    st.stop()
if check_session_timeout():
    st.warning('Session expired.')
    st.stop()
check_rate_limit()

st.markdown("## Network Analysis - Module 67")
st.info("This module provides network analysis functionality. Use the sidebar modules for specific tasks.")
if st.session_state.get("df_cleaned") is not None:
    df = st.session_state["df_cleaned"]
    st.metric("Dataset Size", f"{len(df):,} rows x {len(df.columns)} cols")
else:
    st.warning("Load a dataset from the Home page to use this module.")

st.markdown("---")
st.markdown("""<div style="text-align:center;padding:16px 0;font-size:0.82rem;color:#A0A8B8;"><b>DataScience Flow</b> v10.0 - Part of <b>HMG Academy</b> Ecosystem - Subsidiary of <b>HMG Concepts</b> (est. 2015)<br>Built by <b>Adewale Samson Adeagbo</b> | His Marvellous Grace<br><a href="https://hmgacademy.pages.dev" style="color:#6C63FF;">hmgacademy.pages.dev</a> | <a href="https://hmgconcepts.pages.dev" style="color:#6C63FF;">hmgconcepts.pages.dev</a></div>""", unsafe_allow_html=True)
