"""
Module 54: Notebook Playground — DataScience Flow v9.5
Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts
"""
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Notebook Playground | DataScience Flow", page_icon="📓", layout="wide")


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
## 📓 Notebook Playground — Module 54

> **What is this?** The Notebook Playground lets you write and run Python code directly in the browser 
> using your loaded dataset. It is like a simplified Jupyter Notebook inside DataScience Flow.

### 🎓 Why a Code Playground?
- **Learn by doing**: The best way to learn data science is to write code
- **Extend the platform**: Not everything has a button — code gives you unlimited flexibility
- **Reproduce analyses**: Copy generated code snippets into your own scripts
- **Prototype quickly**: Test ideas before building them into your pipeline

### 📐 How to Use
1. Write Python code in the code editor below
2. Your loaded dataset is available as `df` (original) and `df_cleaned` (cleaned)
3. Common libraries are pre-imported: `pandas as pd`, `numpy as np`, `plotly.express as px`
4. Run the code and see results instantly
5. Copy the code for use in your own projects
""")

tab_playground, tab_snippets, tab_generated = st.tabs([
    "📝 Playground", "📋 Code Snippets", "🔄 Generated Code"
])

with tab_playground:
    st.markdown("### 📝 Interactive Code Playground")
    
    default_code = """# Your data is available as 'df' and 'df_cleaned'
# Try these examples:

# Show dataset info
print(f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Missing values: {df.isnull().sum().sum()}")

# Quick summary statistics
df.describe()
"""
    
    code = st.text_area("Python Code", value=default_code, height=300, key="notebook_code")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("▶️ Run Code", use_container_width=True):
            if st.session_state.get("df") is not None:
                df = st.session_state["df"]
                df_cleaned = st.session_state.get("df_cleaned", df)
                
                # Build namespace
                namespace = {
                    "df": df,
                    "df_cleaned": df_cleaned,
                    "pd": pd,
                    "np": np,
                }
                try:
                    import plotly.express as px
                    import matplotlib.pyplot as plt
                    namespace["px"] = px
                    namespace["plt"] = plt
                except ImportError:
                    pass
                
                # Capture output
                from io import StringIO
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                
                try:
                    exec(code, namespace)
                    output = mystdout.getvalue()
                    if output:
                        st.code(output, language="text")
                    
                    # Check for plotly figures
                    for key, val in namespace.items():
                        if key.startswith('_'):
                            continue
                        try:
                            import plotly.graph_objects as go
                            if isinstance(val, go.Figure):
                                st.plotly_chart(val, use_container_width=True)
                        except:
                            pass
                        
                        # Display DataFrames
                        if isinstance(val, pd.DataFrame) and key not in ['df', 'df_cleaned']:
                            st.dataframe(val, use_container_width=True)
                    
                    st.success("✅ Code executed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    sys.stdout = old_stdout
            else:
                st.warning("Load a dataset first!")
    
    with col2:
        st.caption("💡 Tip: Variable `df` = original data, `df_cleaned` = cleaned data. Use `px` for Plotly charts.")

with tab_snippets:
    st.markdown("### 📋 Useful Code Snippets")
    st.info("Copy these snippets and modify them for your needs.")
    
    snippets = {
        "📊 Quick EDA": """import pandas as pd
import numpy as np

# Quick EDA in one cell
print("Shape:", df.shape)
print("\\nData Types:")
print(df.dtypes)
print("\\nMissing Values:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("\\nSummary Statistics:")
print(df.describe())
""",

        "📈 Correlation Heatmap": """import plotly.express as px

# Correlation heatmap for numeric columns
numeric_df = df.select_dtypes(include=[np.number])
corr = numeric_df.corr()
fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                color_continuous_scale="RdBu_r", range_color=[-1, 1],
                title="Correlation Heatmap")
fig.show()
""",

        "🔍 Outlier Detection (IQR)": """# Detect outliers using IQR method
for col in df.select_dtypes(include=[np.number]).columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    print(f"{col}: {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)")
""",

        "🤖 Quick ML Pipeline": """from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from subscription import init_subscription_state, TIERS, tier_badge_html, get_tier_info, local_save_subscription

from security import (
    init_secure_session, verify_subscription_integrity,
    authenticate_subscription, check_rate_limit, check_export_limit,
    validate_upload, sanitise_string, sanitise_email,
    log_action, check_session_timeout,
    watermark_dataframe, BRAND_WATERMARK, BRAND_FOOTER,
)


# Quick classification pipeline (modify target_col)
target_col = 'target'  # Change this to your target column
feature_cols = [c for c in df.columns if c != target_col]

X = pd.get_dummies(df[feature_cols])
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
""",

        "📝 Text Preprocessing": """import re

# Basic text cleaning function
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z\\s]', '', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

# Apply to a text column (change column name)
text_col = 'text'  # Change this
df['cleaned_text'] = df[text_col].apply(clean_text)
print(df[[text_col, 'cleaned_text']].head(10))
""",

        "📤 Export Cleaned Data": """# Export cleaned dataset in multiple formats
df_cleaned = df_cleaned.dropna()  # or your preferred cleaning

# CSV
df_cleaned.to_csv('cleaned_data.csv', index=False)
print("CSV exported: cleaned_data.csv")

# Excel
df_cleaned.to_excel('cleaned_data.xlsx', index=False)
print("Excel exported: cleaned_data.xlsx")

# JSON
df_cleaned.to_json('cleaned_data.json', orient='records', indent=2)
print("JSON exported: cleaned_data.json")
""",
    }
    
    selected_snippet = st.selectbox("Select a snippet", list(snippets.keys()))
    st.code(snippets[selected_snippet], language="python")
    if st.button("📋 Load into Playground"):
        st.session_state["notebook_code"] = snippets[selected_snippet]
        st.info("Snippet loaded! Switch to the Playground tab to run it.")

with tab_generated:
    st.markdown("### 🔄 Code Generation from Operations")
    st.info("This module generates Python code equivalent to the operations you perform in DataScience Flow. Use this code to reproduce your analysis in scripts or notebooks.")
    
    if st.session_state.get("ent_audit_log"):
        log = st.session_state["ent_audit_log"]
        st.markdown("#### Operation History → Python Code")
        
        code_lines = [
            "# Generated by DataScience Flow v9.0",
            f"# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "import pandas as pd",
            "import numpy as np",
            "",
            "# Load data",
            f"# df = pd.read_csv('your_file.csv')",
        ]
        
        for entry in log[-20:]:  # Last 20 operations
            code_lines.append(f"# {entry['timestamp']}: {entry['action']} — {entry['detail']}")
        
        code_lines.extend([
            "",
            "# Note: This is a template. Customize the data loading and parameters for your use case.",
            "# The operations above were performed in the DataScience Flow interactive platform.",
        ])
        
        full_code = "\n".join(code_lines)
        st.code(full_code, language="python")
        
        st.download_button(
            "💾 Download as Python Script",
            data=full_code,
            file_name="dsflow_analysis.py",
            mime="text/x-python",
            use_container_width=True
        )
    else:
        st.info("Perform operations in the platform first, then return here to see generated code.")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** The Playground is your sandbox for experimentation. Use the code snippets as 
starting points, modify them for your data, and learn by doing. Every expert data scientist writes code daily.

📚 **Next Steps:** Use Module 54 (Deployment Guide) to deploy your custom scripts as applications.
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
