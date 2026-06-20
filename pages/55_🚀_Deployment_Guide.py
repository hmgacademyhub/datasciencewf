"""
Module 55: Deployment Guide — DataScience Flow v9.5
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


st.set_page_config(page_title="Deployment Guide | DataScience Flow", page_icon="🚀", layout="wide")


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
## 🚀 Deployment Guide — Module 55

> **What is Model/App Deployment?** Deployment is the process of taking your trained model or data application 
> from your local machine and making it accessible to users over the internet. A model that stays on your 
> laptop helps nobody — deployment turns analysis into impact.

### 🎓 Why Deployment Matters
- **From notebook to production**: The gap between "works on my machine" and "works for everyone"
- **Real-world impact**: Models only create value when people can use them
- **Scalability**: Production systems handle multiple users, data streams, and edge cases
- **Monitoring**: Deployed systems can be monitored for drift and performance

### 📐 Deployment Options (Free!)
| Platform | Cost | Best For | Limitations |
|----------|------|----------|-------------|
| Streamlit Cloud | Free | Streamlit apps | 1GB RAM, public repos |
| Hugging Face Spaces | Free | ML demos | Limited compute |
| Render | Free tier | Web apps | Sleeps after inactivity |
| Railway | Free trial | Full-stack | Limited hours |
| PythonAnywhere | Free tier | Simple apps | Limited CPU |
| Docker + VPS | ~$5/mo | Full control | Requires DevOps |

### 🇳🇬 Nigerian Developer Tips
- **Internet reliability**: Design for slow/intermittent connections
- **Mobile-first**: Most Nigerian users access via phones
- **Cost discipline**: Free tiers are sufficient for most use cases
- **Local hosting**: Consider local VPS providers for lower latency
""")

tab_streamlit, tab_fastapi, tab_docker, tab_checklist = st.tabs([
    "📊 Streamlit Cloud", "⚡ FastAPI", "🐳 Docker", "✅ Checklist"
])

with tab_streamlit:
    st.markdown("""
    ### 📊 Deploy to Streamlit Community Cloud (FREE)
    
    **Streamlit Community Cloud** is the easiest way to deploy Streamlit apps — completely free.
    
    #### Step-by-Step Instructions:
    
    1. **Prepare your GitHub repository**
       ```bash
       # Create repo on github.com (must be public for free tier)
       # Push your code
       git init
       git add .
       git commit -m "Initial commit"
       git branch -M main
       git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
       git push -u origin main
       ```
    
    2. **Verify requirements.txt**
       - Ensure all Python packages are listed
       - Pin versions for reproducibility: `streamlit>=1.32.0`
    
    3. **Deploy**
       - Go to [share.streamlit.io](https://share.streamlit.io/)
       - Sign in with GitHub
       - Click "New app"
       - Select your repository, branch (main), and main file (app.py)
       - Click "Deploy"
    
    4. **Configure secrets (optional)**
       - In app settings → Secrets
       - Add API keys and credentials
    
    5. **Your app is live!**
       - URL: `https://YOUR_REPO-YOUR_USERNAME.streamlit.app`
       - Share with anyone, access from anywhere
    
    #### ⚠️ Common Issues:
    - **App won't start**: Check `requirements.txt` for missing packages
    - **Memory error**: Free tier has 1GB RAM limit
    - **Slow cold start**: First load after inactivity takes 30-60 seconds
    - **Package not found**: Some packages need system-level dependencies
    """)

