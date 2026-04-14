import streamlit as st
import os
import logging
from config import BASE_DIR
from services.db_service import init_db, create_user_data_table
from ui.user_ui import user_page
from ui.admin_ui import admin_page

# Top-level Logging Config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Must be the first Streamlit command
st.set_page_config(
    page_title="ResumeMatch AI - 🤖",
    layout="wide",
    page_icon="🚀",
)

def apply_styles():
    """Injects isolated CSS mappings cleanly into the DOM framework."""
    style_path = os.path.join(BASE_DIR, "styles", "style.css")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)
    else:
        logging.getLogger(__name__).warning("CSS Stylesheet missing.")

def render_page_header():
    """Top-level unified app header."""
    st.markdown("""
    <div class='page-header'>
      <h1>ResumeMatch AI – Intelligent Resume Analysis & Role Prediction System ✅</h1>
      <p>Upload your resume, extract key insights, and discover personalized career recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Injects sidebar components independent of route rendering logic."""
    st.sidebar.markdown("""
    <div class='sidebar-card'>
      <div class='sidebar-title'>
        <h3>✨ ResumeMatch AI</h3>
        <p>Career-ready resume insights</p>
      </div>
      <div class='sidebar-section'>
        <div class='sidebar-section-title'>Select Mode</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.sidebar.selectbox("Select Mode", ["User","Admin"], label_visibility="collapsed")
    st.sidebar.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)
    debug_mode = st.sidebar.checkbox("Debug Mode", value=False)
    st.sidebar.markdown("<div class='sidebar-footer'>Built with Streamlit</div>", unsafe_allow_html=True)
    return choice, debug_mode

def run():
    """Execution endpoint decoupling configurations from routings."""
    apply_styles()
    render_page_header()

    # init_db is @st.cache_resource — runs only once per server session
    connection = init_db()
    cursor = None
    if connection is not None:
        # Only create the table on the very first load, not every rerun
        if "db_initialized" not in st.session_state:
            create_user_data_table(connection)
            st.session_state["db_initialized"] = True
        cursor = connection.cursor()

    route, debug_mode = render_sidebar()

    # Route delegation
    if route == "User":
        user_page(cursor, connection, debug_mode)
    else:
        admin_page(connection)

if __name__ == "__main__":
    run()