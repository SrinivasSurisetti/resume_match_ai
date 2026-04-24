import streamlit as st
import pandas as pd
import plotly.express as px
from config import ADMIN_USERNAME, ADMIN_PASSWORD

def authenticate(username, password):
    """Verifies that the entered credentials map to the configured admin environment variables."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def do_login():
    """Form callback function to securely handle login without leaking widget references."""
    form_user = st.session_state.admin_user_input
    form_pass = st.session_state.admin_pass_input
    
    if authenticate(form_user, form_pass):
        st.session_state["admin_logged_in"] = True
    else:
        st.session_state["admin_login_error"] = "Invalid credentials"
        
    # Clear memory footprints to prevent double submission anomalies
    st.session_state.admin_pass_input = ""

def do_logout():
    """Properly resets session securely."""
    st.session_state["admin_logged_in"] = False

def admin_page(connection):

    """Primary router determining access rendering to the Admin interface."""
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
    if "admin_login_error" not in st.session_state:
        st.session_state["admin_login_error"] = None

    if st.session_state["admin_logged_in"]:
        _render_dashboard(connection)
    else:
        _render_login_form()

def _render_login_form():
    """Renders the pristine login screen free of dynamic keys loops."""
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("## 🔐 Admin Login")
        st.write("Enter your credentials")
        
        st.info("""
🔐 Demo Admin Access
Username: admin
Password: admin

(For testing/demo purposes only)
""")

        
        # Display authentication errors right above the form if present
        if st.session_state["admin_login_error"]:
            st.error(st.session_state["admin_login_error"])
            st.session_state["admin_login_error"] = None

        with st.form("admin_login_form", clear_on_submit=False):
            st.text_input("Username", key="admin_user_input")
            st.text_input("Password", type="password", key="admin_pass_input")
            st.form_submit_button("Login", on_click=do_login)

        st.markdown("</div>", unsafe_allow_html=True)

def _render_dashboard(connection):
    """Yields all Dataframe insights ensuring database faults do not crash metrics."""
    st.button("Logout", on_click=do_logout)
    
    st.success("Welcome Admin")
    st.header("Admin Dashboard")

    if connection is None:
        st.error("Database unavailable. Cannot load analytics.")
        return

    try:
        df = pd.read_sql("SELECT * FROM user_data", connection)

        if df.empty:
            st.info("No resumes have been analyzed yet.")
            return

        # Core Metrics calculation
        total_resumes = len(df)
        unique_roles = df.get('predicted_field', pd.Series()).nunique()
        avg_score = df.get('resume_score', pd.Series(dtype=float)).astype(float).mean()

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Resumes", total_resumes)
        m2.metric("Unique Roles", unique_roles)
        m3.metric("Average Score", f"{avg_score:.1f}")

        st.subheader("Recent Submissions")
        st.dataframe(df)

        st.download_button("Download CSV", df.to_csv(index=False), "data.csv")

        # Visualization Metrics
        if 'predicted_field' in df.columns and not df['predicted_field'].isnull().all():
            st.subheader("Field Distribution")
            chart1 = px.pie(df, names='predicted_field', hole=0.3)
            st.plotly_chart(chart1, use_container_width=True)

        if 'user_level' in df.columns and not df['user_level'].isnull().all():
            st.subheader("Experience Level Breakdown")
            chart2 = px.pie(df, names='user_level', hole=0.3)
            st.plotly_chart(chart2, use_container_width=True)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Admin Dashboard Error: {e}")
        st.error(f"Error loading dashboard charts or data.")
