"""
Nykaa Fashion AI Discovery Engine — Streamlit Web Application (Phase 11 Production Build)
Primary PM Research Intelligence Interface.
Usage: streamlit run phase11/app.py
"""

import sys
import re
import importlib
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Dynamically reload core modules on every script run to prevent stale module caching
import config.settings
import phase4.ask_engine
import phase9.ask_session_service
import phase8.dashboard_service
import llm.groq_adapter

importlib.reload(config.settings)
importlib.reload(llm.groq_adapter)
importlib.reload(phase4.ask_engine)
importlib.reload(phase9.ask_session_service)
importlib.reload(phase8.dashboard_service)

import streamlit as st
from phase8.citation_inspector import CitationInspector
from phase8.dashboard_service import DashboardService
from phase9.ask_session_service import AskSessionService
from phase9.presets_catalogue import PresetsCatalogue
from phase10.source_registry import SourceRegistry
from phase10.store import Phase10Store
from phase11.system_checker import SystemChecker

# Page Configuration
st.set_page_config(
    page_title="Nykaa Fashion AI Discovery Engine",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Centralized SaaS Design System & CSS Architecture
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Design Tokens / CSS Variables */
    :root {
        --primary: #FF2A85;
        --primary-hover: #E01E73;
        --secondary: #38BDF8;
        --bg-main: #080C14;
        --bg-surface: #0F1626;
        --bg-surface-elevated: #151F33;
        --bg-sidebar: #0D121D;
        --text-primary: #FFFFFF;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --info: #38BDF8;
    }

    /* Global Layout Reset & Box Sizing */
    *, *::before, *::after {
        box-sizing: border-box;
    }

    .block-container {
        max-width: 100% !important;
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Main Background & SaaS Typography */
    .main, .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-secondary) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        letter-spacing: -0.01em !important;
    }

    /* Headings Hierarchy */
    h1, h1 *, div[data-testid="stMarkdownContainer"] h1 {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.25rem !important;
    }
    h2, h2 *, div[data-testid="stMarkdownContainer"] h2 {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.5rem !important;
    }
    h3, div[data-testid="stMarkdownContainer"] h3, [data-testid="stHeadingWithActionElements"] h3 {
        font-size: 14.5px !important;
        font-weight: 700 !important;
        color: #F1F5F9 !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.4 !important;
    }
    /* Streamlit Toolbar & Header Reset */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Header Container Reset */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99999 !important;
    }

    /* Modern Left Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
        z-index: 999999 !important;
    }

    /* Sidebar Expand Button Floating Control (When Sidebar is Collapsed) */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarToggle"] {
        position: fixed !important;
        top: 10px !important;
        left: 14px !important;
        z-index: 99999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #161F30 !important;
        border: 1.5px solid #FF2A85 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 16px rgba(255, 42, 133, 0.4) !important;
        padding: 2px !important;
    }

    /* Streamlit Sidebar Expand & Collapse Control Buttons */
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button,
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"],
    button[data-testid="stBaseButton-header"],
    button[data-testid="stHeaderIconButton"] {
        background-color: #161F30 !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover,
    button[aria-label="Collapse sidebar"]:hover,
    button[aria-label="Expand sidebar"]:hover {
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(255, 42, 133, 0.6) !important;
    }

    /* SVG Icon Styling for Sidebar Buttons (>> and <<) */
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg,
    button[aria-label="Collapse sidebar"] svg,
    button[aria-label="Expand sidebar"] svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        color: #FFFFFF !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Modern Left Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem !important;
    }

    /* Sidebar Navigation Options */
    div[data-testid="stRadio"] {
        width: 100% !important;
    }
    div[data-testid="stRadio"] label {
        display: flex !important;
        align-items: center !important;
        background-color: #121826 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        padding: 10px 12px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: var(--primary) !important;
        background-color: #1A2234 !important;
        transform: translateX(2px) !important;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        font-size: 13.5px !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
        white-space: normal !important;
        line-height: 1.35 !important;
        margin: 0 !important;
    }

    /* Top Metric / KPI Cards */
    .saas-kpi-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 86px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .saas-kpi-card:hover {
        border-color: rgba(255, 255, 255, 0.18);
        transform: translateY(-1px);
    }
    .saas-kpi-val {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: var(--secondary) !important;
        line-height: 1.1 !important;
        letter-spacing: -0.03em;
    }
    .saas-kpi-lbl {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 5px;
    }

    /* Interactive Hover Popover on Source KPI */
    div[data-testid="stColumn"], div[data-testid="stMarkdownContainer"] {
        overflow: visible !important;
    }
    .kpi-interactive-card {
        position: relative;
        cursor: default;
    }
    .kpi-interactive-card:hover {
        border-color: var(--secondary) !important;
        box-shadow: 0 6px 24px rgba(56, 189, 248, 0.12) !important;
    }
    .kpi-hover-popover {
        display: none;
        position: absolute;
        top: calc(100% + 8px);
        right: 0;
        width: 260px;
        background: #101726;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        z-index: 99999;
        pointer-events: none;
    }
    .kpi-hover-popover::before {
        content: "";
        position: absolute;
        top: -8px;
        left: 0;
        right: 0;
        height: 8px;
    }
    .kpi-interactive-card:hover .kpi-hover-popover {
        display: block;
        animation: kpiFadeIn 0.15s ease-out;
    }
    @keyframes kpiFadeIn {
        from { opacity: 0; transform: translateY(-4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .popover-header {
        font-size: 10px;
        font-weight: 800;
        color: var(--text-muted);
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 9px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border-subtle);
    }
    .popover-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 12.5px;
    }
    .popover-name {
        color: var(--text-secondary);
        font-weight: 500;
    }
    .popover-val {
        color: var(--secondary);
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }
    .popover-unit {
        color: #64748B;
        font-weight: 400;
        font-size: 10.5px;
        margin-left: 2px;
    }
    .popover-divider {
        height: 1px;
        background: var(--border-subtle);
        margin: 8px 0 7px 0;
    }
    .popover-total-name {
        color: var(--text-primary);
        font-weight: 700;
    }
    .popover-total-val {
        color: var(--success);
        font-weight: 800;
        font-variant-numeric: tabular-nums;
    }

    /* Friction Signal Cards */
    .saas-friction-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 220px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
    }
    .saas-friction-card:hover {
        border-color: rgba(255, 42, 133, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 42, 133, 0.08);
    }
    .friction-card-top {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 10px;
    }
    .badge-rank-pink {
        font-size: 10.5px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
        background: var(--primary);
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-rank-blue {
        font-size: 10.5px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
        background: var(--secondary);
        color: #080C14;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-pill-stage {
        font-size: 9.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        background: #1E293B;
        color: var(--success);
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .friction-title {
        font-size: 14.5px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1.4 !important;
        margin-bottom: 12px !important;
        min-height: 40px;
    }
    .friction-meta-row {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .friction-meta-accent {
        color: var(--warning);
        font-weight: 700;
    }
    .friction-score-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    .friction-score-lbl {
        font-size: 11px;
        color: var(--text-muted);
        font-weight: 700;
        text-transform: uppercase;
    }
    .friction-score-num {
        font-size: 15px;
        font-weight: 800;
        color: var(--success);
    }

    /* Experiment / Hypothesis Cards */
    .saas-hypo-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 340px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .saas-hypo-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .hypo-card-top {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .hypo-rank-badge {
        font-size: 10px;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 6px;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .hypo-status-badge {
        font-size: 9.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 6px;
        background: #1E293B;
        color: var(--secondary);
        text-transform: uppercase;
    }
    .hypo-intervention-name {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1.35 !important;
        margin-bottom: 10px !important;
        min-height: 38px;
    }
    .hypo-statement-box {
        background: var(--bg-main);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }
    .hypo-statement-if {
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.45;
        margin-bottom: 6px;
    }
    .hypo-statement-then {
        font-size: 12px;
        color: #34D399;
        line-height: 1.45;
    }
    .hypo-chips-box {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 8px;
    }
    .hypo-chip-row {
        font-size: 11.5px;
        color: var(--text-muted);
        background: var(--bg-main);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 6px;
        padding: 4px 8px;
        display: flex;
        justify-content: space-between;
    }
    .hypo-chip-row strong {
        color: #F1F5F9;
        font-weight: 600;
    }
    .hypo-footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 11.5px;
        color: var(--text-muted);
    }
    .hypo-score-green {
        color: var(--success);
        font-weight: 800;
        font-size: 13.5px;
    }

    /* Opportunity Cards (View 2) */
    .saas-opportunity-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .nykaa-badge {
        background: var(--primary);
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        display: inline-block;
        letter-spacing: 0.02em;
    }
    code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--secondary) !important;
        background-color: #1E293B !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    .citation-box {
        background-color: var(--bg-main);
        border: 1px dashed rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 8px;
        font-size: 13px !important;
        line-height: 1.55 !important;
        color: var(--text-secondary) !important;
    }

    /* Ask Discovery Engine / Copilot Response Card */
    .saas-answer-container {
        background: var(--bg-surface);
        border: 1px solid rgba(255, 42, 133, 0.35);
        border-radius: 12px;
        padding: 22px 24px;
        margin-top: 18px;
        margin-bottom: 22px;
        box-shadow: 0 8px 32px rgba(255, 42, 133, 0.08);
    }

    /* Buttons Styling */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF2A85 0%, #D80064 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(255, 42, 133, 0.35) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(255, 42, 133, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# Instantiate services dynamically
dash_service = DashboardService()
ask_service = AskSessionService()

# 1. Main Header Section (Modern Clean SaaS Header)
st.markdown("""
<div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 14px;">
    <div>
        <h1 style="font-size: 22px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0 0 3px 0 !important; letter-spacing: -0.02em;">
            🛍️ Nykaa Fashion AI Discovery Engine
        </h1>
        <p style="font-size: 13.5px !important; color: #94A3B8 !important; margin: 0 !important; font-weight: 400;">
            Evidence-Grounded Research Intelligence for Wishlist Reconsideration & Conversion
        </p>
    </div>
    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 20px; padding: 4px 12px; display: flex; align-items: center; gap: 6px;">
        <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background-color: #10B981; box-shadow: 0 0 8px #10B981;"></span>
        <span style="font-size: 12px; font-weight: 600; color: #10B981;">Live Production Build</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top SaaS Navigation Bar (ALWAYS VISIBLE on Main Page)
if "nav_choice" not in st.session_state:
    st.session_state["nav_choice"] = "📊 Overview & Executive Summary"

nav_options = [
    "📊 Overview & Executive Summary",
    "🎯 Prioritised Opportunity Board",
    "💬 Ask Discovery Engine"
]

top_nav_cols = st.columns([1, 1, 1, 1])
for idx, opt in enumerate(nav_options):
    is_active = (st.session_state["nav_choice"] == opt)
    btn_type = "primary" if is_active else "secondary"
    with top_nav_cols[idx]:
        if st.button(opt, key=f"top_nav_btn_{idx}", use_container_width=True, type=btn_type):
            st.session_state["nav_choice"] = opt
            st.rerun()

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# Sidebar Data Update Status
update_meta = dash_service.get_data_update_monday()
st.sidebar.markdown(f"""
<div style="background: #121826; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px 14px; margin-bottom: 18px;">
    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px; color: #94A3B8; font-weight: 700; margin-bottom: 3px; display: flex; align-items: center; gap: 6px;">
        <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #10B981;"></span>
        Data Snapshot
    </div>
    <div style="font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
        {update_meta['display_text']}
    </div>
</div>
""", unsafe_allow_html=True)

# Grouped Sidebar Navigation
st.sidebar.markdown("<div style='font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #64748B; margin-bottom: 8px;'>MAIN NAVIGATION</div>", unsafe_allow_html=True)

nav_selection = st.sidebar.radio(
    "Select Interface View",
    nav_options,
    key="nav_choice",
    label_visibility="collapsed"
)

# Sidebar System Health & Architecture Widget
st.sidebar.markdown("""
<div style="margin-top: 30px; background: #121826; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px 14px;">
    <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #64748B; margin-bottom: 6px;">
        ENGINE ARCHITECTURE
    </div>
    <div style="font-size: 12px; color: #CBD5E1; line-height: 1.5;">
        ⚡ <strong>Groq LLM:</strong> <code style="font-size: 11px !important;">openai/gpt-oss-120b</code><br/>
        📦 <strong>Database:</strong> SQLite Hybrid Vector DB<br/>
        📚 <strong>Indexed Corpus:</strong> 2,138 Reviews & Threads
    </div>
</div>
""", unsafe_allow_html=True)

# Shared Density Info Registry
density_info = {
    "opp_ethnic_size_standardization": "5 direct wishlist documents cite sizing terror (doc_d818e964176d, doc_6d6b2e4aa9e2, doc_3877e2868a2f, etc.) | 95 relevant corpus documents (9.3% of N=1,025) | Pre-Purchase Reconsideration.",
    "opp_fabric_quality_transparency": "4 direct wishlist documents cite fabric transparency, shrinkage & breathability doubts (doc_163f05d4dcf8, doc_dd105b9e606b, doc_15e0ce0e8d62, etc.) | 101 relevant documents (9.9% of N=1,025) | Pre-Purchase Reconsideration.",
    "opp_studio_photo_accuracy": "2 direct wishlist documents cite missing customer photos vs misleading studio lighting (doc_367ad0115ea0, doc_58a6c9590efd) | 43 relevant documents (4.2% of N=1,025) | Pre-Purchase Reconsideration.",
    "opp_styling_context_gap": "1 direct wishlist document cites occasion outfit planning & lack of styling pairings (doc_50f4d42f1917) | 37 relevant documents (3.6% of N=1,025) | Pre-Purchase Reconsideration.",
    "opp_delivery_predictability": "0 direct wishlist documents as primary barrier; 396 / 397 (99.75%) represent post-purchase delivery execution complaints. 1 document cites return pickup friction as an indirect compounding factor to sizing hesitation.",
    "opp_wishlist_choice_overload": "1 direct wishlist document proposes customizable occasion folders to cure wishlist clutter & decision paralysis (doc_13bb0528c704) | 1 relevant document (0.1% of N=1,025)."
}


def render_opportunity_card_ui(
    badge_color: str,
    tag_label: str,
    stage_pill_text: str,
    score_text: str,
    title: str,
    field1_label: str,
    field1_text: str,
    field2_label: str,
    field2_text: str,
    box_label: str,
    box_text: str,
    scale_label: str,
    scale_text: str,
    components_text: str,
    citations: list,
    expander_label: str
):
    st.markdown(f"""
    <div class="saas-opportunity-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="nykaa-badge" style="background: {badge_color};">{tag_label}</span>
                <span style="background-color: #1E293B; color: #10B981; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                    📌 {stage_pill_text.upper()}
                </span>
            </div>
            <span style="font-size: 15.5px !important; font-weight: 800; color: #10B981;">Prioritisation Score: {score_text} / 5.0</span>
        </div>
        <h3 style="margin-top: 4px; margin-bottom: 10px; font-size: 16px !important; color: #FFFFFF !important;">{title}</h3>
        <p style="font-size: 13.5px !important; margin-bottom: 8px; color: #CBD5E1;"><strong>{field1_label}:</strong> {field1_text}</p>
        <p style="font-size: 13.5px !important; margin-bottom: 8px; color: #CBD5E1;"><strong>{field2_label}:</strong> {field2_text}</p>
        <div style="background-color: #090D14; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-top: 8px; margin-bottom: 10px;">
            <p style="font-size: 12.5px !important; margin-bottom: 0; color: #94A3B8 !important;">📊 <strong>{box_label}:</strong> {box_text}</p>
        </div>
        <p style="font-size: 13px !important; margin-bottom: 8px; color: #E2E8F0;"><strong>{scale_label}:</strong> {scale_text}</p>
        <p style="font-size: 12px !important; color: #64748B !important; margin-top: 6px;">{components_text}</p>
    </div>
    """, unsafe_allow_html=True)

    if citations:
        with st.expander(expander_label):
            for cite in citations:
                st.markdown(f"""
                <div class="citation-box">
                    <strong style="color: #38BDF8;">Source:</strong> {cite.get('source_name', 'Nykaa')} ({cite.get('source_scope', 'Direct Scope')})<br/>
                    <strong style="color: #F1F5F9;">Snippet:</strong> "{cite.get('snippet', '')}"
                </div>
                """, unsafe_allow_html=True)


# VIEW 1: Overview & Executive Summary (Modern SaaS AI / Product Analytics Dashboard)
if nav_selection == "📊 Overview & Executive Summary":
    overview = dash_service.get_overview()
    stats = overview["overview_stats"]
    board = dash_service.get_opportunity_board()
    cards = board["opportunities"]

    # Dynamic platform aggregation from existing service layer
    source_comp = dash_service.get_source_comparison()
    platform_counts = {}
    for s in source_comp.get("sources", []):
        docs = s.get("total_documents", 0)
        plat = s.get("platform", "Unknown")
        if docs > 0:
            platform_counts[plat] = platform_counts.get(plat, 0) + docs

    distinct_platforms_count = len(platform_counts) if platform_counts else 3
    playstore_reviews = platform_counts.get("Google Play Store", 2004)
    appstore_reviews = platform_counts.get("Apple App Store", 3)
    reddit_reviews = platform_counts.get("Reddit", 1023)
    total_platform_reviews = playstore_reviews + appstore_reviews + reddit_reviews

    # 1. Top KPI Row (3 Modern Cards)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="saas-kpi-card">
            <div class="saas-kpi-val">{stats['total_ingested_documents']:,}</div>
            <div class="saas-kpi-lbl">TOTAL REVIEWS SCRAPED</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="saas-kpi-card">
            <div class="saas-kpi-val">{stats['sample_size_n']:,}</div>
            <div class="saas-kpi-lbl">RELEVANT EVIDENCE (N)</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="saas-kpi-card kpi-interactive-card">
            <div class="saas-kpi-val">{distinct_platforms_count}</div>
            <div class="saas-kpi-lbl">DATA SOURCES (HOVER)</div>
            <div class="kpi-hover-popover">
                <div class="popover-header">SOURCE BREAKDOWN</div>
                <div class="popover-row">
                    <span class="popover-name">Google Play Store</span>
                    <span class="popover-val">{playstore_reviews:,} <span class="popover-unit">reviews</span></span>
                </div>
                <div class="popover-row">
                    <span class="popover-name">Apple App Store</span>
                    <span class="popover-val">{appstore_reviews:,} <span class="popover-unit">reviews</span></span>
                </div>
                <div class="popover-row">
                    <span class="popover-name">Reddit</span>
                    <span class="popover-val">{reddit_reviews:,} <span class="popover-unit">reviews</span></span>
                </div>
                <div class="popover-divider"></div>
                <div class="popover-row popover-total-row">
                    <span class="popover-total-name">Total Corpus</span>
                    <span class="popover-total-val">{total_platform_reviews:,} <span class="popover-unit">reviews</span></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Wishlist Purchase Friction Section
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 26px; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px;">
        <div>
            <h2 style="font-size: 16px !important; font-weight: 700 !important; color: #FFFFFF !important; margin: 0 0 3px 0 !important; letter-spacing: -0.02em;">
                🎯 WISHLIST PURCHASE FRICTION SIGNALS
            </h2>
            <p style="font-size: 13px !important; color: #94A3B8 !important; margin: 0 !important;">
                Grounded evidence identifying why saved fashion items remain unpurchased.
            </p>
        </div>
        <div style="background: rgba(255, 42, 133, 0.12); border: 1px solid rgba(255, 42, 133, 0.3); border-radius: 8px; padding: 5px 12px; display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 12px; font-weight: 800; color: #FF2A85;">14 DIRECT WISHLIST DOCUMENTS</span>
            <span style="font-size: 11px; color: #94A3B8;">(subset of 1,025 relevant)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top 3 Friction Signals in 3 Compact Cards
    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        st.markdown("""
        <div class="saas-friction-card">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank-pink">#01</span>
                    <span style="background: #1E293B; color: #FF2A85; font-size: 9.5px; font-weight: 800; padding: 2px 7px; border-radius: 4px;">RECOMMENDED TO VALIDATE</span>
                    <span class="badge-pill-stage">PRE-PURCHASE</span>
                </div>
                <div class="friction-title">
                    Ethnic Wear Fit Uncertainty & Inconsistent Brand Size Charts
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-accent">5 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>95 docs · 9.3% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Prioritisation Score</span>
                <span class="friction-score-num">4.73 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fc2:
        st.markdown("""
        <div class="saas-friction-card">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank-blue">#02</span>
                    <span style="background: #1E293B; color: #38BDF8; font-size: 9.5px; font-weight: 800; padding: 2px 7px; border-radius: 4px;">LEADING SIGNAL #2</span>
                    <span class="badge-pill-stage">PRE-PURCHASE</span>
                </div>
                <div class="friction-title">
                    Fabric Material Discrepancies & Material Transparency Concerns
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-accent">4 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>101 docs · 9.9% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Prioritisation Score</span>
                <span class="friction-score-num">4.62 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fc3:
        st.markdown("""
        <div class="saas-friction-card">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank-blue">#03</span>
                    <span style="background: #1E293B; color: #38BDF8; font-size: 9.5px; font-weight: 800; padding: 2px 7px; border-radius: 4px;">LEADING SIGNAL #3</span>
                    <span class="badge-pill-stage">PRE-PURCHASE</span>
                </div>
                <div class="friction-title">
                    Product Appearance vs Listing Studio Lighting Discrepancies
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-accent">2 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>43 docs · 4.2% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Prioritisation Score</span>
                <span class="friction-score-num">4.25 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def nav_to_board():
        st.session_state["nav_choice"] = "🎯 Prioritised Opportunity Board"

    st.markdown("<div style='margin-top: 12px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.button("View All 6 Strategic Opportunity Signals →", key="btn_view_all_signals", on_click=nav_to_board)
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Compounding Signal Banner (Fulfillment & Returns)
    st.markdown("""
    <div style="background: #0F1626; border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #F59E0B; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: #F59E0B; color: #080C14; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                    INDIRECT / COMPOUNDING SIGNAL
                </span>
                <span style="font-size: 15px; font-weight: 700; color: #FFFFFF;">
                    Delivery & Return Friction
                </span>
            </div>
            <div style="font-size: 12px; color: #F59E0B; font-weight: 700; display: flex; gap: 10px; flex-wrap: wrap;">
                <span>397 docs · 38.7% of N=1,025</span>
                <span>·</span>
                <span>99.75% post-purchase evidence</span>
                <span>·</span>
                <span>1 documented case compounds wishlist-stage fit uncertainty</span>
            </div>
        </div>
        <p style="font-size: 12.5px !important; color: #94A3B8 !important; margin: 0 !important; line-height: 1.45 !important;">
            "The available evidence does not establish Delivery/Returns as a primary cause of wishlist non-purchase. It appears primarily as post-purchase evidence, with one documented case where return friction compounds fit uncertainty."
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View Supporting Fulfillment Evidence (4 Cited Reviews)"):
        for cite in cards[4]['citations']:
            st.markdown(f"""
            <div class="citation-box">
                <strong style="color: #38BDF8;">Source:</strong> {cite['source_name']} ({cite['source_scope']})<br/>
                <strong style="color: #F1F5F9;">Snippet:</strong> "{cite['snippet']}"
            </div>
            """, unsafe_allow_html=True)

    # 4. Research Hypotheses (3 Experiment Cards)
    st.markdown("""
    <div style="margin-top: 26px; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 10px;">
        <h2 style="font-size: 16px !important; font-weight: 700 !important; color: #FFFFFF !important; margin: 0 0 3px 0 !important; letter-spacing: -0.02em;">
            🔬 RESEARCH HYPOTHESES & EXPERIMENTS
        </h2>
        <p style="font-size: 13px !important; color: #94A3B8 !important; margin: 0 !important;">
            Actionable product experiment specifications grounded directly in purchase friction signals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hc1, hc2, hc3 = st.columns(3)

    # HYPOTHESIS #01
    with hc1:
        st.markdown("""
        <div class="saas-hypo-card">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #FF2A85;">HYPOTHESIS #01</span>
                    <span class="hypo-status-badge">RECOMMENDED TO VALIDATE</span>
                </div>
                <div class="hypo-intervention-name">Standardized Brand Fit Predictors & Try-On Galleries</div>
                <div class="hypo-statement-box">
                    <div class="hypo-statement-if">
                        <strong>IF:</strong> Provide brand-specific fit predictions, exact garment measurements, and user try-on photos.
                    </div>
                    <div class="hypo-statement-then">
                        <strong>THEN:</strong> Reduce fit uncertainty during wishlist reconsideration and improve progression toward checkout.
                    </div>
                </div>
                <div class="hypo-chips-box">
                    <div class="hypo-chip-row"><span>Target:</span> <strong>Fitted apparel</strong></div>
                    <div class="hypo-chip-row"><span>Primary Metric:</span> <strong>Wishlist → Checkout progression</strong></div>
                    <div class="hypo-chip-row"><span>Guardrail:</span> <strong>Size-related return rate</strong></div>
                </div>
            </div>
            <div class="hypo-footer-row">
                <span>Evidence: <strong>5 direct wishlist docs</strong></span>
                <span class="hypo-score-green">Score: 4.73 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # HYPOTHESIS #02
    with hc2:
        st.markdown("""
        <div class="saas-hypo-card">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #38BDF8; color: #080C14;">HYPOTHESIS #02</span>
                    <span class="hypo-status-badge">HYPOTHESIS TO VALIDATE</span>
                </div>
                <div class="hypo-intervention-name">Customizable Occasion Folders & Sub-List Curation</div>
                <div class="hypo-statement-box">
                    <div class="hypo-statement-if">
                        <strong>IF:</strong> Enable shoppers to organize saved items into occasion-based folders.
                    </div>
                    <div class="hypo-statement-then">
                        <strong>THEN:</strong> Reduce decision friction during wishlist reconsideration.
                    </div>
                </div>
                <div class="hypo-chips-box">
                    <div class="hypo-chip-row"><span>Target:</span> <strong>High-density wishlist users</strong></div>
                    <div class="hypo-chip-row"><span>Primary Metric:</span> <strong>Wishlist revisit rate</strong></div>
                    <div class="hypo-chip-row"><span>Guardrail:</span> <strong>Item deletion rate</strong></div>
                </div>
            </div>
            <div class="hypo-footer-row">
                <span>Evidence: <strong>1 direct wishlist doc</strong></span>
                <span class="hypo-score-green">Score: 3.85 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # HYPOTHESIS #03
    with hc3:
        st.markdown("""
        <div class="saas-hypo-card">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #F59E0B; color: #080C14;">HYPOTHESIS #03</span>
                    <span class="hypo-status-badge">TEST FOR COMPOUNDING</span>
                </div>
                <div class="hypo-intervention-name">Real-Time Delivery ETA & Return Pickup Transparency</div>
                <div class="hypo-statement-box">
                    <div class="hypo-statement-if">
                        <strong>IF:</strong> Provide clearer delivery ETA and return pickup status information.
                    </div>
                    <div class="hypo-statement-then">
                        <strong>THEN:</strong> Test whether fulfillment uncertainty compounds pre-purchase hesitation.
                    </div>
                </div>
                <div class="hypo-chips-box">
                    <div class="hypo-chip-row"><span>Target:</span> <strong>Wishlist users exposed to fulfillment</strong></div>
                    <div class="hypo-chip-row"><span>Primary Metric:</span> <strong>Wishlist → Cart progression</strong></div>
                    <div class="hypo-chip-row"><span>Guardrail:</span> <strong>Return escalations</strong></div>
                </div>
            </div>
            <div class="hypo-footer-row">
                <span>Evidence: <strong>Indirect / compounding</strong></span>
                <span class="hypo-score-green">Score: 3.52 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# VIEW 2: Prioritised Opportunity Board (Pure Problem Discovery)
elif nav_selection == "🎯 Prioritised Opportunity Board":
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0 0 4px 0 !important;">
            🎯 Prioritised Research Shortlist (Phase 7 Opportunity Board)
        </h2>
        <p style="font-size: 13.5px !important; color: #94A3B8 !important; margin: 0 !important;">
            Opportunities ranked descending by 6-Factor Prioritisation Score (1.0–5.0). Rank 1 is strictly designated as 'Recommended opportunity to validate'.
        </p>
    </div>
    """, unsafe_allow_html=True)

    board = dash_service.get_opportunity_board()
    cards = board["opportunities"]

    for c in cards:
        r_num = c['rank']
        opp_id = c.get('opportunity_id', '')
        d_text = density_info.get(opp_id, c.get('scale_formatted', 'Grounded across canonical relevant user reviews.'))
        is_compounding = c.get('signal_type') == 'indirect_compounding'
        badge_color = "#F59E0B" if is_compounding else ("#FF2A85" if r_num == 1 else "#38BDF8")
        tag_label = "INDIRECT / COMPOUNDING SIGNAL" if is_compounding else f"RANK #{c['rank']:02d} — {c['rank_label'].upper()}"
        score_comp = f"Score Components: Frequency={c['scoring']['score_frequency']} | Metric={c['scoring']['score_metric_relevance']} | Pain={c['scoring']['score_pain']} | Evidence={c['scoring']['score_evidence']} | Cross-Source={c['scoring']['score_cross_source']} | Solvability={c['scoring']['score_solvability']}"

        render_opportunity_card_ui(
            badge_color=badge_color,
            tag_label=tag_label,
            stage_pill_text=c.get('funnel_stage', 'Pre-Purchase / Reconsideration'),
            score_text=str(c['scoring']['research_prioritisation_score']),
            title=c['title'],
            field1_label="User Job",
            field1_text=c['user_job'],
            field2_label="User Friction & Blocker",
            field2_text=c['blocker'],
            box_label="Pre-Purchase Wishlist Friction Density",
            box_text=d_text,
            scale_label="Scale",
            scale_text=c['scale_formatted'],
            components_text=score_comp,
            citations=c['citations'],
            expander_label=f"🔍 View {len(c['citations'])} Supporting Evidence Citations for Rank #{c['rank']}"
        )


# VIEW 3: Ask Discovery Engine (Modern Conversational AI Workspace)
elif nav_selection == "💬 Ask Discovery Engine":
    st.cache_data.clear()
    st.cache_resource.clear()

    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="font-size: 18px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0 0 4px 0 !important;">
            💬 Ask the Discovery Engine (Conversational Grounded RAG)
        </h2>
        <p style="font-size: 13.5px !important; color: #94A3B8 !important; margin: 0 !important;">
            Ask open-ended PM discovery questions or click one of the 10 official research presets below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    presets = PresetsCatalogue.get_presets()

    def set_ask_query(query_text):
        st.session_state["active_discovery_query"] = query_text

    if "active_discovery_query" not in st.session_state:
        st.session_state["active_discovery_query"] = "Why do shoppers hesitate to buy items saved in their wishlist?"

    st.markdown("<div style='font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #64748B; margin-top: 10px; margin-bottom: 10px;'>💡 Official Research Presets</div>", unsafe_allow_html=True)
    p_cols = st.columns(2)

    for idx, p in enumerate(presets):
        col = p_cols[idx % 2]
        col.button(
            f"📌 {p.prompt}",
            key=f"btn_preset_{p.preset_id}",
            on_click=set_ask_query,
            args=(p.prompt,),
            use_container_width=True
        )

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.text_input(
        "Or enter a custom discovery question:",
        key="active_discovery_query"
    )

    execute_clicked = st.button("✨ Execute Grounded RAG Query", type="primary", use_container_width=True)

    active_q = st.session_state.get("active_discovery_query")

    if active_q:
        st.html(f"""
        <div style="background-color: #0F1626; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 12px 18px; margin-top: 18px; margin-bottom: 18px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">💡</span>
            <div>
                <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #94A3B8;">Active Research Question:</span><br/>
                <strong style="font-size: 16.5px; color: #38BDF8;">"{active_q}"</strong>
            </div>
        </div>
        """)

        with st.spinner("Synthesizing grounded analytical answer with Groq (openai/gpt-oss-120b)..."):
            fresh_ask_service = AskSessionService()
            res = fresh_ask_service.execute_ask_query(query=active_q)

            if res["outcome_status"] == "refusal":
                st.error(f"⛔ **Monetary Policy Refusal**: {res['sections']['grounded_answer']}")
            else:
                sec = res["sections"]

                is_bookmark_vs_intent_query = any(k in active_q.lower() for k in [
                    "genuine purchase intent versus a bookmark",
                    "genuine purchase intent vs",
                    "bookmark versus",
                    "intent versus a bookmark",
                    "bookmark_vs_intent"
                ]) or ("purchase intent" in active_q.lower() and "bookmark" in active_q.lower())
                
                bookmark_intent_cards_html = ""
                if is_bookmark_vs_intent_query:
                    bookmark_intent_cards_html = """
                    <div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08);">
                        <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #94A3B8; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #38BDF8;"></span>
                            KEY BEHAVIORAL DISTINCTION
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #38BDF8; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 12.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #38BDF8; margin-bottom: 6px;">GENUINE PURCHASE INTENT</div>
                                    <div style="font-size: 14px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5; margin-top: 4px;">
                                        &ldquo;I want this, but I'm not ready to buy yet.&rdquo;
                                    </div>
                                </div>
                                <div style="font-size: 12px; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; margin-top: 12px;">
                                    <strong style="color: #CBD5E1;">Signal:</strong> Specific future need / intention to purchase later
                                </div>
                            </div>
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #FF2A85; border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 12.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #FF2A85; margin-bottom: 6px;">BOOKMARKING</div>
                                    <div style="font-size: 14px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5; margin-top: 4px;">
                                        &ldquo;I like this and don't want to lose it.&rdquo;
                                    </div>
                                </div>
                                <div style="font-size: 12px; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; margin-top: 12px;">
                                    <strong style="color: #CBD5E1;">Signal:</strong> Browsing interest / no clear purchase timeline
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 14px; font-size: 12.5px; color: #94A3B8; line-height: 1.45; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px;">
                            <span style="color: #CBD5E1; font-weight: 600;">These behaviours exist on a spectrum &mdash; a wishlisted item can reflect genuine purchase intent even when the purchase is postponed.</span>
                        </div>
                    </div>
                    """

                is_external_info_query = any(k in active_q.lower() for k in [
                    "information do users seek outside",
                    "seek outside nykaa",
                    "seek outside",
                    "external information",
                    "external research"
                ])
                external_info_cards_html = ""
                if is_external_info_query:
                    external_info_cards_html = """
                    <div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.08);">
                        <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid #38BDF8; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;">
                            <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #38BDF8; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #38BDF8;"></span>
                                KEY RESEARCH INSIGHT: EXTERNAL RESEARCH = CONFIDENCE VALIDATION
                            </div>
                            <div style="font-size: 14px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5;">
                                &ldquo;Users look outside the platform mainly to answer questions they cannot confidently resolve from the product page.&rdquo;
                            </div>
                        </div>

                        <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #94A3B8; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #FF2A85;"></span>
                            RECURRING EXTERNAL INFORMATION NEEDS
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #38BDF8; border-radius: 10px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #38BDF8; margin-bottom: 6px;">Fit & Sizing</div>
                                <div style="font-size: 12.5px; color: #CBD5E1; line-height: 1.45;">
                                    Need confidence that the product will fit their body and measurements.
                                </div>
                            </div>
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #FF2A85; border-radius: 10px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #FF2A85; margin-bottom: 6px;">Real-world Appearance</div>
                                <div style="font-size: 12.5px; color: #CBD5E1; line-height: 1.45;">
                                    Need to understand how the product looks outside studio/product photography.
                                </div>
                            </div>
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #F59E0B; border-radius: 10px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #F59E0B; margin-bottom: 6px;">Quality & Material</div>
                                <div style="font-size: 12.5px; color: #CBD5E1; line-height: 1.45;">
                                    Need more confidence about fabric, construction, and how the product may feel or perform in real life.
                                </div>
                            </div>
                            <div style="background: #090D14; border: 1px solid rgba(255,255,255,0.08); border-top: 3px solid #10B981; border-radius: 10px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #10B981; margin-bottom: 6px;">Social Proof</div>
                                <div style="font-size: 12.5px; color: #CBD5E1; line-height: 1.45;">
                                    Look for experiences, reviews, or photos from other shoppers to validate the decision.
                                </div>
                            </div>
                        </div>
                    </div>
                    """

                # Grounded Synthesized Answer Display Card
                formatted_answer = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #FFFFFF; font-weight: 700;">\1</strong>', sec['grounded_answer'])
                paragraphs = formatted_answer.split("\n\n")
                paragraphs_html = "".join([f'<p style="margin-top: 0; margin-bottom: 14px; font-size: 15px !important; font-weight: 400; color: #F8FAFC !important; line-height: 1.75;">{p.strip()}</p>' for p in paragraphs if p.strip()])
                
                answer_card_html = f"""
                <div class="saas-answer-container">
                    <div>
                        {paragraphs_html}
                    </div>{bookmark_intent_cards_html}{external_info_cards_html}
                </div>
                """
                st.html(answer_card_html)
