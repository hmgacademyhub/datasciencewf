"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  CONFIDENTIAL — DataScience Flow v10.0 — Subscription & Auth Manager (V3)   ║
║  Copyright © 2015-2026 HMG Concepts — All Rights Reserved                   ║
║  Built by Adewale Samson Adeagbo | HMG Academy | HMG Concepts               ║
║  Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import hashlib
import os
from datetime import datetime, timedelta

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

# ═══════════════════════════════════════════════════════════════════
# SUBSCRIPTION TIERS — Detailed Feature Mapping
# ═══════════════════════════════════════════════════════════════════

TIERS = {
    "free_trial": {
        "name": "1-Day Free Trial",
        "days": 1,
        "price": "Free",
        "price_usd": "$0",
        "description": "Full access to explore the platform for 24 hours. No credit card required.",
        "who_is_this_for": "Students exploring data science, first-time users evaluating the platform, quick one-time analyses.",
        "features": [
            "Full access to all 76 modules for 24 hours",
            "Upload up to 50MB datasets",
            "All visualizations & charts",
            "Basic export (CSV, Excel)",
            "Learning paths (all 4 levels)",
            "Data dictionary builder",
            "PWA install on phone/laptop",
            "No AI API — 100% rule-based",
            "Guided workflow from EDA to deployment",
            "Jupyter Notebook (.ipynb) generation",
            "Data quality scorecard",
            "Secured & integrity-verified session",
            "Curriculum tracker access",
            "Code challenges (beginner level)",
            "Progress tracking",
        ],
        "limits": {"max_rows": 50000, "max_file_mb": 50, "max_exports_per_hour": 10},
        "enterprise_features": False,
        "curriculum_access": ["beginner"],
        "support": "Community forum",
    },
    "essential": {
        "name": "Essential Plan",
        "price": "₦3,500/month",
        "price_usd": "$4/month",
        "description": "For individual data analysts and students who need regular access to data science tools.",
        "who_is_this_for": "Data analysts, undergraduate students, junior data scientists, self-learners building their portfolio.",
        "features": [
            "Everything in Free Trial",
            "Upload up to 200MB datasets",
            "All export formats (incl. Parquet, HTML, .ipynb)",
            "SQL Query Console (DuckDB)",
            "12+ chart types & advanced viz",
            "Hypothesis testing suite",
            "What-If & Scenario Simulator",
            "Data Monitor & Alert Rules",
            "Collaboration Hub",
            "30-day email support",
            "AB Testing Calculator",
            "Data Validation Framework",
            "Curriculum tracker (beginner + intermediate)",
            "Code challenges (all levels)",
            "Progress certificate",
            "Data Collection Hub (full)",
            "Project Journal",
            "Notebook Playground",
        ],
        "limits": {"max_rows": 200000, "max_file_mb": 200, "max_exports_per_hour": 20},
        "enterprise_features": False,
        "curriculum_access": ["beginner", "intermediate"],
        "support": "Email support (48hr response)",
    },
    "professional": {
        "name": "Professional Plan",
        "price": "₦8,500/month",
        "price_usd": "$10/month",
        "description": "For professional data scientists who need the full ML pipeline and advanced analytics.",
        "who_is_this_for": "Professional data scientists, ML engineers, researchers, data science teams (2-5 people), 3MTT fellows.",
        "features": [
            "Everything in Essential",
            "Unlimited dataset size",
            "Full ML Pipeline (7 algorithms + comparison)",
            "Feature Engineering Suite (7 encodings)",
            "SMOTE & Class Imbalance Handling",
            "Advanced Charts (Gantt, Sankey, 3D)",
            "Text Analysis (TF-IDF, Sentiment)",
            "Data Privacy & PII Masking (8 methods)",
            "Data Contracts & Schema Validation",
            "Priority email support",
            "Model Comparison Dashboard",
            "Geospatial Analysis & NLP Pipeline",
            "Hyperparameter Guide & Simulator",
            "Causal Inference module",
            "Network Analysis module",
            "Anomaly Detection Dashboard",
            "Survival Analysis module",
            "Full curriculum access (all levels)",
            "Certificate generator",
            "Data Catalog",
            "Cost Estimator for ML",
        ],
        "limits": {"max_rows": 1000000, "max_file_mb": 500, "max_exports_per_hour": 30},
        "enterprise_features": False,
        "curriculum_access": ["beginner", "intermediate", "advanced"],
        "support": "Priority email + WhatsApp (24hr response)",
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price": "₦25,000/month",
        "price_usd": "$30/month",
        "description": "For organizations that need governance, compliance, and team collaboration features.",
        "who_is_this_for": "Enterprise data teams, compliance officers, organizations with GDPR/NDPR requirements, universities, training institutions.",
        "features": [
            "Everything in Professional",
            "Compliance Center (GDPR/NDPR)",
            "Disaster Recovery (RPO/RTO)",
            "Retention Policy Management",
            "Data Lineage & Full Audit Trails",
            "Enterprise KPI Dashboard",
            "API Documentation Generator",
            "Audit & Compliance Reports",
            "Role-Based Access Control (4 roles)",
            "Dedicated account manager",
            "Custom feature requests",
            "Pipeline Builder & Dashboard Builder",
            "Notebook Playground & Deployment Guide",
            "Workflow Scheduler",
            "Feature Store concepts",
            "Data Quality SLA monitor",
            "Model Registry",
            "Full audit trail viewer",
            "Organization branding options",
            "Bulk user management (Supabase)",
        ],
        "limits": {"max_rows": None, "max_file_mb": 1000, "max_exports_per_hour": 100},
        "enterprise_features": True,
        "curriculum_access": ["beginner", "intermediate", "advanced", "enterprise"],
        "support": "Dedicated account manager + WhatsApp + Phone",
    },
}

