import psycopg2
import logging
import streamlit as st
from config import DATABASE_URL

logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def init_db():
    """Initializes and returns a database connection (cached per server session)."""
    if not DATABASE_URL:
        logger.warning("DATABASE_URL is not set — database features will be disabled.")
        return None
        
    try:
        connection = psycopg2.connect(dsn=DATABASE_URL, connect_timeout=10)
        connection.autocommit = True
        logger.info("Database connection established successfully.")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def create_user_data_table(connection):
    """Creates the user_data table and required columns if they do not exist."""
    if connection is None:
        return
        
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                resume_score REAL,
                timestamp TIMESTAMPTZ,
                page_no INTEGER,
                predicted_field TEXT,
                predicted_role_confidence REAL,
                resume_strength TEXT,
                user_level TEXT,
                actual_skills JSONB,
                recommended_skills JSONB,
                recommended_courses JSONB
            );
            """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS user_data_unique_email_timestamp ON user_data(email, timestamp);")
            
            # Polyfill columns for backwards compatibility
            columns = [
                ("predicted_role_confidence", "REAL"),
                ("resume_strength", "TEXT"),
                ("actual_skills", "JSONB"),
                ("recommended_skills", "JSONB"),
                ("recommended_courses", "JSONB")
            ]
            for col_name, col_type in columns:
                cursor.execute(f"ALTER TABLE user_data ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                
            logger.info("Database schemas verified.")
    except Exception as e:
        logger.error(f"Unable to initialize database table: {e}")

def insert_data(cursor, connection, data):
    """Inserts processed resume data into the user_data table."""
    if connection is None or cursor is None:
        return False
        
    try:
        cursor.execute("""
        INSERT INTO user_data 
        (name, email, resume_score, timestamp, page_no, predicted_field, predicted_role_confidence, resume_strength, user_level, actual_skills, recommended_skills, recommended_courses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (email, timestamp) DO NOTHING
        """, data)
        connection.commit()
        logger.info(f"Successfully inserted record for email: {data[1]}")
        return True
    except Exception as e:
        logger.error(f"Failed to save resume record: {e}")
        return False
