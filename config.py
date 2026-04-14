import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Admin Authentication
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.txt")
JOB_ROLES_FILE = os.path.join(DATA_DIR, "job_roles.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "Uploaded_Resumes")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
