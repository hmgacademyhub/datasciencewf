"""
Module 51: Pipeline Builder — DataScience Flow v9.5
Visual data pipeline builder, step-by-step ETL workflow
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

st.set_page_config(page_title="Pipeline Builder | DataScience Flow", page_icon="📥", layout="wide")

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
## 📥 Pipeline Builder — Module 51

> **What is a Data Pipeline?** A data pipeline is a sequence of automated steps that transform raw data 
> into a final, analysis-ready format. Pipelines ensure **reproducibility** — run the same steps on new data 
> and get consistent results.

### 🎓 Key Concepts
| Concept | What It Means | Why It Matters |
|---------|---------------|----------------|
| ETL | Extract → Transform → Load | Classic data pipeline pattern |
| Step | Single operation (clean, filter, transform) | Building blocks of a pipeline |
| Pipeline | Ordered sequence of steps | Ensures reproducibility |
| DAG | Directed Acyclic Graph | Complex pipelines with branches |
| Idempotent | Same result no matter how many times run | Critical for reliability |
| Checkpoint | Save intermediate results | Enables debugging and recovery |

### 📐 Common Pipeline Patterns
| Pattern | Description | When to Use |
|---------|-------------|-------------|
| Linear | Step1 → Step2 → Step3 | Simple workflows |
| Branching | Step1 → Step2a, Step2b | Multiple outputs needed |
| Loop | Step1 → Step2 → Step1 | Iterative processing |
| Fan-in | Step1a, Step1b → Step2 | Merging multiple sources |
""")

if st.session_state.get("df_cleaned") is None:
    st.warning("📥 Please load a dataset from the sidebar first.")
    st.stop()

df = st.session_state["df_cleaned"]

# Initialize pipeline state
if "pipeline_steps" not in st.session_state:
    st.session_state["pipeline_steps"] = []

if "pipeline_name" not in st.session_state:
    st.session_state["pipeline_name"] = "My Data Pipeline"

tab_build, tab_run, tab_templates, tab_export = st.tabs([
    "🏗️ Build", "▶️ Run", "📋 Templates", "📤 Export"
])

