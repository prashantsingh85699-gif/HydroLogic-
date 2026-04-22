import streamlit as st
import time
from streamlit_cookies_controller import CookieController
from auth_api import authenticate_user, register_user, authenticate_oauth

# Initialize Cookie Controller with unified key
controller = CookieController(key="utilityguard_auth")

# --- Custom CSS for High-Fidelity Responsive Design ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(-45deg, #a1c4fd, #c2e9fb, #e0c3fc, #8ec5fc);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Responsive Container */
    .stMainBlockContainer {
        padding-top: 2vh !important;
        width: 95% !important;
        max-width: 550px !important;
        margin: 0 auto;
    }

    /* Tabs Redesign - Mocking the separate button look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px !important;
        background-color: transparent !important;
        padding-bottom: 20px !important;
        border-bottom: none !important;
        justify-content: center !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #64748b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        flex: 1 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 12px -1px rgba(59, 130, 246, 0.2) !important;
    }

    /* Card Styling */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 24px !important;
        padding: 2rem 2.5rem 2rem 2.5rem !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        margin-top: 0px !important;
    }

    /* Brand Logo / Section */
    .brand-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .logo-box {
        background: #3b82f6;
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 12px -3px rgba(59, 130, 246, 0.3) !important;
    }
    .brand-logo-svg {
        width: 35px;
        height: 35px;
    }
    .brand-title {
        font-family: 'Montserrat', sans-serif;
        color: #0f172a;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem !important;
        letter-spacing: -1px;
    }
    .brand-subtitle {
        font-family: 'Inter', sans-serif;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 0 !important;
    }

    /* Input Styling - High Visibility Fix */
    div[data-baseweb="input"], 
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border-radius: 14px !important;
    }
    div[data-baseweb="input"] {
        border: 1.5px solid #cbd5e1 !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        transition: all 0.2s !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] input {
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
        background-color: transparent !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        border: none !important;
    }
    [data-testid="stTextInput"] label {
        display: none !important;
    }
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Forgot Password Link */
    .forgot-link {
        text-align: right;
        margin-bottom: 1.2rem;
        margin-top: 0.4rem;
    }
    .forgot-link a {
        color: #3b82f6;
        text-decoration: none;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Primary Button */
    [data-testid="stForm"] button[kind="primary"], 
    [data-testid="stForm"] button[kind="secondaryFormSubmit"] {
        width: 100% !important;
        background-color: #0f172a !important;
        color: #ffffff !important;
        height: 50px !important;
        border-radius: 14px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
        cursor: pointer !important;
        margin-top: 0px !important;
    }
    [data-testid="stForm"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.3) !important;
    }

    /* Divider */
    .divider-container {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
    }
    .divider-line {
        flex-grow: 1;
        background: #e2e8f0;
        height: 1px;
    }
    .divider-text {
        padding: 0 15px;
        color: #94a3b8;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Social Buttons */
    .stButton button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 14px !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        transition: background-color 0.2s, border-color 0.2s !important;
    }
    .stButton button:hover {
        background-color: #f8fafc !important;
        border-color: #cbd5e1 !important;
    }

    /* Footer */
    .legal-footer {
        text-align: center;
        margin-top: 2.5rem;
        color: #64748b;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .legal-footer a {
        color: #1e293b;
        text-decoration: underline;
        font-weight: 500;
    }

    /* Responsiveness for mobile */
    @media (max-width: 480px) {
        .stMainBlockContainer {
            padding-top: 3vh !important;
        }
        [data-testid="stForm"] {
            padding: 2.5rem 1.5rem !important;
        }
        .social-row {
            flex-direction: column;
            gap: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Layout ---

# Branding Block
brand_html = """
<div class="brand-section">
    <div class="logo-box">
        <svg class="brand-logo-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 21.5C16.1421 21.5 19.5 18.1421 19.5 14C19.5 9.85786 12 2.5 12 2.5C12 2.5 4.5 9.85786 4.5 14C4.5 18.1421 7.85786 21.5 12 21.5Z" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 18.5C14.4853 18.5 16.5 16.4853 16.5 14C16.5 11.5147 12 7 12 7C12 7 7.5 11.5147 7.5 14C7.5 16.4853 9.51471 18.5 12 18.5Z" fill="#ffffff" fill-opacity="0.2"/>
        </svg>
    </div>
    <div class="brand-title">UtilityGuard</div>
    <p class="brand-subtitle">Manage your utilities with confidence</p>
</div>
"""

@st.dialog("Simulating External Login...")
def mock_oauth_dialog(provider: str):
    st.write(f"Connecting to **{provider.capitalize()}** OAuth Server...")
    oauth_email = st.text_input(f"Verify your {provider.capitalize()} Email", placeholder="user@gmail.com")
    oauth_name = st.text_input(f"Verify your Display Name", placeholder="Your Name")
    
    if st.button(f"Authorize {provider.capitalize()} ➔", use_container_width=True):
        if oauth_email and oauth_name:
            with st.spinner("Authorizing Token..."):
                time.sleep(1.5)
                result = authenticate_oauth(provider, oauth_email, oauth_name)
                if result['success']:
                    controller.set("auth_status", "logged_in", path="/")
                    st.session_state.username = result['username']
                    st.session_state.user_name = result['name']
                    st.session_state.logged_in = True
                    st.success("Authenticated! Redirecting...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(result['error'])
        else:
            st.warning("Please fill out the mock details to proceed.")

# Main Application logic
tab1, tab2 = st.tabs(["🔒 Sign In", "📝 Register"])

with tab1:
    with st.form("login_form", border=False):
        st.markdown(brand_html, unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="👤 Username", key="login_usr")
        password = st.text_input("Password", type="password", placeholder="🔒 Password", key="login_pwd")
        
        st.markdown('<div class="forgot-link"><a href="#">Forgot password?</a></div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Sign In →")
        
        if submitted:
            result = authenticate_user(username, password)
            if result['success']:
                controller.set("auth_status", "logged_in", path="/")
                st.session_state.username = result['username']
                st.session_state.user_name = result['name']
                st.session_state.logged_in = True
                st.success("Authentication successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(result['error'])

    # Divider & Social
    st.markdown("""
    <div class="divider-container">
        <div class="divider-line"></div>
        <div class="divider-text">OR CONTINUE WITH</div>
        <div class="divider-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Google", key="login_google", use_container_width=True):
            mock_oauth_dialog("google")
    with col2:
        if st.button("🐈 GitHub", key="login_github", use_container_width=True):
            mock_oauth_dialog("github")
            
    # Legal Footer
    st.markdown("""
    <div class="legal-footer">
        By continuing, you agree to our <br>
        <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    with st.form("register_form", border=False):
        st.markdown(brand_html, unsafe_allow_html=True)
        
        new_name = st.text_input("Full Name", placeholder="🏷️ Full Name", key="reg_name")
        new_username = st.text_input("Username", placeholder="👤 Choose Username", key="reg_usr")
        new_password = st.text_input("Password", type="password", placeholder="🔒 Create Password", key="reg_pwd")
        
        st.markdown('<div style="height: 15px"></div>', unsafe_allow_html=True)
        
        registered = st.form_submit_button("Create Account →")
        
        if registered:
            if new_name and new_username and new_password:
                success = register_user(new_name, new_username, new_password)
                if success:
                    st.success("Account created! Please Sign In.")
                else:
                    st.error("That username/email is already taken.")
            else:
                st.warning("Please fill out all fields.")
    
    st.markdown("""
    <div class="legal-footer">
        Already have an account? <b>Logout and Sign In</b>
    </div>
    """, unsafe_allow_html=True)
