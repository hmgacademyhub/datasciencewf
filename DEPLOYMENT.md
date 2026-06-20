# 🚀 DataScience Flow v10.0 — Detailed Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option A: Streamlit Community Cloud](#option-a-streamlit-community-cloud)
3. [Option B: Docker](#option-b-docker)
4. [Option C: HuggingFace Spaces](#option-c-huggingface-spaces)
5. [Post-Deployment Security Checklist](#security-checklist)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:
- A **GitHub account** (free at github.com)
- The **DSFlow V3** folder with all 76+ files
- A modern web browser (Chrome, Firefox, Edge)
- Basic familiarity with terminal/command line (for Docker option)

---

## Option A: Streamlit Community Cloud (Free — Recommended)

This is the simplest and most cost-effective option. Streamlit provides free hosting for public repositories.

### Step 1: Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `datascienceflow-studio`
3. Description: `DataScience Flow v10.0 — 76-Module Enterprise Data Science Workflow Platform | HMG Academy`
4. Select **Public** (required for free Streamlit Cloud)
5. **Do NOT** check "Add a README file" (we have our own)
6. Click **Create repository**

### Step 2: Upload Files to GitHub

**Method 1: Using Git Command Line**
```bash
# Open terminal in the DSFlow V3 folder
cd "/path/to/DSFlow V3"

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "DataScience Flow v10.0 — 76 modules, security hardened, curriculum aligned"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/datascienceflow-studio.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Method 2: Using GitHub Web Upload**
1. Go to your new repository page
2. Click "Add file" → "Upload files"
3. Drag and drop ALL files from the DSFlow V3 folder
4. Add commit message and click "Commit changes"

### Step 3: Secure the Repository

1. Go to your repo → **Settings** → **General**
2. Scroll to "Danger Zone"
3. **Uncheck "Allow forks"** — This prevents others from forking your code
4. Ensure the repo stays **Public** (required for free Streamlit Cloud)

### Step 4: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** YOUR_USERNAME/datascienceflow-studio
   - **Branch:** main
   - **Main file path:** app.py
5. Click **"Advanced settings..."**
6. In the **Secrets** field, paste:
```toml
DSFLOW_SALT = "CHANGE_THIS_TO_A_RANDOM_STRING_AT_LEAST_32_CHARACTERS_LONG_EXAMPLE_hmg2025dsflow_salt_x9k2m"
```
7. Click **"Deploy"**
8. Wait 2-5 minutes for the first deployment

### Step 5: Get Your App URL

Your app will be available at:
`https://datascienceflow-studio-YOUR_USERNAME.streamlit.app`

Or you can customize the app name in Streamlit Cloud settings.

### Step 6: Verify Everything Works

Open your app URL and check:
- ✅ "DataScience Flow" heading appears
- ✅ 76 modules in the sidebar
- ✅ "Start Free Trial" button works
- ✅ File upload works (try a CSV)
- ✅ Navigate to a module page
- ✅ Generate a Jupyter notebook
- ✅ Security badge shows "🔒 Secured"

---

## Option B: Docker Deployment

For organizations that need more control.

### Step 1: Create Dockerfile

Create a file named `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV DSFLOW_SALT=CHANGE_THIS_SALT
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
```

### Step 2: Build and Run
```bash
# Build the Docker image
docker build -t datascienceflow:v10.0 .

# Run the container
docker run -d \
  --name dsflow \
  -p 8501:8501 \
  -e DSFLOW_SALT=your-secure-random-salt-32-chars \
  --restart unless-stopped \
  datascienceflow:v10.0

# Check logs
docker logs dsflow

# Stop
docker stop dsflow

# Restart
docker start dsflow
```

### Step 3: Using Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  dsflow:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DSFLOW_SALT=your-secure-salt-32-chars-minimum
    restart: unless-stopped
    healthcheck:
      test: curl --fail http://localhost:8501/_stcore/health || exit 1
      interval: 60s
      timeout: 10s
      retries: 3
```

Run with: `docker-compose up -d`

---

## Option C: HuggingFace Spaces

Free hosting with Streamlit support.

### Step 1: Create a Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Space name: `datascienceflow`
3. SDK: **Streamlit**
4. Visibility: **Public**
5. Click **Create Space**

### Step 2: Upload Files
1. Go to your Space → **Files and versions**
2. Click **"Add file"** → **"Upload files"**
3. Upload ALL files from DSFlow V3 folder
4. Commit

### Step 3: Configure Secrets
1. Go to **Settings** → **Repository secrets**
2. Add: `DSFLOW_SALT` = `your-secure-random-salt-32-chars`
3. The Space will auto-rebuild

---

## Security Checklist

After deployment, verify ALL of these:

- [ ] `DSFLOW_SALT` environment variable is set (minimum 32 characters)
- [ ] `.streamlit/secrets.toml` is NOT visible in the repo (check .gitignore)
- [ ] GitHub repo has **"Allow forks" disabled**
- [ ] `gatherUsageStats = false` in `.streamlit/config.toml`
- [ ] `enableXsrfProtection = true` in `.streamlit/config.toml`
- [ ] All 76 page modules load without errors
- [ ] Subscription gate works (unauthenticated users see landing page only)
- [ ] Rate limiting is active (test by rapidly clicking buttons)
- [ ] Session timeout works (wait 2+ hours, verify redirect to login)
- [ ] Export watermarks appear in downloaded files
- [ ] Notebook watermarks appear in generated .ipynb files
- [ ] Audit trail records actions (check Module 74)
- [ ] No sensitive data in repository (no .env files committed)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App shows "Streamlit" default page | Wait 2-3 min for deployment. If persists, check app.py is in root. |
| Module not found error | Ensure all 76 .py files are in `pages/` folder |
| Import error on security.py | Check security.py is in root, not in pages/ |
| Subscription gate blocks everything | The landing page should be visible; modules require auth |
| Rate limit errors | Normal after rapid clicking. Wait 60 seconds. |
| .ipynb generation fails | Ensure nbformat is in requirements.txt |
| CSS not loading | Streamlit Cloud serves CSS automatically from app.py |
| Large file upload fails | Streamlit Cloud has 200MB limit. Reduce file size. |
| App is slow | First load is slow; subsequent loads are faster. |

---

*DataScience Flow v10.0 — HMG Academy — HMG Concepts (est. 2015) — His Marvellous Grace*
