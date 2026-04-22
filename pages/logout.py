import streamlit as st
import time
from streamlit_cookies_controller import CookieController

controller = CookieController(key="utilityguard_auth")

st.markdown("""
<style>
    /* Force Light Background for this page to override Streamlit defaults */
    .stApp {
        background-color: #f8fbfa !important;
    }

    /* Override header to be transparent */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Target the form to act as the nicely styled layout box */
    [data-testid="stForm"] {
        max-width: 450px;
        margin: 10vh auto;
        background: #ffffff !important;
        border: 2px solid rgba(192, 57, 43, 0.1) !important;
        padding: 3.5rem 3rem !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 40px rgba(192, 57, 43, 0.08) !important;
        text-align: center;
    }
    
    .logout-title {
        color: #0f3057;
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .logout-desc {
        color: #4a5568;
        font-family: 'Roboto', sans-serif;
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
        line-height: 1.5;
    }

    /* Center text explicitly inside the form internal div if needed */
    [data-testid="stForm"] > div:first-child {
        text-align: center;
    }

    /* Style the logout button */
    div.stButton > button {
        background: #e53e3e !important;
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.7rem 2rem !important;
        border: none !important;
        border-radius: 30px !important;
        width: 100%;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px rgba(229, 62, 62, 0.25) !important;
    }
    div.stButton > button:hover {
        background: #c53030 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(229, 62, 62, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

with st.form("logout_form", clear_on_submit=False):
    # Place text directly inside the structural form to avoid Streamlit HTML clipping
    st.markdown("<div class='logout-title'>Secure Session Exit</div>", unsafe_allow_html=True)
    st.markdown("<div class='logout-desc'>Are you sure you want to end your active UtilityGuard session and clear your authentication?</div>", unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Confirm Logout")
    
    if submitted:
        # Clear the JS cookie physically
        controller.remove("auth_status")
        # Reset Session State flags
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_name = "Host"
        
        st.success("Session closed securely. Redirecting...")
        time.sleep(1)
        st.rerun()