with tab_fastapi:
    st.markdown("""
    ### ⚡ Deploy ML Models with FastAPI
    
    **FastAPI** is the best way to deploy ML models as REST APIs. Here's how:
    
    #### Step 1: Create the API
    
    ```python
    # main.py
    from fastapi import FastAPI
    from pydantic import BaseModel
    import joblib
    import pandas as pd
    
    app = FastAPI(title="My ML API", version="1.0")
    model = joblib.load("model.pkl")
    
    class PredictionInput(BaseModel):
        feature1: float
        feature2: float
        feature3: float
    
    class PredictionOutput(BaseModel):
        prediction: float
        probability: float
    
    @app.get("/")
    def root():
        return {"message": "ML API is running!"}
    
    @app.post("/predict", response_model=PredictionOutput)
    def predict(input_data: PredictionInput):
        df = pd.DataFrame([input_data.dict()])
        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0][1] if hasattr(model, 'predict_proba') else None
        return PredictionOutput(prediction=prediction, probability=probability)
    ```
    
    #### Step 2: Create requirements.txt
    ```
    fastapi>=0.104.0
    uvicorn>=0.24.0
    scikit-learn>=1.4.0
    pandas>=2.0.0
    joblib>=1.3.0
    pydantic>=2.0.0
    ```
    
    #### Step 3: Deploy to Render (Free)
    1. Create account at [render.com](https://render.com)
    2. New Web Service → Connect GitHub repo
    3. Build command: `pip install -r requirements.txt`
    4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    5. Select free instance → Deploy
    
    #### Step 4: Test the API
    ```bash
    # Test locally
    curl http://localhost:8000/
    curl -X POST http://localhost:8000/predict \\
         -H "Content-Type: application/json" \\
         -d '{"feature1": 1.0, "feature2": 2.0, "feature3": 3.0}'
    ```
    """)

with tab_docker:
    st.markdown("""
    ### 🐳 Deploy with Docker
    
    Docker ensures your app runs consistently across all environments.
    
    #### Dockerfile
    ```dockerfile
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # System dependencies
    RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
    
    # Python dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Application code
    COPY . .
    
    # Streamlit specific
    EXPOSE 8501
    HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
    
    ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    ```
    
    #### Docker Compose (for multi-service)
    ```yaml
    version: '3.8'
    services:
      streamlit:
        build: .
        ports:
          - "8501:8501"
        volumes:
          - .:/app
        environment:
          - SUPABASE_URL=\${SUPABASE_URL}
          - SUPABASE_ANON_KEY=\${SUPABASE_ANON_KEY}
      
      fastapi:
        build: ./api
        ports:
          - "8000:8000"
        command: uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    
    #### Deploy Commands
    ```bash
    # Build
    docker build -t datascienceflow:v9.0 .
    
    # Run locally
    docker run -p 8501:8501 datascienceflow:v9.0
    
    # Push to registry
    docker tag datascienceflow:v9.0 YOUR_REGISTRY/datascienceflow:v9.0
    docker push YOUR_REGISTRY/datascienceflow:v9.0
    ```
    """)

with tab_checklist:
    st.markdown("""
    ### ✅ Pre-Deployment Checklist
    
    Use this checklist before deploying any data application:
    """)
    
    checks = {
        "📦 Code Quality": [
            "All code runs without errors locally",
            "requirements.txt is complete and accurate",
            "No hardcoded secrets or API keys",
            "Error handling for all user inputs",
            "No print() statements — use logging instead",
        ],
        "🔒 Security": [
            "Secrets stored in environment variables or secrets manager",
            ".gitignore excludes sensitive files",
            "CORS configured appropriately",
            "Input validation on all user-provided data",
            "No SQL injection vulnerabilities in queries",
        ],
        "📊 Data Handling": [
            "Large datasets handled efficiently (chunking, sampling)",
            "Memory usage within platform limits",
            "File upload size limits configured",
            "Data export tested for all formats",
            "Session state managed properly",
        ],
        "🧪 Testing": [
            "Tested with multiple datasets and sizes",
            "Edge cases handled (empty data, single row, all nulls)",
            "Mobile responsive tested",
            "Browser compatibility verified (Chrome, Firefox, Safari)",
            "Performance tested with concurrent users",
        ],
        "📝 Documentation": [
            "README.md is complete with setup instructions",
            "All features documented",
            "Deployment guide included",
            "Known limitations listed",
            "Contact information provided",
        ],
    }
    
    for category, items in checks.items():
        st.markdown(f"#### {category}")
        for item in items:
            checked = st.checkbox(item, key=f"check_{item[:30]}")
        st.markdown("---")

st.markdown("---")
st.markdown("""
💡 **Key Takeaway:** Deployment is not the end — it is the beginning. Monitor your deployed 
application for data drift, model performance degradation, and user feedback. Iteration never stops.

📚 **Next Steps:** After deployment, use Module 55 (Data Monitor & Alerts) to set up monitoring rules.
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