with tab_build:
    st.markdown("### 🏗️ Build Your Pipeline")
    
    pipeline_name = st.text_input("Pipeline Name", st.session_state["pipeline_name"], key="pipe_name")
    st.session_state["pipeline_name"] = pipeline_name
    
    # Available steps
    step_types = {
        "🔍 Filter Rows": {
            "desc": "Filter rows by condition",
            "category": "Transform",
            "params": ["column", "condition", "value"]
        },
        "🗑️ Drop Columns": {
            "desc": "Remove specified columns",
            "category": "Transform",
            "params": ["columns"]
        },
        "🕳️ Fill Missing": {
            "desc": "Impute missing values",
            "category": "Cleaning",
            "params": ["column", "method"]
        },
        "♻️ Drop Duplicates": {
            "desc": "Remove duplicate rows",
            "category": "Cleaning",
            "params": ["subset"]
        },
        "📊 Rename Column": {
            "desc": "Rename a column",
            "category": "Transform",
            "params": ["old_name", "new_name"]
        },
        "🔢 Type Cast": {
            "desc": "Change column data type",
            "category": "Transform",
            "params": ["column", "new_type"]
        },
        "📐 Scale Column": {
            "desc": "Normalize or standardize a numeric column",
            "category": "Engineering",
            "params": ["column", "method"]
        },
        "🔤 Encode Categorical": {
            "desc": "Label encode or one-hot encode",
            "category": "Engineering",
            "params": ["column", "method"]
        },
        "🎯 Remove Outliers": {
            "desc": "Remove outliers using IQR method",
            "category": "Cleaning",
            "params": ["column", "method", "threshold"]
        },
        "📋 Sort By": {
            "desc": "Sort by one or more columns",
            "category": "Transform",
            "params": ["column", "ascending"]
        },
        "🔗 Create Column": {
            "desc": "Create new column from formula",
            "category": "Engineering",
            "params": ["name", "formula"]
        },
        "🔢 Round Column": {
            "desc": "Round numeric column values",
            "category": "Transform",
            "params": ["column", "decimals"]
        },
    }
    
    st.markdown("#### Add a Step")
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_step = st.selectbox("Step type", list(step_types.keys()), key="add_step_type")
    with c2:
        st.info(f"**{step_types[selected_step]['desc']}** — Category: {step_types[selected_step]['category']}")
    
    # Step configuration
    step_config = {"type": selected_step, "category": step_types[selected_step]["category"]}
    
    if selected_step == "🔍 Filter Rows":
        col = st.selectbox("Column", df.columns.tolist(), key="filter_col")
        condition = st.selectbox("Condition", [">", "<", ">=", "<=", "==", "!=", "contains", "not contains"], key="filter_cond")
        value = st.text_input("Value", key="filter_val")
        step_config["config"] = {"column": col, "condition": condition, "value": value}
        
    elif selected_step == "🗑️ Drop Columns":
        cols = st.multiselect("Columns to drop", df.columns.tolist(), key="drop_cols")
        step_config["config"] = {"columns": cols}
        
    elif selected_step == "🕳️ Fill Missing":
        col = st.selectbox("Column", df.columns.tolist(), key="fill_col")
        method = st.selectbox("Method", ["mean", "median", "mode", "constant", "forward_fill", "backward_fill"], key="fill_method")
        fill_value = st.text_input("Constant value (if method='constant')", key="fill_value")
        step_config["config"] = {"column": col, "method": method, "fill_value": fill_value}
        
    elif selected_step == "♻️ Drop Duplicates":
        subset = st.multiselect("Check columns (empty = all)", df.columns.tolist(), key="dup_subset")
        step_config["config"] = {"subset": subset}
        
    elif selected_step == "📊 Rename Column":
        old_name = st.selectbox("Current name", df.columns.tolist(), key="rename_old")
        new_name = st.text_input("New name", key="rename_new")
        step_config["config"] = {"old_name": old_name, "new_name": new_name}
        
    elif selected_step == "🔢 Type Cast":
        col = st.selectbox("Column", df.columns.tolist(), key="cast_col")
        new_type = st.selectbox("New type", ["int", "float", "str", "category", "datetime"], key="cast_type")
        step_config["config"] = {"column": col, "new_type": new_type}
        
    elif selected_step == "📐 Scale Column":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        col = st.selectbox("Column", num_cols if num_cols else ["No numeric columns"], key="scale_col")
        method = st.selectbox("Method", ["minmax", "standard", "robust", "log"], key="scale_method")
        step_config["config"] = {"column": col, "method": method}
        
    elif selected_step == "🔤 Encode Categorical":
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        col = st.selectbox("Column", cat_cols if cat_cols else ["No categorical columns"], key="encode_col")
        method = st.selectbox("Method", ["label", "one_hot"], key="encode_method")
        step_config["config"] = {"column": col, "method": method}
        
    elif selected_step == "🎯 Remove Outliers":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        col = st.selectbox("Column", num_cols if num_cols else ["No numeric columns"], key="outlier_col")
        method = st.selectbox("Method", ["iqr", "zscore"], key="outlier_method")
        threshold = st.number_input("Threshold", value=1.5 if method == "iqr" else 3.0, key="outlier_thresh")
        step_config["config"] = {"column": col, "method": method, "threshold": threshold}
        
    elif selected_step == "📋 Sort By":
        col = st.selectbox("Column", df.columns.tolist(), key="sort_col")
        ascending = st.checkbox("Ascending", value=True, key="sort_asc")
        step_config["config"] = {"column": col, "ascending": ascending}
        
    elif selected_step == "🔗 Create Column":
        name = st.text_input("New column name", key="create_col_name")
        existing_cols = df.columns.tolist()
        formula = st.text_area("Formula (use pandas expressions, e.g., df['col1'] * df['col2'])", key="create_formula")
        step_config["config"] = {"name": name, "formula": formula}
        
    elif selected_step == "🔢 Round Column":
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        col = st.selectbox("Column", num_cols if num_cols else ["No numeric columns"], key="round_col")
        decimals = st.number_input("Decimal places", min_value=0, max_value=10, value=2, key="round_dec")
        step_config["config"] = {"column": col, "decimals": decimals}
    
    if st.button("➕ Add Step to Pipeline"):
        st.session_state["pipeline_steps"].append(step_config)
        st.success(f"✅ Added: {selected_step}")
        st.rerun()
    
    # Show current pipeline
    if st.session_state["pipeline_steps"]:
        st.markdown("---")
        st.markdown(f"### 📋 Pipeline: {pipeline_name} ({len(st.session_state['pipeline_steps'])} steps)")
        
        for i, step in enumerate(st.session_state["pipeline_steps"]):
            c1, c2, c3 = st.columns([0.05, 0.85, 0.1])
            with c1:
                st.markdown(f"**{i+1}**")
            with c2:
                config_str = " | ".join([f"{k}: {v}" for k, v in step.get("config", {}).items()])
                cat_tag = step.get("category", "")
                st.markdown(f"**{step['type']}** — `{config_str}` <span style='background:rgba(108,99,255,0.15); color:#6C63FF; padding:2px 8px; border-radius:8px; font-size:0.7rem;'>{cat_tag}</span>", unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_step_{i}"):
                    st.session_state["pipeline_steps"].pop(i)
                    st.rerun()
            
            if i < len(st.session_state["pipeline_steps"]) - 1:
                st.markdown("<div style='text-align:center; color:#6C63FF;'>⬇️</div>", unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All Steps"):
            st.session_state["pipeline_steps"] = []
            st.rerun()
    else:
        st.info("Pipeline is empty. Add steps above to build your data pipeline.")

with tab_run:
    st.markdown("### ▶️ Run Pipeline")
    
    if not st.session_state["pipeline_steps"]:
        st.warning("No pipeline steps configured. Go to the Build tab first.")
    else:
        st.markdown(f"**Pipeline:** {st.session_state['pipeline_name']} — {len(st.session_state['pipeline_steps'])} steps")
        
        if st.button("▶️ Execute Pipeline", key="run_pipeline"):
            result_df = df.copy()
            execution_log = []
            
            progress = st.progress(0, text="Starting pipeline...")
            
            for i, step in enumerate(st.session_state["pipeline_steps"]):
                step_name = step["type"]
                config = step.get("config", {})
                rows_before = len(result_df)
                
                try:
                    if step_name == "🔍 Filter Rows":
                        col, cond, val = config["column"], config["condition"], config["value"]
                        try: val = float(val)
                        except: pass
                        if cond == ">": result_df = result_df[result_df[col] > val]
                        elif cond == "<": result_df = result_df[result_df[col] < val]
                        elif cond == ">=": result_df = result_df[result_df[col] >= val]
                        elif cond == "<=": result_df = result_df[result_df[col] <= val]
                        elif cond == "==": result_df = result_df[result_df[col] == val]
                        elif cond == "!=": result_df = result_df[result_df[col] != val]
                        elif cond == "contains": result_df = result_df[result_df[col].astype(str).str.contains(str(val))]
                        elif cond == "not contains": result_df = result_df[~result_df[col].astype(str).str.contains(str(val))]
                    
                    elif step_name == "🗑️ Drop Columns":
                        result_df = result_df.drop(columns=config["columns"], errors="ignore")
                    
                    elif step_name == "🕳️ Fill Missing":
                        col, method = config["column"], config["method"]
                        if method == "mean": result_df[col] = result_df[col].fillna(result_df[col].mean())
                        elif method == "median": result_df[col] = result_df[col].fillna(result_df[col].median())
                        elif method == "mode": result_df[col] = result_df[col].fillna(result_df[col].mode().iloc[0])
                        elif method == "constant": result_df[col] = result_df[col].fillna(config.get("fill_value", ""))
                        elif method == "forward_fill": result_df[col] = result_df[col].ffill()
                        elif method == "backward_fill": result_df[col] = result_df[col].bfill()
                    
                    elif step_name == "♻️ Drop Duplicates":
                        subset = config.get("subset", None) or None
                        result_df = result_df.drop_duplicates(subset=subset)
                    
                    elif step_name == "📊 Rename Column":
                        result_df = result_df.rename(columns={config["old_name"]: config["new_name"]})
                    
                    elif step_name == "🔢 Type Cast":
                        col, new_type = config["column"], config["new_type"]
                        type_map = {"int": "int64", "float": "float64", "str": "object", "category": "category"}
                        if new_type == "datetime":
                            result_df[col] = pd.to_datetime(result_df[col], errors="coerce")
                        else:
                            result_df[col] = result_df[col].astype(type_map[new_type], errors="ignore")
                    
                    elif step_name == "📐 Scale Column":
                        col, method = config["column"], config["method"]
                        if method == "minmax":
                            result_df[col] = (result_df[col] - result_df[col].min()) / (result_df[col].max() - result_df[col].min())
                        elif method == "standard":
                            result_df[col] = (result_df[col] - result_df[col].mean()) / result_df[col].std()
                        elif method == "robust":
                            q1, q3 = result_df[col].quantile(0.25), result_df[col].quantile(0.75)
                            result_df[col] = (result_df[col] - q1) / (q3 - q1)
                        elif method == "log":
                            result_df[col] = np.log1p(result_df[col].clip(lower=0))
                    
                    elif step_name == "🔤 Encode Categorical":
                        col, method = config["column"], config["method"]
                        if method == "label":
                            result_df[col] = result_df[col].astype('category').cat.codes
                        elif method == "one_hot":
                            result_df = pd.get_dummies(result_df, columns=[col], drop_first=True)
                    
                    elif step_name == "🎯 Remove Outliers":
                        col = config["column"]
                        method, threshold = config["method"], config["threshold"]
                        if method == "iqr":
                            q1, q3 = result_df[col].quantile(0.25), result_df[col].quantile(0.75)
                            iqr = q3 - q1
                            result_df = result_df[(result_df[col] >= q1 - threshold * iqr) & (result_df[col] <= q3 + threshold * iqr)]
                        elif method == "zscore":
                            z = (result_df[col] - result_df[col].mean()) / result_df[col].std()
                            result_df = result_df[z.abs() <= threshold]
                    
                    elif step_name == "📋 Sort By":
                        result_df = result_df.sort_values(config["column"], ascending=config["ascending"])
                    
                    elif step_name == "🔗 Create Column":
                        result_df[config["name"]] = eval(config["formula"], {"df": result_df, "pd": pd, "np": np})
                    
                    elif step_name == "🔢 Round Column":
                        result_df[config["column"]] = result_df[config["column"]].round(config["decimals"])
                    
                    rows_after = len(result_df)
                    execution_log.append({
                        "Step": f"{i+1}. {step_name}",
                        "Status": "✅ Success",
                        "Rows": f"{rows_before} → {rows_after}",
                        "Delta": rows_after - rows_before,
                    })
                    
                except Exception as e:
                    execution_log.append({
                        "Step": f"{i+1}. {step_name}",
                        "Status": f"❌ Error: {str(e)[:50]}",
                        "Rows": f"{rows_before} → ?",
                        "Delta": "Error",
                    })
                
                progress.progress((i + 1) / len(st.session_state["pipeline_steps"]), 
                                 text=f"Step {i+1}/{len(st.session_state['pipeline_steps'])}: {step_name}")
            
            st.success("✅ Pipeline execution complete!")
            
            st.markdown("#### Execution Log")
            st.dataframe(pd.DataFrame(execution_log), use_container_width=True, hide_index=True)
            
            st.markdown("#### Result Preview")
            st.dataframe(result_df.head(20), use_container_width=True)
            st.metric("Final Shape", f"{result_df.shape[0]:,} rows × {result_df.shape[1]} columns")
            
            if st.button("💾 Apply Pipeline Result"):
                st.session_state["df_cleaned"] = result_df
                st.success("Pipeline result applied to your working dataset!")

with tab_templates:
    st.markdown("### 📋 Pipeline Templates")
    st.caption("Start with a template and customize it to your needs.")
    
    templates = {
        "🧹 Basic Data Cleaning": [
            {"type": "🕳️ Fill Missing", "category": "Cleaning", "config": {"column": "auto_detect", "method": "median"}},
            {"type": "♻️ Drop Duplicates", "category": "Cleaning", "config": {"subset": []}},
            {"type": "🎯 Remove Outliers", "category": "Cleaning", "config": {"column": "auto", "method": "iqr", "threshold": 1.5}},
        ],
        "📊 Data Preparation for ML": [
            {"type": "🕳️ Fill Missing", "category": "Cleaning", "config": {"column": "auto_detect", "method": "median"}},
            {"type": "🔤 Encode Categorical", "category": "Engineering", "config": {"column": "auto", "method": "label"}},
            {"type": "📐 Scale Column", "category": "Engineering", "config": {"column": "auto", "method": "standard"}},
        ],
        "🔍 EDA Quick Clean": [
            {"type": "♻️ Drop Duplicates", "category": "Cleaning", "config": {"subset": []}},
            {"type": "🕳️ Fill Missing", "category": "Cleaning", "config": {"column": "auto_detect", "method": "forward_fill"}},
            {"type": "📋 Sort By", "category": "Transform", "config": {"column": "auto", "ascending": True}},
        ],
        "🏭 Feature Engineering Pipeline": [
            {"type": "🕳️ Fill Missing", "category": "Cleaning", "config": {"column": "auto_detect", "method": "median"}},
            {"type": "📐 Scale Column", "category": "Engineering", "config": {"column": "auto", "method": "standard"}},
            {"type": "🔤 Encode Categorical", "category": "Engineering", "config": {"column": "auto", "method": "one_hot"}},
            {"type": "🔗 Create Column", "category": "Engineering", "config": {"name": "feature_interaction", "formula": "df[col1] * df[col2]"}},
        ],
    }
    
    for name, steps in templates.items():
        with st.expander(name):
            st.markdown(f"**{len(steps)} steps:**")
            for i, step in enumerate(steps):
                st.markdown(f"{i+1}. {step['type']} — {step['config']}")
            if st.button(f"📋 Use Template", key=f"template_{name}"):
                st.session_state["pipeline_steps"] = steps.copy()
                st.session_state["pipeline_name"] = name
                st.success(f"✅ Template loaded! Go to Build tab to customize.")
                st.rerun()

with tab_export:
    st.markdown("### 📤 Export Pipeline")
    
    if not st.session_state["pipeline_steps"]:
        st.warning("No pipeline steps to export.")
    else:
        # Export as JSON
        pipeline_data = {
            "name": st.session_state["pipeline_name"],
            "version": "DataScience Flow v9.5",
            "platform": "HMG Academy | HMG Concepts",
            "created": datetime.now().isoformat(),
            "steps": st.session_state["pipeline_steps"],
            "source_shape": list(df.shape),
        }
        
        pipeline_json = json.dumps(pipeline_data, indent=2, default=str)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "📥 Download Pipeline (JSON)",
                pipeline_json,
                f"{st.session_state['pipeline_name'].replace(' ', '_')}_pipeline.json",
                "application/json"
            )
        with c2:
            # Generate Python script
            py_lines = [
                f'# Pipeline: {st.session_state["pipeline_name"]}',
                '# Generated by DataScience Flow v9.5 — HMG Academy',
                '# Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts',
                'import pandas as pd',
                'import numpy as np',
                '',
                f'df = pd.read_csv("your_data.csv")  # Load your data',
                '',
            ]
            for i, step in enumerate(st.session_state["pipeline_steps"]):
                py_lines.append(f'# Step {i+1}: {step["type"]}')
                config = step.get("config", {})
                if step["type"] == "🔍 Filter Rows":
                    py_lines.append(f'df = df[df["{config.get("column","")}"] {config.get("condition",">")} {config.get("value","")}]')
                elif step["type"] == "🗑️ Drop Columns":
                    py_lines.append(f'df = df.drop(columns={config.get("columns",[])})')
                elif step["type"] == "🕳️ Fill Missing":
                    py_lines.append(f'df["{config.get("column","")}"] = df["{config.get("column","")}"].fillna(df["{config.get("column","")}"].{config.get("method","mean")}())')
                elif step["type"] == "♻️ Drop Duplicates":
                    py_lines.append(f'df = df.drop_duplicates()')
                elif step["type"] == "📐 Scale Column":
                    py_lines.append(f'from sklearn.preprocessing import StandardScaler')
                    py_lines.append(f'scaler = StandardScaler()')
                    py_lines.append(f'df["{config.get("column","")}_scaled"] = scaler.fit_transform(df[["{config.get("column","")}"]])')
                elif step["type"] == "🔤 Encode Categorical":
                    py_lines.append(f'df = pd.get_dummies(df, columns=["{config.get("column","")}"])')
                else:
                    py_lines.append(f'# {step["type"]} - customize this step')
                py_lines.append('')
            
            py_lines.append('print(f"Final shape: {df.shape}")')
            py_lines.append('df.to_csv("output.csv", index=False)')
            
            py_script = '\n'.join(py_lines)
            st.download_button(
                "🐍 Download as Python Script",
                py_script,
                f"{st.session_state['pipeline_name'].replace(' ', '_')}_pipeline.py",
                "text/x-python"
            )
        
        with st.expander("📋 View Pipeline JSON"):
            st.code(pipeline_json, language="json")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Data pipelines are the backbone of reproducible data science. A well-built pipeline 
ensures that your data transformations are consistent, auditable, and repeatable. Always version your 
pipelines and test them on small samples before running on full datasets.

📚 **Next Steps:** Use Module 52 (Dashboard Builder) to create visual dashboards from your pipeline output.
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
