import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController

# Global Page Config must be first
st.set_page_config(
    page_title="Hydrologic Platform",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Cookie Controller with a UNIFIED key for all pages
controller = CookieController(key="hydrologic_auth")

# Provide a small invisible state to keep track
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_name" not in st.session_state:
    st.session_state.user_name = "Host"

# Fetch cookie state
auth_cookie = controller.get("auth_status")

if auth_cookie == "logged_in":
    st.session_state.logged_in = True
else:
    # If cookie is missing or 'logged_out', we treat as logged out
    st.session_state.logged_in = False
# Define application routes
if st.session_state.logged_in:
    home = st.Page("pages/home.py", title="Home Profile", icon=":material/home:")
    dash = st.Page("pages/dashboard_page.py", title="Analytics & Dashboard", icon=":material/analytics:")
    alerts = st.Page("pages/alerts.py", title="Alerts Log", icon=":material/notifications:")
    settings = st.Page("pages/settings.py", title="Settings", icon=":material/settings:")
    support = st.Page("pages/support.py", title="Support & Docs", icon=":material/help:")
    logout = st.Page("pages/logout.py", title="Logout", icon=":material/logout:")
    
    pg = st.navigation([home, dash, alerts, settings, support, logout])
    
    # Sidebar branding
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h3 style='color: #00BCD4; margin: 0;'>Hydrologic v2.0</h3>
        <p style='font-size: 0.8rem; color: #888;'>Enterprise Water Management</p>
    </div>
    <hr style='margin: 0;'>
    """, unsafe_allow_html=True)
else:
    login = st.Page("pages/login.py", title="Secure Login", icon=":material/lock:")
    pg = st.navigation([login])

# Run active router
pg.run()

# App Footer (Sticky to bottom if possible in Streamlit, otherwise standard footer)
if st.session_state.logged_in:
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 50px; padding: 20px; border-top: 1px solid #eee;'>
        © 2026 Hydrologic Platform • Autonomous Infrastructure Management
    </div>
    """, unsafe_allow_html=True)
