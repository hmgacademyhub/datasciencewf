# DataScience Flow v10.0 (V3)

**76-Module Enterprise Data Science Workflow Platform**

Part of **HMG Academy** Ecosystem — Subsidiary of **HMG Concepts** (est. 2015)

Built by **Adewale Samson Adeagbo** — Data Scientist | EdTech Builder | AI-Augmented Solutions Developer

---

## Overview

DataScience Flow v10.0 is a comprehensive, browser-based data science workflow platform built on Streamlit. It covers **every stage** of the data science lifecycle with **76 fully functional modules** — from data collection to governance. **100% free tools, no AI API required.**

### Founding Vision: "His Marvellous Grace"

HMG Concepts was founded in 2015 on the conviction that quality education and technology should be accessible to every Nigerian student and professional. DataScience Flow embodies this vision — a world-class data science platform that costs ₦0 to start, requires no paid APIs, and is aligned with Nigeria's 3MTT programme and university curricula.

---

## 76 Modules — Complete Data Science Workflow

| Stage | Modules | Description |
|-------|---------|-------------|
| 📥 Collection | 01-05 | Data ingestion, simulation, web connectors, sampling |
| 🧹 Prep | 06-12 | Exploration, missing values, duplicates, outliers, quality, validation |
| 📊 EDA | 13-18 | Statistics, visualisation, advanced charts, profiling, correlation, diff |
| 📐 Statistics | 19-20 | Hypothesis testing, AB testing calculator |
| 🔄 Transform | 21-22 | Data merging, transformation |
| ⚙️ Engineering | 23-25 | Feature engineering, selection, dimensionality reduction |
| 🤖 ML | 26-30 | Baseline, class imbalance, comparison, explainability, hyperparameters |
| 📈 Analysis | 31-36 | Time series, text, geospatial, search, what-if, SQL |
| 🔐 Security | 37, 74 | Privacy & masking, audit trail viewer |
| ⚖️ Governance | 38-41 | Contracts, compliance, retention, lineage |
| 🔔 Operations | 42-43, 68, 70 | Monitoring, disaster recovery, anomaly detection, workflow scheduler |
| 📤 Export | 44 | Multi-format export |
| 📝 Reporting | 45-47 | Storytelling, reports, audit reports |
| 🏢 Enterprise | 48-52, 65, 71-73, 76 | KPIs, collaboration, API docs, pipelines, dashboards, data catalog, feature store, model registry, data factory |
| 🎓 Education | 53-64, 75 | Learning hub, notebooks, deployment, journal, curriculum, challenges, achievements, certificates |

### V3 New Modules (62-76)
- **62 Curriculum Tracker** — 3MTT/LASU-aligned structured learning paths with progress tracking
- **63 Code Challenges** — Interactive Python exercises by beginner/intermediate/advanced level
- **64 Achievement System** — Gamified learning with badges, milestones, and progress
- **65 Data Catalog** — Centralized metadata registry with business context and tags
- **66 Causal Inference** — DAG builder, treatment effect estimation, methods guide
- **67 Network Analysis** — Graph analysis with centrality, communities, and visualization
- **68 Anomaly Detection Dashboard** — Multi-method anomaly detection (IQR, Z-Score, Isolation Forest)
- **69 Survival Analysis** — Time-to-event analysis with Kaplan-Meier estimation
- **70 Workflow Scheduler** — Task scheduling with dependencies and templates
- **71 Feature Store** — Centralized ML feature management with documentation
- **72 Cost Estimator** — ML project cost/ROI calculator, free vs paid tools comparison
- **73 Model Registry** — Model versioning, approval workflows, deployment status
- **74 Audit Trail Viewer** — Complete audit log with search and export
- **75 Certificate Generator** — HMG Academy certificates with verification codes
- **76 Data Factory** — End-to-end production pipeline with quality gates and SLAs

---

## HMG Academy Ecosystem