# ═══════════════════════════════════════════════════════════════════
# SUBSCRIPTION STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def init_subscription_state():
    """Initialize subscription state with defaults."""
    defaults = {
        "sub_auth_email": None,
        "sub_tier": None,
        "sub_expires": None,
        "sub_trial_used": False,
        "sub_authenticated": False,
        "sub_payment_ref": None,
        "sub_hmac_token": None,
        "sub_hmac_payload": None,
        "sub_started": None,
        "sub_last_activity": None,
        "sub_feature_usage": {},
        "sub_progress": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def tier_badge_html(tier_key: str) -> str:
    """Generate HTML badge for subscription tier."""
    colors = {
        "free_trial": ("#4f8ef7", "FREE TRIAL"),
        "essential": ("#00d9a7", "ESSENTIAL"),
        "professional": ("#d4a843", "PROFESSIONAL"),
        "enterprise": ("#8b5cf6", "ENTERPRISE"),
    }
    color, label = colors.get(tier_key, ("#484f58", tier_key.upper()))
    return f'<span style="background:{color}; color:#fff; padding:4px 14px; border-radius:16px; font-size:0.78rem; font-weight:700;">{label}</span>'

def get_tier_info():
    """Get current tier information."""
    tier = st.session_state.get("sub_tier")
    if tier and tier in TIERS:
        return TIERS[tier]
    return None

def has_feature(feature_name: str) -> bool:
    """Check if current tier has access to a specific feature."""
    tier_info = get_tier_info()
    if not tier_info:
        return False
    return any(feature_name.lower() in f.lower() for f in tier_info.get("features", []))

def has_curriculum_access(level: str) -> bool:
    """Check if current tier has access to a curriculum level."""
    tier_info = get_tier_info()
    if not tier_info:
        return False
    return level in tier_info.get("curriculum_access", [])

def check_trial_expiry() -> bool:
    """Check if trial has expired. Returns True if still valid."""
    expires = st.session_state.get("sub_expires")
    if not expires:
        return False
    try:
        expiry_dt = datetime.fromisoformat(str(expires))
        return datetime.now() < expiry_dt
    except:
        return False

def get_remaining_time() -> str:
    """Get remaining subscription time as human-readable string."""
    expires = st.session_state.get("sub_expires")
    if not expires:
        return "Not active"
    try:
        expiry_dt = datetime.fromisoformat(str(expires))
        remaining = expiry_dt - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Expired"
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        if hours > 24:
            days = hours // 24
            return f"{days} days {hours % 24} hours"
        return f"{hours}h {minutes}m"
    except:
        return "Unknown"

def record_feature_usage(feature: str):
    """Record usage of a feature for analytics."""
    usage = st.session_state.get("sub_feature_usage", {})
    usage[feature] = usage.get(feature, 0) + 1
    st.session_state["sub_feature_usage"] = usage

def local_save_subscription(email: str, tier: str, expires: str):
    """Save subscription data locally."""
    st.session_state["_sub_data"] = {
        "email": email,
        "tier": tier,
        "expires": expires,
        "trial_used": st.session_state.get("sub_trial_used", False),
        "started": datetime.now().isoformat(),
        "platform": "DataScience Flow v10.0 — HMG Academy — HMG Concepts",
    }
    return True

def local_load_subscription():
    """Load subscription data from local storage."""
    return st.session_state.get("_sub_data")

def get_subscription_summary() -> dict:
    """Get a comprehensive subscription summary."""
    tier_info = get_tier_info()
    return {
        "email": st.session_state.get("sub_auth_email", "Not set"),
        "tier": st.session_state.get("sub_tier", "None"),
        "tier_name": tier_info.get("name", "None") if tier_info else "None",
        "remaining_time": get_remaining_time(),
        "features_used": st.session_state.get("sub_feature_usage", {}),
        "is_active": st.session_state.get("sub_authenticated", False),
        "trial_available": not st.session_state.get("sub_trial_used", False),
    }
