import streamlit as st

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
        font-size: clamp(1.8rem, 3vw, 2.4rem) !important;
    }
    .doc-section {
        background: #ffffff;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        margin-bottom: 1.5rem;
    }
    .topic-tag {
        background: #f1f5f9;
        color: #475569;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    h3 {
        font-family: 'Montserrat', sans-serif !important;
        color: #0f172a !important;
        margin-top: 0;
    }
    p, li {
        font-family: 'Inter', sans-serif;
        color: #475569;
        line-height: 1.6;
    }

    @media (max-width: 768px) {
        .doc-section { padding: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Support & Documentation 📚</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #607d8b; font-size: 1.1rem; margin-bottom: 2rem;'>Guides on using the UtilityGuard multi-agent platform.</p>", unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="doc-section">
        <span class="topic-tag">GETTING STARTED</span>
        <h3>How Authentication Works</h3>
        <p>UtilityGuard supports both local account creation and Social Login (Google/GitHub). Social logins are automatically mapped to your system profile upon first authorization.</p>
    </div>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="doc-section">
        <span class="topic-tag">AGENT ARCHITECTURE</span>
        <h3>The Reasoning Pipeline</h3>
        <p>Our platform utilizes five specialized agents:</p>
        <ul>
            <li><b>Perception Agent:</b> Monitors raw sensor data for anomalies.</li>
            <li><b>Reasoning Agent:</b> Evaluates the severity and determines root causes.</li>
            <li><b>Action Agent:</b> Triggers mechanical or digital fail-safes.</li>
            <li><b>Notification Agent:</b> Routes alerts to Slack, Email, and SMS.</li>
            <li><b>Manager Agent:</b> Orchestrates the entire lifecycle.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.info("Need more help? Contact our support team at support@utilityguard.tech")
