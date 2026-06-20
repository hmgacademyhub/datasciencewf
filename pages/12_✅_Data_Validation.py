"""
Module 12: Data Validation — DataScience Flow v9.5
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


st.set_page_config(page_title="Data Validation | DataScience Flow", page_icon="✅", layout="wide")


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
## ✅ Data Validation — Module 12

> **What is Data Validation?** Data validation is the process of ensuring your data meets expected quality rules 
> before it enters your analysis or ML pipeline. Think of it as a quality checkpoint — catching bad data early 
> prevents garbage-in-garbage-out.

### 🎓 Why Validate Data?
- **Prevent pipeline failures**: Bad data types, unexpected nulls, and out-of-range values crash pipelines
- **Ensure statistical validity**: Analyses on invalid data produce misleading results
- **Meet regulatory requirements**: Data governance standards (GDPR, SOX) require data quality checks
- **Build trust**: Stakeholders trust results when data quality is verified

### 📐 Validation Rule Types
| Rule Type | Example | What It Checks |
|-----------|---------|----------------|
| Not Null | Email must not be null | Completeness |
| Type Check | Age must be integer | Data type consistency |
| Range | Age must be 0-120 | Logical bounds |
| Uniqueness | ID must be unique | No duplicates |
| Regex | Email matches pattern | Format compliance |
| Referential | State must be in valid list | Domain integrity |
| Custom | Revenue > 0 AND Cost < Revenue | Business logic |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]
validation_results = []

tab_auto, tab_schema, tab_custom, tab_report = st.tabs([
    "🔍 Auto Validation", "📋 Schema Check", "⚙️ Custom Rules", "📊 Validation Report"
])

with tab_auto:
    st.markdown("### 🔍 Automatic Validation Checks")
    
    # Null checks
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = null_count / len(df) * 100
        validation_results.append({
            "Rule": f"NOT_NULL:{col}", "Status": "✅ PASS" if null_count == 0 else "❌ FAIL",
            "Details": f"{null_count} nulls ({null_pct:.1f}%)", "Severity": "HIGH" if null_pct > 20 else "MEDIUM" if null_pct > 5 else "LOW"
        })
    
    # Duplicate checks
    dup_count = df.duplicated().sum()
    validation_results.append({
        "Rule": "NO_DUPLICATES", "Status": "✅ PASS" if dup_count == 0 else "❌ FAIL",
        "Details": f"{dup_count} duplicate rows ({dup_count/len(df)*100:.1f}%)", "Severity": "MEDIUM"
    })
    
    # Numeric range checks
    for col in df.select_dtypes(include=np.number).columns:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0 and col.lower() not in ['latitude', 'longitude', 'balance', 'change', 'diff', 'delta']:
            validation_results.append({
                "Rule": f"NON_NEGATIVE:{col}", "Status": "⚠️ WARNING",
                "Details": f"{negative_count} negative values", "Severity": "LOW"
            })
    
    # Unique ID checks
    for col in df.columns:
        if df[col].nunique() == len(df) and len(df) > 10:
            validation_results.append({
                "Rule": f"UNIQUE_IDENTIFIER:{col}", "Status": "ℹ️ INFO",
                "Details": f"All values unique — possible ID column", "Severity": "INFO"
            })
    
    results_df = pd.DataFrame(validation_results)
    pass_count = len(results_df[results_df["Status"] == "✅ PASS"])
    fail_count = len(results_df[results_df["Status"] == "❌ FAIL"])
    warn_count = len(results_df[results_df["Status"] == "⚠️ WARNING"])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Passed", pass_count)
    c2.metric("❌ Failed", fail_count)
    c3.metric("⚠️ Warnings", warn_count)
    
    # Filter
    status_filter = st.multiselect("Filter by status", ["✅ PASS", "❌ FAIL", "⚠️ WARNING", "ℹ️ INFO"], default=["❌ FAIL", "⚠️ WARNING"])
    filtered_results = results_df[results_df["Status"].isin(status_filter)]
    st.dataframe(filtered_results, use_container_width=True)

with tab_schema:
    st.markdown("### 📋 Schema Validation")
    st.info("Define expected schema rules for your dataset. The validator will check if your data conforms.")
    
    schema_rules = []
    for col in df.columns:
        with st.expander(f"📌 {col} ({df[col].dtype})"):
            expected_type = st.selectbox("Expected type", [
                "Any", "integer", "float", "string", "datetime", "boolean"
            ], key=f"schema_type_{col}")
            allow_null = st.checkbox("Allow nulls", value=True, key=f"schema_null_{col}")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val = st.number_input("Min value", value=float(df[col].min()), key=f"schema_min_{col}")
                max_val = st.number_input("Max value", value=float(df[col].max()), key=f"schema_max_{col}")
                schema_rules.append({
                    "Column": col, "Expected Type": expected_type,
                    "Allow Nulls": allow_null, "Min": min_val, "Max": max_val
                })
            else:
                schema_rules.append({
                    "Column": col, "Expected Type": expected_type,
                    "Allow Nulls": allow_null, "Min": "—", "Max": "—"
                })
    
    if st.button("🔍 Validate Schema"):
        schema_results = []
        for rule in schema_rules:
            col = rule["Column"]
            col_data = df[col]
            issues = []
            
            # Type check
            if rule["Expected Type"] == "integer" and not pd.api.types.is_integer_dtype(col_data):
                issues.append("Not integer type")
            elif rule["Expected Type"] == "float" and not pd.api.types.is_float_dtype(col_data):
                issues.append("Not float type")
            elif rule["Expected Type"] == "string" and not pd.api.types.is_string_dtype(col_data):
                issues.append("Not string type")
            
            # Null check
            if not rule["Allow Nulls"] and col_data.isnull().sum() > 0:
                issues.append(f"{col_data.isnull().sum()} null values found")
            
            # Range check
            if isinstance(rule["Min"], (int, float)) and pd.api.types.is_numeric_dtype(col_data):
                below_min = (col_data < rule["Min"]).sum()
                above_max = (col_data > rule["Max"]).sum()
                if below_min > 0:
                    issues.append(f"{below_min} values below min ({rule['Min']})")
                if above_max > 0:
                    issues.append(f"{above_max} values above max ({rule['Max']})")
            
            schema_results.append({
                "Column": col,
                "Status": "✅ PASS" if len(issues) == 0 else "❌ FAIL",
                "Issues": "; ".join(issues) if issues else "None"
            })
        
        st.dataframe(pd.DataFrame(schema_results), use_container_width=True)

with tab_custom:
    st.markdown("### ⚙️ Custom Validation Rules")
    st.info("Write custom validation rules using Python expressions. The variable `df` contains your dataset.")
    
    rule_name = st.text_input("Rule name", "Revenue is positive")
    rule_expr = st.text_area("Python expression (must return boolean Series)", "df.select_dtypes(include=np.number).gt(0).all(axis=1)")
    
    if st.button("▶️ Run Custom Rule"):
        try:
            result = eval(rule_expr, {"df": df, "pd": pd, "np": np})
            if isinstance(result, pd.Series):
                pass_rate = result.mean() * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
                st.metric("Failed Rows", int((~result).sum()))
                if pass_rate == 100:
                    st.success("✅ All rows pass this rule!")
                else:
                    st.warning(f"⚠️ {(~result).sum()} rows fail this rule.")
                    failed_df = df[~result]
                    st.dataframe(failed_df.head(20), use_container_width=True)
            else:
                st.info(f"Result: {result}")
        except Exception as e:
            st.error(f"Rule execution error: {e}")

with tab_report:
    st.markdown("### 📊 Validation Report Summary")
    total_checks = len(validation_results)
    pass_rate = pass_count / total_checks * 100 if total_checks > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Checks", total_checks)
    c2.metric("Pass Rate", f"{pass_rate:.1f}%")
    c3.metric("High Severity", len([r for r in validation_results if r["Severity"] == "HIGH"]))
    c4.metric("Data Quality Score", f"{min(100, pass_rate + 10):.0f}/100")
    
    st.dataframe(pd.DataFrame(validation_results), use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Data validation should be run **before** any analysis or modelling. 
Build a validation suite that runs automatically whenever new data arrives. 
This is how production ML pipelines maintain data quality.

📚 **Next Steps:** Combine with Module 12 (Data Quality Audit) for a comprehensive quality scorecard.
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
