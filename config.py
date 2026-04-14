import os

def _get_secret(key, default=None):
    """Read a secret from st.secrets (Streamlit Cloud) or fall back to os.getenv."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

# Database
DATABASE_URL = _get_secret("DATABASE_URL")

# Admin Authentication
ADMIN_USERNAME = _get_secret("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = _get_secret("ADMIN_PASSWORD", "admin")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.txt")
JOB_ROLES_FILE = os.path.join(DATA_DIR, "job_roles.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "Uploaded_Resumes")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
