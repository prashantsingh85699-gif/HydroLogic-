"""
UtilityGuard — Streamlit Dashboard (Responsive Light Green Edition)

Live status panel, agent logs, event history, simulation controls,
and summary report — fully responsive, clean light green theme,
enterprise-grade polish, works on all screen sizes.
"""

import sys
import os
import json
import time
import random
from datetime import datetime

import streamlit as st

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings
from logger_setup import get_dashboard_logs
from memory import memory
from sensor_data import ZONE_BASELINES, load_last_readings
from pipeline import run_cycle, simulate_leak, simulate_shortage

# ── Page Config ────────────────────────────────────────────────────────────────
# (Moved to app.py global router)

# ── Responsive Light Green Theme CSS ───────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@700;800&display=swap');

    :root {
        --bg-primary: #FAFAFA;
        --bg-card: #FFFFFF;
        --bg-card-hover: #F0F9FA;
        --accent: #00BCD4;
        --accent-deep: #1A237E;
        --text-dark: #0f172a;
        --text-muted: #64748b;
        --border: rgba(59, 130, 246, 0.1);
        --border-hover: rgba(59, 130, 246, 0.3);
        --red: #ef4444;
        --orange: #f59e0b;
        --white: #FAFAFA;
        --green: #22c55e;
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --radius: 20px;
    }

    *, *::before, *::after {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }

    /* ─── Prevent ALL overflow ─── */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* ─── Light Background ─── */
    .stApp {
        background: var(--bg-primary) !important;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(ellipse 50% 40% at 15% 20%, rgba(76, 175, 80, 0.1) 0%, transparent 70%),
            radial-gradient(ellipse 50% 35% at 80% 70%, rgba(0, 188, 212, 0.06) 0%, transparent 70%);
    }

    /* ─── Animations ─── */
    @keyframes subtleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
    }
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(0, 188, 212,0.3); }
        50% { border-color: rgba(0, 188, 212,0.55); }
    }
    @keyframes alertPulse {
        0%, 100% { box-shadow: var(--shadow-sm); }
        50% { box-shadow: 0 2px 12px rgba(192,57,43,0.2); }
    }
    @keyframes alertPulseOrange {
        0%, 100% { box-shadow: var(--shadow-sm); }
        50% { box-shadow: 0 2px 12px rgba(214,137,16,0.2); }
    }
    @keyframes sparklineAnim {
        0% { stroke-dashoffset: 200; }
        100% { stroke-dashoffset: 0; }
    }
    @keyframes liveDot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    @keyframes agentStatusPulse {
        0%, 100% { box-shadow: 0 0 2px currentColor; }
        50% { box-shadow: 0 0 5px currentColor; }
    }
    @keyframes cardEntrance {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* ─── Main Container ─── */
    .main .block-container {
        padding: 1rem 1.5rem;
        max-width: 1600px;
        position: relative;
        z-index: 1;
    }

    /* ─── Header ─── */
    .hero-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 1.2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(0, 188, 212, 0.15);
    }
    .hero-left {
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
    }
    .hero-shield {
        width: 48px; height: 48px;
        min-width: 48px;
        background: linear-gradient(135deg, #00BCD4 0%, #4CAF50 100%);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        font-weight: 800;
        color: #fff;
        box-shadow: 0 4px 16px rgba(0, 188, 212, 0.3);
        animation: subtleFloat 4s ease-in-out infinite;
        letter-spacing: -1px;
    }
    .hero-title {
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(1.4rem, 3vw, 2.1rem);
        font-weight: 800;
        color: var(--text-dark);
        letter-spacing: -0.5px;
        margin: 0;
        line-height: 1.1;
    }
    .hero-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(0.65rem, 1.2vw, 0.82rem);
        color: var(--text-muted);
        margin: 2px 0 0 0;
        letter-spacing: 0.1px;
        line-height: 1.3;
    }
    .live-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 188, 212, 0.1);
        border: 1.5px solid rgba(0, 188, 212, 0.3);
        border-radius: 24px;
        padding: 7px 18px;
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--accent-deep);
        letter-spacing: 0.5px;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .live-dot {
        width: 8px; height: 8px;
        background: var(--accent-deep);
        border-radius: 50%;
        animation: liveDot 2s ease-in-out infinite;
    }

    /* ─── Stat Cards ─── */
    .stat-box {
        background: var(--bg-card);
        border-radius: var(--radius);
        border: 1.5px solid var(--border);
        padding: 1.3rem 1rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
        animation: cardEntrance 0.5s ease both;
        position: relative;
        overflow: hidden;
    }
    .stat-box::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent-deep));
        border-radius: var(--radius) var(--radius) 0 0;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .stat-box:hover {
        border-color: var(--border-hover);
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }
    .stat-box:hover::after { opacity: 1; }

    .stat-number {
        font-size: clamp(1.8rem, 3.5vw, 2.5rem);
        font-weight: 800;
        color: var(--text-dark);
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: clamp(0.55rem, 1vw, 0.7rem);
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-top: 2px;
    }
    .sparkline-container {
        margin-top: 8px;
        height: 24px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }
    .sparkline-container svg {
        width: 85%;
        height: 24px;
    }

    /* ─── Zone Cards ─── */
    .zone-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.1rem;
        border: 1.5px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 0.5rem;
        box-shadow: var(--shadow-md);
        animation: cardEntrance 0.5s ease both;
        min-width: 0;
    }
    .zone-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--border-hover);
    }
    .zone-card.leak {
        border-color: rgba(192, 57, 43, 0.45);
        animation: alertPulse 2s ease-in-out infinite;
    }
    .zone-card.shortage {
        border-color: rgba(214, 137, 16, 0.45);
        animation: alertPulseOrange 2s ease-in-out infinite;
    }
    .zone-card.normal {
        animation: borderGlow 3s ease-in-out infinite, cardEntrance 0.5s ease both;
    }

    .zone-title {
        font-size: clamp(0.8rem, 1.2vw, 0.95rem);
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .zone-status {
        font-size: 0.65rem;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 20px;
        display: inline-block;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .status-normal {
        background: var(--accent);
        color: var(--text-dark);
        border: 1px solid var(--accent-deep);
    }
    .status-leak {
        background: rgba(192, 57, 43, 0.12);
        color: #c0392b;
        border: 1px solid rgba(192, 57, 43, 0.35);
    }
    .status-shortage {
        background: rgba(214, 137, 16, 0.12);
        color: #d68910;
        border: 1px solid rgba(214, 137, 16, 0.35);
    }

    .zone-metrics {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: 12px;
    }
    .zone-metric-item {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 3px 0;
        border-bottom: 1px solid rgba(26, 35, 126, 0.05);
    }
    .zone-metric-item:last-child { border-bottom: none; }

    .metric-val {
        font-size: clamp(0.85rem, 1.5vw, 1.05rem);
        font-weight: 700;
        color: var(--text-dark);
        white-space: nowrap;
    }
    .metric-val small {
        font-size: 0.6rem;
        color: var(--text-muted);
        font-weight: 400;
    }
    .metric-label {
        font-size: clamp(0.5rem, 0.9vw, 0.6rem);
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* ─── Section Titles ─── */
    .section-title {
        font-size: clamp(0.9rem, 1.5vw, 1.1rem);
        font-weight: 700;
        color: var(--text-dark);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.8rem;
        padding-bottom: 8px;
        background-image: url("data:image/svg+xml,%3Csvg width='100%25' height='10' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 5c20 0 20-5 40-5s20 5 40 5 20-5 40-5 20 5 40 5' stroke='%2300BCD4' stroke-opacity='0.5' stroke-width='2' fill='none'/%3E%3C/svg%3E");
        background-repeat: repeat-x;
        background-position: bottom left;
        border-bottom: none;
        padding-bottom: 12px;
    }
    .section-dot {
        width: 8px; height: 8px;
        background: var(--accent-deep);
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* ─── Live Agent Activity Panel ─── */
    .agent-panel {
        background: var(--bg-card);
        border-radius: var(--radius);
        border: 1.5px solid var(--border);
        padding: 1rem;
        box-shadow: var(--shadow-md);
        animation: cardEntrance 0.5s ease both;
    }
    .agent-panel-title {
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--text-dark);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(26, 35, 126, 0.1);
        display: flex;
        align-items: center;
        gap: 7px;
    }
    .agent-panel-dot {
        width: 7px; height: 7px;
        background: var(--accent-deep);
        border-radius: 50%;
        animation: liveDot 2s ease-in-out infinite;
        flex-shrink: 0;
    }
    .agent-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 6px;
        border-bottom: 1px solid rgba(26, 35, 126, 0.05);
        border-radius: 8px;
        transition: background 0.2s;
    }
    .agent-item:hover { background: rgba(76, 175, 80, 0.1); }
    .agent-item:last-child { border-bottom: none; }
    .agent-indicator {
        width: 8px; height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .agent-indicator.perception { background: #00BCD4; }
    .agent-indicator.reasoning { background: #4CAF50; }
    .agent-indicator.manager { background: #1A237E; }
    .agent-indicator.action { background: #00BCD4; }
    .agent-indicator.notification { background: #4CAF50; }
    .agent-name {
        font-size: clamp(0.65rem, 1vw, 0.78rem);
        font-weight: 500;
        color: var(--text-dark);
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .agent-status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
        animation: agentStatusPulse 2s ease-in-out infinite;
    }
    .agent-status-dot.active { background: var(--accent-deep); color: var(--accent-deep); }
    .agent-status-dot.idle { background: var(--text-muted); color: var(--text-muted); }
    .agent-log-scroll {
        margin-top: 8px;
        max-height: 120px;
        overflow-y: auto;
        border-top: 1px solid rgba(26, 35, 126, 0.08);
        padding-top: 6px;
    }
    .agent-log-entry {
        font-size: 0.58rem;
        color: var(--text-muted);
        padding: 2px 0 2px 8px;
        border-left: 2px solid rgba(0, 188, 212,0.25);
        margin-bottom: 2px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* ─── Log Entries ─── */
    .log-entry {
        font-family: 'Roboto', monospace;
        font-size: 0.72rem;
        padding: 6px 10px;
        border-left: 3px solid rgba(26, 35, 126, 0.12);
        margin-bottom: 3px;
        color: var(--text-dark);
        background: rgba(240, 249, 250, 0.4);
        border-radius: 0 8px 8px 0;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .log-entry.WARNING { border-left-color: var(--orange); color: #8a6d11; }
    .log-entry.ERROR { border-left-color: var(--red); color: #922b21; }
    .log-entry.INFO { border-left-color: var(--accent-deep); }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FAFAFA 0%, #ECEFF1 100%) !important;
        border-right: 1.5px solid rgba(0, 188, 212, 0.2) !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Montserrat', sans-serif !important;
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        font-size: clamp(1rem, 2vw, 1.25rem) !important;
    }
    [data-testid="stSidebar"] .stMarkdown h4 {
        font-family: 'Montserrat', sans-serif !important;
        color: var(--text-dark) !important;
        font-size: clamp(0.8rem, 1.5vw, 0.95rem) !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] span {
        color: var(--text-dark) !important;
    }

    /* ─── Buttons ─── */
    div[data-testid="stButton"] button {
        border-radius: 10px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: clamp(0.75rem, 1.2vw, 0.88rem);
        padding: 0.55rem 1rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1.5px solid var(--accent) !important;
        background: linear-gradient(135deg, var(--accent), #4CAF50) !important;
        color: var(--text-dark) !important;
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    div[data-testid="stButton"] button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%; right: 0; bottom: 0;
        width: 200%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transition: left 0.5s;
    }
    div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, var(--accent-deep), var(--accent)) !important;
        border-color: var(--accent-deep) !important;
        color: #ffffff !important;
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    div[data-testid="stButton"] button:hover::before {
        left: 100%;
    }
    div[data-testid="stButton"] button:active {
        transform: translateY(0px);
        box-shadow: var(--shadow-sm);
    }

    /* Streamlit element overrides */
    .stSelectbox > div > div {
        background: rgba(240, 249, 250, 0.8) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-dark) !important;
    }
    div[data-testid="stCheckbox"] p,
    div[data-testid="stCheckbox"] span,
    .stCheckbox label span,
    .stCheckbox label div p {
        color: var(--text-dark) !important;
    }
    div[data-testid="stExpander"] {
        background: rgba(240, 249, 250, 0.4) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    div[data-testid="stExpander"] summary span {
        color: var(--text-dark) !important;
    }
    .stDataFrame {
        border-radius: var(--radius);
        overflow: hidden;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: var(--text-dark) !important;
    }

    /* ─── RESPONSIVE: Tablet (< 1024px) ─── */
    @media (max-width: 1024px) {
        .main .block-container {
            padding: 0.8rem 1rem;
        }
        .hero-header {
            gap: 8px;
        }
        .hero-shield {
            width: 40px; height: 40px; min-width: 40px;
            font-size: 0.95rem;
        }
        .stat-box {
            padding: 1rem 0.8rem;
        }
        .zone-card {
            padding: 0.9rem;
        }
    }

    /* ─── RESPONSIVE: Mobile (< 768px) ─── */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem 0.5rem;
        }
        .hero-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }
        .hero-left {
            gap: 10px;
        }
        .hero-shield {
            width: 36px; height: 36px; min-width: 36px;
            font-size: 0.85rem;
            border-radius: 10px;
        }
        .live-badge {
            font-size: 0.65rem;
            padding: 5px 12px;
        }
        .stat-box {
            padding: 0.8rem 0.6rem;
            border-radius: 12px;
        }
        .zone-card {
            padding: 0.8rem;
            border-radius: 12px;
        }
        .agent-panel {
            border-radius: 12px;
            padding: 0.8rem;
        }
        .section-title {
            font-size: 0.9rem;
        }
    }

    /* ─── RESPONSIVE: Small Mobile (< 480px) ─── */
    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.3rem;
        }
        .stat-box {
            padding: 0.7rem 0.5rem;
        }
        .stat-number {
            font-size: 1.5rem;
        }
        .stat-label {
            font-size: 0.5rem;
            letter-spacing: 0.8px;
        }
        .zone-card {
            padding: 0.7rem;
        }
        .zone-title {
            font-size: 0.8rem;
        }
        .zone-status {
            font-size: 0.55rem;
            padding: 3px 8px;
        }
        .metric-val {
            font-size: 0.8rem;
        }
        .metric-label {
            font-size: 0.5rem;
        }
        .log-entry {
            font-size: 0.6rem;
            padding: 4px 6px;
        }
    }

    /* Log container */
    .log-container {
        max-height: 400px;
        overflow-y: auto;
        border-radius: var(--radius);
        padding: 8px;
        background: rgba(240, 249, 250, 0.3);
        border: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <div class="hero-left">
        <div class="hero-shield">UG</div>
        <div>
            <div class="hero-title">UtilityGuard</div>
            <div class="hero-subtitle">Autonomous Multi-Agent System for Real-Time Water Utility Leak &amp; Shortage Management</div>
        </div>
    </div>
    <div class="live-badge">
        <div class="live-dot"></div>
        LIVE &bull; Autonomous Agents Active
    </div>
</div>
""", unsafe_allow_html=True)


# ── Helper: determine zone status from recent events ──────────────────────────

def _get_zone_statuses():
    """Return dict zone_id -> (status, event_dict|None)."""
    statuses = {}
    events = memory.get_events(limit=200)
    latest = {}
    for e in events:
        zid = e.get("zone_id")
        if zid:
            latest[zid] = e

    for zone_id in ZONE_BASELINES:
        evt = latest.get(zone_id)
        if evt:
            issue = evt.get("issue_type", "NORMAL")
            ts = evt.get("timestamp", "")
            try:
                evt_time = datetime.fromisoformat(ts)
                age = (datetime.utcnow() - evt_time).total_seconds()
                if age > 300:
                    issue = "NORMAL"
            except Exception:
                pass
            statuses[zone_id] = (issue, evt)
        else:
            statuses[zone_id] = ("NORMAL", None)

    return statuses


# ── Helper: Generate sparkline SVG ────────────────────────────────────────────

def _sparkline_svg(values, color="#00BCD4"):
    """Generate a tiny SVG sparkline from a list of values."""
    if not values or len(values) < 2:
        values = [random.randint(2, 8) for _ in range(8)]
    w, h = 100, 24
    n = len(values)
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1
    points = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * w
        y = h - ((v - mn) / rng) * (h - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")
    path = "M" + "L".join(points)
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="0.55"'
        f' stroke-dasharray="200" stroke-dashoffset="200"'
        f' style="animation: sparklineAnim 2s ease forwards;"/>'
        f'</svg>'
    )


# ── Sidebar: Controls ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Controls")

    st.markdown("---")
    st.markdown("#### Simulation")

    sim_zone = st.selectbox(
        "Select Zone",
        list(ZONE_BASELINES.keys()),
        index=2,
        format_func=lambda x: x.replace("_", " ").title(),
        key="sim_zone",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Leak", key="sim_leak", use_container_width=True):
            with st.spinner("Running leak simulation..."):
                result = simulate_leak(sim_zone)
            st.success(f"Leak simulated in {sim_zone}!")
            st.rerun()

    with col2:
        if st.button("Simulate Shortage", key="sim_short", use_container_width=True):
            with st.spinner("Running shortage simulation..."):
                result = simulate_shortage(sim_zone)
            st.success(f"Shortage simulated in {sim_zone}!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### Manual Cycle")

    if st.button("Run Normal Cycle", key="run_cycle", use_container_width=True):
        with st.spinner("Running cycle..."):
            result = run_cycle()
        st.success("Cycle completed!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### Auto-Refresh")
    auto_refresh = st.checkbox("Enable auto-refresh (10s)", value=False)

    st.markdown("---")
    st.markdown(
        f"<small style='color:var(--text-muted)'>Last updated: "
        f"{datetime.utcnow().strftime('%H:%M:%S UTC')}</small>",
        unsafe_allow_html=True,
    )

# ── Stats Row ──────────────────────────────────────────────────────────────────

events = memory.get_events(limit=500)
total_events = len(events)
leaks = sum(1 for e in events if e.get("issue_type") == "LEAK")
shortages = sum(1 for e in events if e.get("issue_type") == "SHORTAGE")
actions_taken = sum(1 for e in events if e.get("action_success"))

stat_cols = st.columns(4)
stats = [
    ("Total Events", total_events, "#00BCD4"),
    ("Leaks Detected", leaks, "#1A237E"),
    ("Shortages Detected", shortages, "#4CAF50"),
    ("Actions Taken", actions_taken, "#1A237E"),
]
for col, (label, value, color) in zip(stat_cols, stats):
    sparkline = _sparkline_svg([random.randint(max(0, value-3), value+3) for _ in range(8)], color)
    with col:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{value}</div>'
            f'<div class="stat-label">{label}</div>'
            f'<div class="sparkline-container">{sparkline}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("")

# ── Main Content: Zone Status + Live Agent Activity ───────────────────────────

main_col, agent_col = st.columns([5.5, 1.3])

with main_col:
    st.markdown('<div class="section-title"><span class="section-dot"></span> Zone Status</div>', unsafe_allow_html=True)

    zone_statuses = _get_zone_statuses()
    readings = load_last_readings()
    readings_by_zone = {r.zone_id: r for r in readings} if readings else {}

    zone_cols = st.columns(5)
    for col, zone_id in zip(zone_cols, ZONE_BASELINES):
        status, evt = zone_statuses.get(zone_id, ("NORMAL", None))
        css_class = status.lower() if status in ("LEAK", "SHORTAGE") else "normal"
        status_class = f"status-{status.lower()}" if status in ("LEAK", "SHORTAGE") else "status-normal"

        reading = readings_by_zone.get(zone_id)
        pressure = reading.pressure_psi if reading else 0
        flow = reading.flow_rate_lps if reading else 0
        consumption = reading.consumption_m3 if reading else 0

        zone_display = zone_id.replace("_", " ").title()

        with col:
            st.markdown(
                f'<div class="zone-card {css_class}">'
                f'  <div class="zone-title">{zone_display}</div>'
                f'  <div class="zone-status {status_class}">{status}</div>'
                f'  <div class="zone-metrics">'
                f'    <div class="zone-metric-item">'
                f'      <div class="metric-label">Pressure</div>'
                f'      <div class="metric-val">{pressure:.1f} <small>psi</small></div>'
                f'    </div>'
                f'    <div class="zone-metric-item">'
                f'      <div class="metric-label">Flow Rate</div>'
                f'      <div class="metric-val">{flow:.1f} <small>lps</small></div>'
                f'    </div>'
                f'    <div class="zone-metric-item">'
                f'      <div class="metric-label">Consumption</div>'
                f'      <div class="metric-val">{consumption:.1f} <small>m3</small></div>'
                f'    </div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )

with agent_col:
    # ── Live Agent Activity Panel ──
    agents_info = [
        ("Perception", "perception", True),
        ("Reasoning", "reasoning", True),
        ("Manager", "manager", True),
        ("Action", "action", True),
        ("Notification", "notification", True),
    ]

    # Get recent logs for activity feed
    recent_logs = get_dashboard_logs(limit=8)
    log_html = ""
    if recent_logs:
        for entry in reversed(recent_logs[:6]):
            ts = entry.get("timestamp", "")[-8:]
            agent = entry.get("agent", "SYS")
            msg = entry.get("message", "")[:40]
            log_html += f'<div class="agent-log-entry"><strong>{agent}</strong> {msg}</div>'
    else:
        log_html = '<div class="agent-log-entry">Awaiting agent activity...</div>'

    agents_html = ""
    for name, cls, active in agents_info:
        dot_cls = "active" if active else "idle"
        agents_html += (
            f'<div class="agent-item">'
            f'  <div class="agent-indicator {cls}"></div>'
            f'  <div class="agent-name">{name}</div>'
            f'  <div class="agent-status-dot {dot_cls}"></div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="agent-panel">'
        f'  <div class="agent-panel-title"><div class="agent-panel-dot"></div> Live Agent Activity</div>'
        f'  {agents_html}'
        f'  <div class="agent-log-scroll">{log_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("")

# ── Two-column layout: Logs + Events ──────────────────────────────────────────

log_col, event_col = st.columns([1, 1])

with log_col:
    st.markdown('<div class="section-title"><span class="section-dot"></span> Agent Logs</div>', unsafe_allow_html=True)
    logs = get_dashboard_logs(limit=50)
    if logs:
        log_html = ""
        for entry in reversed(logs):
            level = entry.get("level", "INFO")
            ts = entry.get("timestamp", "")[:19]
            agent = entry.get("agent", "")
            msg = entry.get("message", "")
            log_html += (
                f'<div class="log-entry {level}">'
                f'<span style="color:var(--text-muted)">{ts}</span> '
                f'<strong>[{agent}]</strong> {msg}'
                f'</div>'
            )
        st.markdown(
            f'<div class="log-container">{log_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No logs yet. Run a cycle or simulation to see agent activity.")

with event_col:
    st.markdown('<div class="section-title"><span class="section-dot"></span> Event History</div>', unsafe_allow_html=True)
    events_display = memory.get_events(limit=20)
    if events_display:
        rows = []
        for e in reversed(events_display):
            rows.append({
                "Time": e.get("timestamp", "")[:19],
                "Zone": e.get("zone_id", ""),
                "Issue": e.get("issue_type", ""),
                "Severity": e.get("severity", ""),
                "Confidence": f"{e.get('confidence', 0):.0%}",
                "Action": e.get("action", ""),
                "Success": "Yes" if e.get("action_success") else "No",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No events recorded yet. Run a simulation to generate events.")

# ── Summary Reports ────────────────────────────────────────────────────────────

st.markdown('<div class="section-title"><span class="section-dot"></span> Cycle Summary Reports</div>', unsafe_allow_html=True)
summaries = memory.get_cycle_summaries(limit=5)
if summaries:
    for s in reversed(summaries):
        cycle_id = s.get("cycle_id", "?")
        ts = s.get("timestamp", "")[:19]
        status = s.get("status", "unknown")

        reasonings = s.get("reasonings", [])
        anomalies = [r for r in reasonings if r.get("issue_type") != "NORMAL"]
        actions = s.get("actions", [])
        notifs = s.get("notifications", [])

        with st.expander(f"Cycle {cycle_id} — {ts} — {status.upper()}", expanded=False):
            st.markdown(f"**Zones analyzed:** {len(reasonings)}")
            st.markdown(f"**Anomalies found:** {len(anomalies)}")
            if anomalies:
                for a in anomalies:
                    st.markdown(
                        f"- **{a['issue_type']}** in `{a['affected_zone']}` "
                        f"(severity: {a['severity']}, confidence: {a['confidence']:.0%})"
                    )
                    if a.get("reasoning_steps"):
                        st.markdown("  **Reasoning:**")
                        for step in a["reasoning_steps"]:
                            st.markdown(f"  - {step}")

            st.markdown(f"**Actions executed:** {len(actions)}")
            st.markdown(f"**Notifications sent:** {len(notifs)}")
else:
    st.info("No cycle summaries yet. Run a cycle to generate a report.")

# ── CRM Entries ────────────────────────────────────────────────────────────────

st.markdown('<div class="section-title"><span class="section-dot"></span> Mock CRM Entries</div>', unsafe_allow_html=True)
if os.path.exists(settings.CRM_FILE):
    with open(settings.CRM_FILE, "r") as f:
        try:
            crm_data = json.load(f)
            if crm_data:
                rows = []
                for entry in reversed(crm_data[-20:]):
                    rows.append({
                        "Time": entry.get("timestamp", "")[:19],
                        "Zone": entry.get("zone_id", ""),
                        "Action": entry.get("action", ""),
                        "Issue": entry.get("issue_type", ""),
                        "Severity": entry.get("severity", ""),
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("CRM is empty.")
        except json.JSONDecodeError:
            st.warning("CRM file is corrupted.")
else:
    st.info("No CRM entries yet.")

# ── Auto-refresh ───────────────────────────────────────────────────────────────

if auto_refresh:
    time.sleep(10)
    st.rerun()
