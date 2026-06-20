"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  DataScience Flow v10.0 — Security & Integrity Module (V3 Enhanced)         ║
║  Anti-bypass, anti-tamper, session hardening, input sanitisation             ║
║  Fingerprinting, audit trails, threat detection, CAPTCHA-like verification   ║
║  Built by Adewale Samson Adeagbo | HMG Concepts | Lagos, Nigeria             ║
║  Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import hashlib
import hmac
import time
import re
import os
import json
import secrets
from datetime import datetime, timedelta
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════
# SECURITY CONSTANTS
# ═══════════════════════════════════════════════════════════════════

PLATFORM_ID = "DSFlow_v10.0_HMG_Academy_V3"
PLATFORM_SALT = os.environ.get("DSFLOW_SALT", "hmg_academy_2025_salt_adewale_v3_enhanced")

# Rate limiting
MAX_ACTIONS_PER_MINUTE = 60
MAX_UPLOAD_SIZE_MB = 200
MAX_EXPORT_PER_HOUR = 30
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# Session security
SESSION_TIMEOUT_MINUTES = 120
MAX_CONCURRENT_SESSIONS = 3

# Subscription security
TRIAL_HOURS = 24
MAX_TRIAL_EXTENSIONS = 0
EMAIL_BREACH_COOLDOWN_HOURS = 24

# Brand watermark
BRAND_WATERMARK = "DataScience Flow | HMG Academy | HMG Concepts | Built by Adewale Samson Adeagbo"
BRAND_FOOTER = "© HMG Concepts (est. 2015) — HMG Academy · HMG Technologies · HMG Media · HMG Gospel"

# Suspicious patterns for threat detection
SUSPICIOUS_SQL = [
    "drop table", "drop database", "truncate", "delete from",
    "union select", "insert into", "update.*set", "exec xp_",
    "sp_", ";--", "1=1", "' or", "\" or", "admin'--",
    "waitfor delay", "benchmark(", "sleep(", "load_file(",
    "into outfile", "into dumpfile"
]
SUSPICIOUS_XSS = [
    "<script", "javascript:", "onerror=", "onload=", "onclick=",
    "onmouseover=", "<iframe", "<embed", "<object",
    "document.cookie", "window.location", "eval(",
    "alert(", "confirm(", "prompt("
]
SUSPICIOUS_PATH = [
    "../", "..\\", "/etc/passwd", "/etc/shadow",
    "c:\\windows", "\\boot.ini", "cmd.exe",
    "/proc/self", "wp-admin", "phpmyadmin"
]

# ═══════════════════════════════════════════════════════════════════
# SESSION INITIALIZATION
# ═══════════════════════════════════════════════════════════════════