| Entity | Role | URL |
|--------|------|-----|
| 🏢 HMG Concepts | Parent company (est. 2015) | [hmgconcepts.pages.dev](https://hmgconcepts.pages.dev) |
| 🎓 HMG Academy | Education & training arm | [hmgacademy.pages.dev](https://hmgacademy.pages.dev) |
| 💻 HMG Technologies | Innovation & tools arm | [hmgtechnologies.pages.dev](https://hmgtechnologies.pages.dev) |
| 📢 HMG Media | Content & visibility arm | [hmgmedia.pages.dev](https://hmgmedia.pages.dev) |
| ✝️ HMG Gospel | Faith & outreach arm | [hmggospel.pages.dev](https://hmggospel.pages.dev) |

---

## Security Features

- **HMAC-SHA256 Token Verification** — Tamper-proof session tokens
- **Email Reuse Prevention** — 24-hour cooldown per email
- **Rate Limiting** — 60 actions/min, 30 exports/hour
- **Input Sanitisation** — XSS, SQL injection, HTML, URL, email, path traversal
- **Threat Detection** — Automatic detection and scoring of suspicious inputs
- **Login Lockout** — 5 failed attempts = 15-minute lockout
- **CAPTCHA-like Challenge** — Simple math verification
- **Session Fingerprinting** — Detect session tampering
- **Audit Trail** — Every action logged with timestamp and metadata
- **Export Watermarking** — All exports contain HMG Academy branding
- **Proprietary License** — Anti-forking protection

---

## Deployment Steps

### Streamlit Community Cloud (Free — Recommended)

**Step 1: Prepare Your GitHub Repository**
```bash
# Navigate to the project folder
cd "DSFlow V3"

# Initialize git
git init
git add .
git commit -m "DataScience Flow v10.0 — Initial commit"

# Create repo on GitHub (use GitHub web UI)
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/datascienceflow-studio.git
git branch -M main
git push -u origin main
```

**Step 2: Configure GitHub Security**
1. Go to your repo → Settings → General
2. Under "Danger Zone", **uncheck** "Allow forks"
3. Ensure repository is **Public** (required for free Streamlit Cloud)

**Step 3: Deploy on Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository and branch (`main`)
4. Set **Main file path** to `app.py`
5. Click **"Advanced settings..."**
6. Add these secrets:
```toml
DSFLOW_SALT = "your-random-secure-salt-here-at-least-32-characters-long"
```
Optional (for Supabase auth):
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key-here"
```
7. Click **"Deploy"**
8. Wait 2-3 minutes for deployment to complete
9. Visit your app URL (e.g., `https://datascienceflow-hmgacademy.streamlit.app`)

**Step 4: Verify Deployment**
- [ ] App loads with "DataScience Flow" heading
- [ ] 76 modules appear in the sidebar
- [ ] Subscription flow works (start free trial)
- [ ] Upload a CSV file successfully
- [ ] Navigate between modules
- [ ] Generate a Jupyter notebook (.ipynb)
- [ ] Export data works (CSV, Excel)
- [ ] Security badge shows "🔒 Secured"

### Docker Deployment
```bash
# Build image
docker build -t datascienceflow:v10.0 .

# Run container
docker run -d \
  --name dsflow \
  -p 8501:8501 \
  -e DSFLOW_SALT=your-secure-salt-min-32-chars \
  datascienceflow:v10.0

# Verify
docker ps
curl http://localhost:8501/_stcore/health
```

### HuggingFace Spaces
1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space)
2. Select **Streamlit** as the SDK
3. Upload all files from this folder
4. Set `DSFLOW_SALT` in Space secrets (Settings → Repository secrets)
5. Space auto-builds and deploys

---

## Tech Stack (100% Free)

| Component | Technology | Cost |
|-----------|-----------|------|
| Framework | Streamlit 1.32+ | Free |
| Data | Pandas, NumPy | Free |
| ML | Scikit-learn, Imbalanced-learn | Free |
| SQL | DuckDB (in-memory) | Free |
| Viz | Plotly, Matplotlib, Seaborn | Free |
| Profiling | Sweetviz | Free |
| Geo | Folium | Free |
| NLP | NLTK, TextBlob | Free |
| Network | NetworkX | Free |
| Survival | Lifelines | Free |
| Security | HMAC-SHA256 | Free |
| Notebook | nbformat | Free |
| AI API | **None — 100% rule-based** | **₦0** |

---

## Builder

**Adewale Samson Adeagbo**
- 🎓 B.Sc.(Ed) Computer Science Education (LASU, 2023)
- 📊 3MTT Data Science Fellow (2025)
- 🏗️ Founder, HMG Concepts (est. 2015) — "His Marvellous Grace"
- 🔗 [Portfolio](https://cssadewale.pages.dev) · [GitHub](https://github.com/cssadewale) · [LinkedIn](https://linkedin.com/in/adewalesamsonadeagbo)
- 📧 adeagboadewalesamson@gmail.com · 📞 +234 810 086 6322 · 📍 Lagos, Nigeria

---

## License

**Proprietary License** — Copyright © 2015-2026 HMG Concepts. All Rights Reserved.

Unauthorized copying, distribution, modification, reverse engineering, or forking is strictly prohibited.

---

*DataScience Flow v10.0 — HMG Academy Ecosystem — HMG Concepts (est. 2015) — His Marvellous Grace*
