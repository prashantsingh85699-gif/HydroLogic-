import streamlit as st
import time

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap');
    
    .stApp {
        background-color: #f8fbfa !important;
    }
    h1 {
        font-family: 'Montserrat', sans-serif !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem;
    }
    .settings-panel {
        background: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        margin-top: 1rem;
    }
    
    /* Input Styling */
    div[data-baseweb="input"] {
        border-radius: 12px !important;
    }

    /* Buttons */
    div.stButton > button {
        background: #0f172a !important;
        color: white !important;
        border-radius: 14px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        width: auto !important;
        transition: all 0.2s !important;
    }
    div.stButton > button:hover {
        background: #1e293b !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.2) !important;
    }

    @media (max-width: 768px) {
        .settings-panel { padding: 1.5rem; }
        div.stButton > button { width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Settings & Preferences ⚙️</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #607d8b; font-size: 1.1rem; margin-bottom: 2rem;'>Manage your account and platform preferences.</p>", unsafe_allow_html=True)

# Fetch current info
user_name = st.session_state.get('user_name', 'Host')
username = st.session_state.get('username', 'admin')

with st.container():
    st.markdown("<div class='settings-panel text-align: left;'>", unsafe_allow_html=True)
    st.subheader("Profile Information")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full Name", value=user_name)
        st.text_input("Username / Email", value=username, disabled=True)
    with c2:
        st.text_input("Role", value="System Administrator", disabled=True)
        st.text_input("Phone Number", placeholder="+1 (555) 000-0000")
    
    if st.button("Save Profile"):
        with st.spinner("Saving..."):
            time.sleep(0.5)
        st.success("Profile updated.")
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='settings-panel' style='margin-top:20px;'>", unsafe_allow_html=True)
    st.subheader("Notification Preferences")
    st.checkbox("Receive SMS on Critical Alerts", value=True)
    st.checkbox("Receive Daily Email Digest", value=True)
    st.checkbox("Push Notifications", value=False)
    
    if st.button("Update Preferences"):
        with st.spinner("Saving..."):
            time.sleep(0.5)
        st.success("Preferences updated.")
    st.markdown("</div>", unsafe_allow_html=True)