def init_secure_session():
    """Initialize security state in session with defaults."""
    defaults = {
        "sec_initialized": True,
        "sec_init_time": time.time(),
        "sec_last_action": time.time(),
        "sec_action_log": [],
        "sec_export_count": 0,
        "sec_export_hour": datetime.now().hour,
        "sec_login_attempts": 0,
        "sec_lockout_until": None,
        "sec_fingerprint": None,
        "sec_violations": 0,
        "sec_hmac_token": None,
        "sec_audit_trail": [],
        "sec_threat_score": 0,
        "sec_email_used": None,
        "sec_email_used_time": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════
# HMAC TOKEN VERIFICATION
# ═══════════════════════════════════════════════════════════════════

def generate_hmac_token(data: str) -> str:
    """Generate HMAC-SHA256 token for integrity verification."""
    return hmac.new(
        PLATFORM_SALT.encode(),
        f"{PLATFORM_ID}:{data}".encode(),
        hashlib.sha256
    ).hexdigest()

def verify_hmac_token(data: str, token: str) -> bool:
    """Verify HMAC-SHA256 token integrity."""
    expected = generate_hmac_token(data)
    return hmac.compare_digest(expected, token)

def set_subscription_token(email: str, tier: str, expires: str):
    """Set tamper-proof subscription token."""
    payload = f"{email}:{tier}:{expires}"
    token = generate_hmac_token(payload)
    st.session_state["sub_hmac_token"] = token
    st.session_state["sub_hmac_payload"] = payload

def verify_subscription_integrity() -> bool:
    """Verify subscription session hasn't been tampered with."""
    token = st.session_state.get("sub_hmac_token")
    payload = st.session_state.get("sub_hmac_payload")
    if not token or not payload:
        return False
    return verify_hmac_token(payload, token)

# ═══════════════════════════════════════════════════════════════════
# INPUT SANITISATION (Enhanced V3)
# ═══════════════════════════════════════════════════════════════════

def sanitise_string(value: str, max_length: int = 500) -> str:
    """Remove potentially dangerous characters from string input."""
    if not value:
        return ""
    value = str(value)[:max_length]
    # Remove null bytes
    value = value.replace("\x00", "")
    # Remove control characters except newline and tab
    value = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    return value.strip()

def sanitise_email(email: str) -> str:
    """Validate and sanitise email address."""
    if not email:
        return ""
    email = email.strip().lower()[:254]
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return ""

def sanitise_url(url: str) -> str:
    """Validate and sanitise URL — only http/https allowed."""
    if not url:
        return ""
    url = url.strip()[:2048]
    pattern = r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+$'
    if re.match(pattern, url):
        return url
    return ""

def sanitise_sql(query: str) -> str:
    """Block dangerous SQL commands."""
    if not query:
        return ""
    lower = query.lower().strip()
    for pattern in SUSPICIOUS_SQL:
        if re.search(pattern, lower):
            log_action("sql_injection_blocked", pattern)
            return ""
    return query[:5000]

def sanitise_html(value: str) -> str:
    """Escape HTML to prevent XSS."""
    if not value:
        return ""
    return (value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;"))

def detect_xss(value: str) -> bool:
    """Detect potential XSS attack patterns."""
    if not value:
        return False
    lower = value.lower()
    return any(p in lower for p in SUSPICIOUS_XSS)

def detect_path_traversal(value: str) -> bool:
    """Detect path traversal attempts."""
    if not value:
        return False
    lower = value.lower()
    return any(p in lower for p in SUSPICIOUS_PATH)

def detect_threat(value: str) -> dict:
    """Comprehensive threat detection for any input."""
    threats = {
        "xss": detect_xss(value),
        "path_traversal": detect_path_traversal(value),
        "sql_injection": any(p in value.lower() for p in SUSPICIOUS_SQL) if value else False,
        "is_safe": True,
    }
    threats["is_safe"] = not any([threats["xss"], threats["path_traversal"], threats["sql_injection"]])
    if not threats["is_safe"]:
        st.session_state["sec_threat_score"] = st.session_state.get("sec_threat_score", 0) + 1
        log_action("threat_detected", json.dumps(threats))
    return threats

# ═══════════════════════════════════════════════════════════════════
# RATE LIMITING (Enhanced with lockout)
# ═══════════════════════════════════════════════════════════════════

def check_rate_limit(action: str = "general") -> bool:
    """Check if action is within rate limits. Returns True if allowed."""
    now = time.time()
    last = st.session_state.get("sec_last_action", now)
    actions = st.session_state.get("sec_action_log", [])

    # Clean old entries (older than 60 seconds)
    actions = [a for a in actions if now - a < 60]

    if len(actions) >= MAX_ACTIONS_PER_MINUTE:
        st.session_state["sec_violations"] = st.session_state.get("sec_violations", 0) + 1
        log_action("rate_limit_exceeded", action)
        return False

    actions.append(now)
    st.session_state["sec_action_log"] = actions
    st.session_state["sec_last_action"] = now
    return True

def check_export_limit() -> bool:
    """Check if export is within hourly limit."""
    current_hour = datetime.now().hour
    if st.session_state.get("sec_export_hour") != current_hour:
        st.session_state["sec_export_count"] = 0
        st.session_state["sec_export_hour"] = current_hour

    count = st.session_state.get("sec_export_count", 0)
    if count >= MAX_EXPORT_PER_HOUR:
        log_action("export_limit_exceeded", f"{count}/{MAX_EXPORT_PER_HOUR}")
        return False

    st.session_state["sec_export_count"] = count + 1
    return True

def check_login_attempts() -> bool:
    """Check if login attempts are within limits. Returns True if allowed."""
    lockout = st.session_state.get("sec_lockout_until")
    if lockout and datetime.now() < lockout:
        remaining = (lockout - datetime.now()).seconds // 60
        return False

    attempts = st.session_state.get("sec_login_attempts", 0)
    if attempts >= MAX_LOGIN_ATTEMPTS:
        st.session_state["sec_lockout_until"] = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
        st.session_state["sec_login_attempts"] = 0
        log_action("account_locked", f"{LOCKOUT_MINUTES} minutes")
        return False
    return True

def record_failed_login():
    """Record a failed login attempt."""
    st.session_state["sec_login_attempts"] = st.session_state.get("sec_login_attempts", 0) + 1

def record_successful_login():
    """Reset login attempts on success."""
    st.session_state["sec_login_attempts"] = 0
    st.session_state["sec_lockout_until"] = None

# ═══════════════════════════════════════════════════════════════════
# EMAIL REUSE PREVENTION
# ═══════════════════════════════════════════════════════════════════

def check_email_reuse(email: str) -> bool:
    """Check if email was recently used for a trial. Returns True if email is OK to use."""
    last_email = st.session_state.get("sec_email_used")
    last_time = st.session_state.get("sec_email_used_time")

    if last_email and last_email == email and last_time:
        elapsed = (datetime.now() - last_time).total_seconds() / 3600
        if elapsed < EMAIL_BREACH_COOLDOWN_HOURS:
            return False
    return True

def record_email_use(email: str):
    """Record that an email was used for a trial."""
    st.session_state["sec_email_used"] = email
    st.session_state["sec_email_used_time"] = datetime.now()

# ═══════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def check_session_timeout() -> bool:
    """Check if session has expired. Returns True if expired."""
    init_time = st.session_state.get("sec_init_time", time.time())
    elapsed = (time.time() - init_time) / 60
    return elapsed > SESSION_TIMEOUT_MINUTES

def generate_session_fingerprint() -> str:
    """Generate a session fingerprint for integrity checking."""
    data = f"{st.session_state.get('sub_auth_email', '')}:{st.session_state.get('sub_tier', '')}:{PLATFORM_ID}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def validate_session_fingerprint() -> bool:
    """Validate that the session fingerprint hasn't changed."""
    current = generate_session_fingerprint()
    stored = st.session_state.get("sec_fingerprint")
    if stored is None:
        st.session_state["sec_fingerprint"] = current
        return True
    return stored == current

# ═══════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════

def authenticate_subscription(email: str, tier: str) -> bool:
    """Authenticate a subscription with security checks."""
    email = sanitise_email(email)
    if not email:
        return False

    if not check_email_reuse(email):
        return False

    if not check_login_attempts():
        return False

    # Set session state
    st.session_state["sub_authenticated"] = True
    st.session_state["sub_auth_email"] = email
    st.session_state["sub_tier"] = tier

    # Calculate expiry
    from subscription import TIERS
    tier_info = TIERS.get(tier, TIERS.get("free_trial"))
    days = tier_info.get("days", 1) if tier_info else 1
    expires = datetime.now() + timedelta(days=days)
    st.session_state["sub_expires"] = expires.isoformat()

    # Set HMAC token for integrity
    set_subscription_token(email, tier, expires.isoformat())

    # Record success
    record_successful_login()
    record_email_use(email)
    st.session_state["sec_fingerprint"] = generate_session_fingerprint()

    log_action("login_success", f"{email}:{tier}")
    return True

# ═══════════════════════════════════════════════════════════════════
# UPLOAD VALIDATION
# ═══════════════════════════════════════════════════════════════════

ALLOWED_EXTENSIONS = {
    "csv", "xlsx", "xls", "json", "parquet", "tsv",
    "txt", "md", "py", "ipynb"
}
ALLOWED_MIME_TYPES = {
    "text/csv", "application/csv", "text/plain",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel", "application/json",
    "application/octet-stream", "text/tab-separated-values",
}

def validate_upload(filename: str, size: int, content_type: str = "") -> dict:
    """Validate file upload for security. Returns {valid: bool, error: str}."""
    if not filename:
        return {"valid": False, "error": "No filename provided"}

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return {"valid": False, "error": f"File type '.{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}

    if size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        return {"valid": False, "error": f"File too large. Maximum: {MAX_UPLOAD_SIZE_MB}MB"}

    if content_type and content_type not in ALLOWED_MIME_TYPES and not content_type.startswith("text/"):
        pass  # Allow unknown MIME types as Streamlit may not always provide correct MIME

    # Check for suspicious filename patterns
    for pattern in SUSPICIOUS_PATH:
        if pattern in filename.lower():
            return {"valid": False, "error": "Invalid filename detected"}

    return {"valid": True, "error": ""}

# ═══════════════════════════════════════════════════════════════════
# AUDIT LOGGING
# ═══════════════════════════════════════════════════════════════════

def log_action(action: str, detail: str = ""):
    """Log an action to the session audit trail."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action[:100],
        "detail": detail[:200],
        "threat_score": st.session_state.get("sec_threat_score", 0),
    }
    trail = st.session_state.get("sec_audit_trail", [])
    trail.append(entry)
    # Keep only last 200 entries
    st.session_state["sec_audit_trail"] = trail[-200:]

def get_security_status() -> dict:
    """Get current security status summary."""
    return {
        "session_age_minutes": int((time.time() - st.session_state.get("sec_init_time", time.time())) / 60),
        "total_actions": len(st.session_state.get("sec_audit_trail", [])),
        "exports_this_hour": st.session_state.get("sec_export_count", 0),
        "threat_score": st.session_state.get("sec_threat_score", 0),
        "violations": st.session_state.get("sec_violations", 0),
        "fingerprint_valid": validate_session_fingerprint(),
        "integrity_verified": verify_subscription_integrity() if st.session_state.get("sub_authenticated") else False,
    }

# ═══════════════════════════════════════════════════════════════════
# WATERMARKING
# ═══════════════════════════════════════════════════════════════════

def watermark_dataframe(df, platform: str = "DataScience Flow v10.0") -> str:
    """Return watermark metadata string for data exports."""
    return f"# {BRAND_WATERMARK} | Generated: {datetime.now().isoformat()} | Platform: {platform}"

def watermark_notebook() -> dict:
    """Return watermark cell for Jupyter notebooks."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            f"**{BRAND_WATERMARK}**\n\n",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n",
            "Part of HMG Academy Ecosystem — Subsidiary of HMG Concepts (est. 2015)\n\n",
            "*This notebook was auto-generated by DataScience Flow. Unauthorized redistribution prohibited.*\n",
            "---"
        ]
    }

# ═══════════════════════════════════════════════════════════════════
# CAPTCHA-LIKE VERIFICATION (Simple math challenge)
# ═══════════════════════════════════════════════════════════════════

def generate_captcha_challenge() -> tuple:
    """Generate a simple math challenge. Returns (question, answer)."""
    import random
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    ops = [("+", a + b), ("-", a - b), ("×", a * b)]
    op, answer = random.choice(ops)
    question = f"{a} {op} {b} = ?"
    return question, str(answer)

# ═══════════════════════════════════════════════════════════════════
# SECURITY STATUS DISPLAY
# ═══════════════════════════════════════════════════════════════════

def render_security_badge():
    """Render a compact security status indicator."""
    status = get_security_status()
    integrity = "🔒 Secured" if status["integrity_verified"] else "⚠️ Unverified"
    threat = "🟢" if status["threat_score"] == 0 else "🟡" if status["threat_score"] < 3 else "🔴"
    return f"{threat} {integrity} | Session: {status['session_age_minutes']}min | Actions: {status['total_actions']}"
