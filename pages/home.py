import streamlit as st
import random

# --- CSS for Home Page ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background-color: #f8fbfa !important;
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif !important;
        color: #0f172a !important;
    }

    .home-hero {
        background: linear-gradient(135deg, #E0F7FA 0%, #FFFFFF 100%);
        border-radius: 24px;
        padding: clamp(1.5rem, 5vw, 3rem);
        margin-bottom: 2rem;
        border: 1px solid rgba(59, 130, 246, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-title {
        font-family: 'Montserrat', sans-serif;
        color: #0f172a !important;
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 800;
        margin: 0 0 1rem 0;
        letter-spacing: -1px;
    }
    .welcome-subtitle {
        font-family: 'Inter', sans-serif;
        color: #475569 !important;
        font-size: clamp(0.95rem, 1.2vw, 1.1rem);
        line-height: 1.6;
        max-width: 700px;
    }
    
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .status-dot {
        width: 10px; height: 10px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
    
    .quick-card {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        height: 100%;
        text-align: center;
    }
    .quick-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #3b82f633;
    }
    .card-icon {
        font-size: 2.8rem;
        margin-bottom: 1.2rem;
    }
    .card-title {
        font-family: 'Montserrat', sans-serif;
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    .card-desc {
        font-family: 'Inter', sans-serif;
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Tablet/Mobile Adjustments */
    @media (max-width: 1024px) {
        .welcome-title { font-size: 2.2rem; }
    }
    @media (max-width: 768px) {
        .home-hero { padding: 2rem 1.5rem; }
        .quick-card { margin-bottom: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Fetch User
user_name = st.session_state.get('user_name', 'Host')

# --- Hero Section ---
st.markdown(f"""
<div class="home-hero">
    <h1 class="welcome-title">Welcome back, {user_name}.</h1>
    <p class="welcome-subtitle">
        Your UtilityGuard autonomous pipeline is active and monitoring all sectors. 
        Multi-agent reasoning cycles are nominal and no critical anomalies require human intervention at this time.
    </p>
    <div>
        <div class="status-pill">
            <div class="status-dot"></div>
            System Operating Normally
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Interactive Quick Action Blocks ---
st.markdown("### Quick Overview")
st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="quick-card">
        <div class="card-icon">🌊</div>
        <div class="card-title">Live Analytics</div>
        <div class="card-desc">Navigate to the dashboard for real-time sensor streams and multi-agent logs.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    uptime = random.randint(120, 480)
    st.markdown(f"""
    <div class="quick-card">
        <div class="card-icon">⚡</div>
        <div class="card-title">System Metrics</div>
        <div class="card-desc">Uptime: {uptime} hours. 100% LLM Reasoning reliability observed.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="quick-card">
        <div class="card-icon">🛡️</div>
        <div class="card-title">Autonomous Action</div>
        <div class="card-desc">Simulate controlled leak/shortage events across zones via Dashboard.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid rgba(0,188,212,0.1)'><br>", unsafe_allow_html=True)

st.info("Tip: Look to your sidebar to navigate to the Analytics & Dashboard or to Log out securely.")
