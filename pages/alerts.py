import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap');
    
    .stApp {
        background-color: #f8fbfa !important;
    }
    .header-container {
        padding: 2rem 0 1rem 0;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    h1 {
        font-family: 'Montserrat', sans-serif !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: clamp(1.8rem, 3vw, 2.4rem) !important;
    }
    .alert-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        border-left: 6px solid;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .alert-card:hover {
        transform: translateY(-4px);
    }
    .critical { border-left-color: #ef4444; }
    .warning { border-left-color: #f59e0b; }
    .info { border-left-color: #0ea5e9; }
    
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #f1f5f9;
    }

    @media (max-width: 768px) {
        .alert-card { padding: 1.2rem; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-container'><h1>System Alerts Log 🔔</h1><p style='color: #607d8b; font-size: 1.1rem;'>Real-time operational alerts from Perception and Reasoning Agents.</p></div>", unsafe_allow_html=True)


# Generate dummy alerts data
now = datetime.now()
data = []
levels = ["Critical", "Warning", "Info", "Info"]
locations = ["Sector A-1 (Main Pipe)", "Zone 4 Reservoir", "Pump Station B", "Substation X (Power)"]
messages = ["High pressure detected! Potential leak.", "Flow rate drop of 15%. Investigation needed.", "Routine maintenance completed.", "Power blip registered; failovers engaged."]

for i in range(12):
    lvl = random.choice(levels)
    data.append({
        "Time": (now - timedelta(minutes=random.randint(5, 500))).strftime("%Y-%m-%d %H:%M"),
        "Level": lvl,
        "Location": random.choice(locations),
        "Message": random.choice(messages),
        "Status": random.choice(["Open", "Investigating", "Resolved"])
    })

df = pd.DataFrame(data).sort_values("Time", ascending=False).reset_index(drop=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='alert-card critical'><h3>🔴 3 Critical</h3><p>Requires immediate action.</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='alert-card warning'><h3>🟡 5 Warnings</h3><p>Monitoring closely.</p></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='alert-card info'><h3>🔵 12 Info</h3><p>System operational logs.</p></div>", unsafe_allow_html=True)

st.markdown("### Recent Log Entries")
st.dataframe(df, use_container_width=True, hide_index=True)
