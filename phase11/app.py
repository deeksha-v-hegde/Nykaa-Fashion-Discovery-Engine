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

# Modern Dark AI / Product Analytics Dashboard CSS
st.markdown("""
<style>
    /* Full-Width Controlled Layout */
    .block-container {
        max-width: 100% !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Main Dark Theme & Clean Proportional Typography */
    .main, .stApp {
        background-color: #0B0F17 !important;
        color: #E6EDF3 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif !important;
    }
    
    /* Controlled Typography Hierarchy */
    h1, h1 *, div[data-testid="stMarkdownContainer"] h1 {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.4px !important;
        margin-bottom: 0.25rem !important;
    }
    h2, h2 *, div[data-testid="stMarkdownContainer"] h2 {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    h3, div[data-testid="stMarkdownContainer"] h3, [data-testid="stHeadingWithActionElements"] h3 {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.2rem !important;
        line-height: 1.3 !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    /* Modern Narrow Dashboard Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #121720 !important;
        border-right: 1px solid #21262D !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        width: 260px !important;
        padding: 1.2rem 0.9rem !important;
    }
    
    /* Sidebar Radio Navigation Panel */
    div[data-testid="stRadio"] {
        width: 100% !important;
    }
    div[data-testid="stRadio"] label {
        display: flex !important;
        align-items: center !important;
        background-color: #161B22 !important;
        border: 1px solid #21262D !important;
        border-radius: 6px !important;
        margin-bottom: 6px !important;
        padding: 8px 10px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #E80071 !important;
        background-color: #1F242C !important;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #E6EDF3 !important;
        white-space: normal !important;
        line-height: 1.3 !important;
        margin: 0 !important;
    }
    
    /* Modern Analytics KPI Cards */
    .analytics-kpi-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 14px 18px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 80px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .analytics-kpi-val {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #58A6FF !important;
        line-height: 1.1 !important;
        letter-spacing: -0.5px;
    }
    .analytics-kpi-lbl {
        font-size: 11.5px !important;
        font-weight: 700 !important;
        color: #8B949E !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* KPI Card with Tooltip Popover */
    div[data-testid="stColumn"], div[data-testid="stMarkdownContainer"] {
        overflow: visible !important;
    }
    .kpi-interactive-card {
        position: relative;
        cursor: default;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-interactive-card:hover {
        border-color: #58A6FF;
        box-shadow: 0 4px 14px rgba(88, 166, 255, 0.15);
    }
    .kpi-hover-popover {
        display: none;
        position: absolute;
        top: calc(100% + 8px);
        right: 0;
        width: 250px;
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.75);
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
        color: #8B949E;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 9px;
        padding-bottom: 5px;
        border-bottom: 1px solid #21262D;
    }
    .popover-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        font-size: 12px;
    }
    .popover-name {
        color: #C9D1D9;
        font-weight: 500;
    }
    .popover-val {
        color: #58A6FF;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }
    .popover-unit {
        color: #8B949E;
        font-weight: 400;
        font-size: 10.5px;
        margin-left: 2px;
    }
    .popover-divider {
        height: 1px;
        background: #30363D;
        margin: 8px 0 7px 0;
    }
    .popover-total-row {
        margin-bottom: 0;
    }
    .popover-total-name {
        color: #FFFFFF;
        font-weight: 700;
    }
    .popover-total-val {
        color: #3FB950;
        font-weight: 800;
        font-variant-numeric: tabular-nums;
    }
    
    /* Compact Analytics Friction Cards */
    .analytics-friction-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-top: 3px solid #E80071;
        border-radius: 8px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 220px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .analytics-friction-card:hover {
        border-color: #58A6FF;
        transform: translateY(-2px);
    }
    .friction-card-top {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .badge-rank {
        font-size: 10.5px;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 4px;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-pill-stage {
        font-size: 9.5px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        background: #21262D;
        color: #7EE787;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .friction-title {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        line-height: 1.35 !important;
        margin-bottom: 10px !important;
        min-height: 38px;
    }
    .friction-meta-row {
        font-size: 12px;
        color: #8B949E;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .friction-meta-orange {
        color: #F0883E;
        font-weight: 700;
    }
    .friction-score-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #21262D;
    }
    .friction-score-lbl {
        font-size: 11px;
        color: #8B949E;
        font-weight: 700;
        text-transform: uppercase;
    }
    .friction-score-num {
        font-size: 15px;
        font-weight: 800;
        color: #3FB950;
    }

    /* Modern Experiment Hypothesis Cards */
    .analytics-hypo-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-top: 3px solid #58A6FF;
        border-radius: 8px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 340px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .analytics-hypo-card:hover {
        border-color: #58A6FF;
        transform: translateY(-2px);
    }
    .hypo-card-top {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
    }
    .hypo-rank-badge {
        font-size: 10px;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 4px;
        color: #FFFFFF;
        text-transform: uppercase;
    }
    .hypo-status-badge {
        font-size: 9.5px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        background: #21262D;
        color: #58A6FF;
        text-transform: uppercase;
    }
    .hypo-theme-title {
        font-size: 10.5px;
        font-weight: 700;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .hypo-intervention-name {
        font-size: 13.5px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        line-height: 1.35 !important;
        margin-bottom: 8px !important;
        min-height: 36px;
    }
    .hypo-statement-box {
        background: #0D1117;
        border: 1px solid #21262D;
        border-radius: 6px;
        padding: 8px 10px;
        margin-bottom: 8px;
    }
    .hypo-statement-if {
        font-size: 12px;
        color: #C9D1D9;
        line-height: 1.4;
        margin-bottom: 5px;
    }
    .hypo-statement-then {
        font-size: 12px;
        color: #7EE787;
        line-height: 1.4;
    }
    .hypo-chips-box {
        display: flex;
        flex-direction: column;
        gap: 3px;
        margin-bottom: 8px;
    }
    .hypo-chip-row {
        font-size: 11px;
        color: #8B949E;
        background: #0D1117;
        border: 1px solid #21262D;
        border-radius: 4px;
        padding: 3px 6px;
        display: flex;
        justify-content: space-between;
    }
    .hypo-chip-row strong {
        color: #E6EDF3;
        font-weight: 600;
    }
    .hypo-footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px solid #21262D;
        font-size: 11px;
        color: #8B949E;
    }
    .hypo-score-green {
        color: #3FB950;
        font-weight: 800;
        font-size: 13px;
    }
    
    /* Detailed Opportunity Cards (View 2) */
    .opportunity-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-left: 5px solid #E80071;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .nykaa-badge {
        background: #E80071;
        color: #FFFFFF !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px !important;
        font-weight: 800 !important;
        display: inline-block;
    }
    code {
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: #79C0FF !important;
        background-color: #21262D !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    .citation-box {
        background-color: #0D1117;
        border: 1px dashed #30363D;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 13px !important;
        line-height: 1.5 !important;
        color: #E6EDF3 !important;
    }
    .grounded-answer-box {
        background: #161B22;
        border: 1px solid #E80071;
        border-radius: 8px;
        padding: 18px 20px;
        margin-top: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(232, 0, 113, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Instantiate services dynamically
dash_service = DashboardService()
ask_service = AskSessionService()

# 1. Main Header Section (Clean, Prominent but Not Oversized)
st.markdown("""
<div style="margin-bottom: 18px;">
    <h1 style="font-size: 22px !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0 0 3px 0 !important; letter-spacing: -0.3px;">
        🛍️ Nykaa Fashion AI Discovery Engine
    </h1>
    <p style="font-size: 13.5px !important; color: #8B949E !important; margin: 0 !important; font-weight: 400;">
        Evidence-Grounded Research Intelligence for Wishlist Reconsideration & Conversion
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Data Update Status (Above Navigation)
update_meta = dash_service.get_data_update_monday()
st.sidebar.markdown(f"""
<div style="background: #161B22; border: 1px solid #30363D; border-left: 3px solid #E80071; border-radius: 6px; padding: 10px 12px; margin-bottom: 16px;">
    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.8px; color: #8B949E; font-weight: 700; margin-bottom: 2px; display: flex; align-items: center; gap: 5px;">
        <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #3FB950;"></span>
        Data Updated
    </div>
    <div style="font-size: 13.5px; font-weight: 700; color: #FFFFFF;">
        {update_meta['display_text']}
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation with State Key
if "nav_choice" not in st.session_state:
    st.session_state["nav_choice"] = "📊 Overview & Executive Summary"

st.sidebar.markdown("<div style='font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #8B949E; margin-bottom: 8px;'>Navigation</div>", unsafe_allow_html=True)
nav_selection = st.sidebar.radio(
    "Select Interface View",
    [
        "📊 Overview & Executive Summary",
        "🎯 Prioritised Opportunity Board",
        "💬 Ask Discovery Engine"
    ],
    key="nav_choice",
    label_visibility="collapsed"
)


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
    <div class="opportunity-card" style="border-left-color: {badge_color};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <span class="nykaa-badge" style="background: {badge_color};">{tag_label}</span>
                <span style="background-color: #21262D; color: #7EE787; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 10px; margin-left: 6px;">
                    📌 {stage_pill_text.upper()}
                </span>
            </div>
            <span style="font-size: 16px !important; font-weight: 800; color: #3FB950;">Prioritisation Score: {score_text} / 5.0</span>
        </div>
        <h3 style="margin-top: 4px; margin-bottom: 10px; font-size: 16px !important; color: #FFFFFF !important;">{title}</h3>
        <p style="font-size: 13.5px !important; margin-bottom: 8px;"><strong>{field1_label}:</strong> {field1_text}</p>
        <p style="font-size: 13.5px !important; margin-bottom: 8px;"><strong>{field2_label}:</strong> {field2_text}</p>
        <div style="background-color: #0D1117; border: 1px solid #30363D; border-radius: 6px; padding: 10px 14px; margin-top: 8px; margin-bottom: 10px;">
            <p style="font-size: 12.5px !important; margin-bottom: 0; color: #8B949E !important;">📊 <strong>{box_label}:</strong> {box_text}</p>
        </div>
        <p style="font-size: 13px !important; margin-bottom: 8px;"><strong>{scale_label}:</strong> {scale_text}</p>
        <p style="font-size: 12px !important; color: #8B949E !important; margin-top: 6px;">{components_text}</p>
    </div>
    """, unsafe_allow_html=True)

    if citations:
        with st.expander(expander_label):
            for cite in citations:
                st.markdown(f"""
                <div class="citation-box">
                    <strong>Source:</strong> {cite.get('source_name', 'Nykaa')} ({cite.get('source_scope', 'Direct Scope')})<br/>
                    <strong>Snippet:</strong> "{cite.get('snippet', '')}"
                </div>
                """, unsafe_allow_html=True)


# VIEW 1: Overview & Executive Summary (Modern Dark AI / Product Analytics Dashboard)
if nav_selection == "📊 Overview & Executive Summary":
    overview = dash_service.get_overview()
    stats = overview["overview_stats"]
    board = dash_service.get_opportunity_board()
    cards = board["opportunities"]

    # Dynamic platform aggregation from existing service layer (excluding inactive Phase 10 registry entries)
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

    # 1. KPI ROW (EXACTLY 3 CARDS — REMOVED UNKNOWN METRIC ENTIRELY)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="analytics-kpi-card">
            <div class="analytics-kpi-val">{stats['total_ingested_documents']:,}</div>
            <div class="analytics-kpi-lbl">TOTAL REVIEWS SCRAPED</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="analytics-kpi-card">
            <div class="analytics-kpi-val">{stats['sample_size_n']:,}</div>
            <div class="analytics-kpi-lbl">RELEVANT EVIDENCE</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="analytics-kpi-card kpi-interactive-card">
            <div class="analytics-kpi-val">{distinct_platforms_count}</div>
            <div class="analytics-kpi-lbl">SOURCES</div>
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
                    <span class="popover-total-name">Total</span>
                    <span class="popover-total-val">{total_platform_reviews:,} <span class="popover-unit">reviews</span></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2. WISHLIST PURCHASE FRICTION (WITH DIRECT WISHLIST EVIDENCE 14 BADGE)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 24px; margin-bottom: 12px; border-bottom: 1px solid #21262D; padding-bottom: 8px;">
        <div>
            <h2 style="font-size: 15px !important; font-weight: 700 !important; color: #FFFFFF !important; margin: 0 0 2px 0 !important; letter-spacing: -0.2px;">
                🎯 WISHLIST PURCHASE FRICTION
            </h2>
            <p style="font-size: 12.5px !important; color: #8B949E !important; margin: 0 !important;">
                Evidence most closely connected to why saved fashion items remain unpurchased.
            </p>
        </div>
        <div style="background: rgba(232, 0, 113, 0.12); border: 1px solid rgba(232, 0, 113, 0.35); border-radius: 6px; padding: 4px 10px; display: flex; align-items: center; gap: 6px;">
            <span style="font-size: 12px; font-weight: 800; color: #FF527B;">14 DIRECT WISHLIST DOCUMENTS</span>
            <span style="font-size: 11px; color: #8B949E;">(subset of 1,025 relevant)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TOP 3 SIGNALS ARRANGED IN 3 COMPACT HORIZONTAL CARDS
    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        st.markdown("""
        <div class="analytics-friction-card" style="border-top-color: #E80071;">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank" style="background: #E80071;">#01</span>
                    <span class="badge-rank" style="background: #21262D; color: #FF527B; font-size: 9.5px;">RECOMMENDED TO VALIDATE</span>
                    <span class="badge-pill-stage">PRE-PURCHASE / RECONSIDERATION</span>
                </div>
                <div class="friction-title">
                    Ethnic Wear Fit Uncertainty & Inconsistent Brand Size Charts
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-orange">5 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>95 docs · 9.3% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Score</span>
                <span class="friction-score-num">4.73 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fc2:
        st.markdown("""
        <div class="analytics-friction-card" style="border-top-color: #388BFD;">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank" style="background: #388BFD;">#02</span>
                    <span class="badge-rank" style="background: #21262D; color: #58A6FF; font-size: 9.5px;">LEADING RESEARCH SIGNAL #2</span>
                    <span class="badge-pill-stage">PRE-PURCHASE / RECONSIDERATION</span>
                </div>
                <div class="friction-title">
                    Fabric Material Discrepancies & Material Transparency Concerns
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-orange">4 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>101 docs · 9.9% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Score</span>
                <span class="friction-score-num">4.62 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with fc3:
        st.markdown("""
        <div class="analytics-friction-card" style="border-top-color: #388BFD;">
            <div>
                <div class="friction-card-top">
                    <span class="badge-rank" style="background: #388BFD;">#03</span>
                    <span class="badge-rank" style="background: #21262D; color: #58A6FF; font-size: 9.5px;">LEADING RESEARCH SIGNAL #3</span>
                    <span class="badge-pill-stage">PRE-PURCHASE / RECONSIDERATION</span>
                </div>
                <div class="friction-title">
                    Product Appearance vs Listing Studio Lighting Discrepancies
                </div>
                <div class="friction-meta-row">
                    <span>📌</span>
                    <span class="friction-meta-orange">2 direct wishlist documents</span>
                </div>
                <div class="friction-meta-row">
                    <span>📊</span>
                    <span>43 docs · 4.2% of N=1,025</span>
                </div>
            </div>
            <div class="friction-score-row">
                <span class="friction-score-lbl">Score</span>
                <span class="friction-score-num">4.25 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def nav_to_board():
        st.session_state["nav_choice"] = "🎯 Prioritised Opportunity Board"

    st.markdown("<div style='margin-top: 10px; margin-bottom: 18px;'>", unsafe_allow_html=True)
    st.button("VIEW ALL SIGNALS →", key="btn_view_all_signals", on_click=nav_to_board)
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. INDIRECT / COMPOUNDING SIGNAL (COMPACT HORIZONTAL CALLOUT)
    st.markdown("""
    <div style="background: #161B22; border: 1px solid #30363D; border-left: 4px solid #D29922; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="background: #D29922; color: #0D1117; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 4px; text-transform: uppercase;">
                    INDIRECT / COMPOUNDING SIGNAL
                </span>
                <span style="font-size: 14.5px; font-weight: 700; color: #FFFFFF;">
                    Delivery & Return Friction
                </span>
            </div>
            <div style="font-size: 12px; color: #D29922; font-weight: 700; display: flex; gap: 10px; flex-wrap: wrap;">
                <span>397 docs · 38.7% of N=1,025</span>
                <span>·</span>
                <span>99.75% post-purchase evidence</span>
                <span>·</span>
                <span>1 documented case compounds wishlist-stage fit uncertainty</span>
            </div>
        </div>
        <p style="font-size: 12.5px !important; color: #8B949E !important; margin: 0 !important; line-height: 1.4 !important;">
            "The available evidence does not establish Delivery/Returns as a primary cause of wishlist non-purchase. It appears primarily as post-purchase evidence, with one documented case where return friction compounds fit uncertainty."
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("VIEW FULFILLMENT EVIDENCE → (4 Cited Logistics Reviews)"):
        for cite in cards[4]['citations']:
            st.markdown(f"""
            <div class="citation-box">
                <strong>Source:</strong> {cite['source_name']} ({cite['source_scope']})<br/>
                <strong>Snippet:</strong> "{cite['snippet']}"
            </div>
            """, unsafe_allow_html=True)

    # 4. RESEARCH HYPOTHESES (3 COMPACT EXPERIMENT CARDS)
    st.markdown("""
    <div style="margin-top: 24px; margin-bottom: 12px; border-bottom: 1px solid #21262D; padding-bottom: 8px;">
        <h2 style="font-size: 15px !important; font-weight: 700 !important; color: #FFFFFF !important; margin: 0 0 2px 0 !important; letter-spacing: -0.2px;">
            🔬 RESEARCH HYPOTHESES
        </h2>
        <p style="font-size: 12.5px !important; color: #8B949E !important; margin: 0 !important;">
            Actionable product experiment specifications grounded directly in purchase friction signals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hc1, hc2, hc3 = st.columns(3)

    # HYPOTHESIS #01
    with hc1:
        st.markdown("""
        <div class="analytics-hypo-card" style="border-top-color: #E80071;">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #E80071;">HYPOTHESIS #01 — FIT & SIZING CONFIDENCE</span>
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
                <span>Evidence: <strong>5 direct wishlist documents</strong></span>
                <span class="hypo-score-green">Score: 4.73 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # HYPOTHESIS #02
    with hc2:
        st.markdown("""
        <div class="analytics-hypo-card" style="border-top-color: #388BFD;">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #388BFD;">HYPOTHESIS #02 — WISHLIST ORGANIZATION</span>
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
                <span>Evidence: <strong>1 direct wishlist document</strong></span>
                <span class="hypo-score-green">Score: 3.85 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # HYPOTHESIS #03
    with hc3:
        st.markdown("""
        <div class="analytics-hypo-card" style="border-top-color: #D29922;">
            <div>
                <div class="hypo-card-top">
                    <span class="hypo-rank-badge" style="background: #D29922; color: #0D1117;">HYPOTHESIS #03 — FULFILLMENT REASSURANCE</span>
                    <span class="hypo-status-badge">TEST FOR COMPOUNDING EFFECT</span>
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
                    <div class="hypo-chip-row"><span>Target:</span> <strong>Wishlist users exposed to fulfillment/return uncertainty</strong></div>
                    <div class="hypo-chip-row"><span>Primary Metric:</span> <strong>Wishlist → Cart progression</strong></div>
                    <div class="hypo-chip-row"><span>Guardrail:</span> <strong>Return-related escalations</strong></div>
                </div>
            </div>
            <div class="hypo-footer-row">
                <span>Evidence: <strong>Indirect / compounding signal</strong></span>
                <span class="hypo-score-green">Score: 3.52 / 5.0</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# VIEW 2: Prioritised Opportunity Board (Pure Problem Discovery)
elif nav_selection == "🎯 Prioritised Opportunity Board":
    st.markdown("<h2 style='color: #FFFFFF !important;'>🎯 Prioritised Research Shortlist (Phase 7 Opportunity Board)</h2>", unsafe_allow_html=True)
    st.info("Opportunities are ranked descending by 6-Factor Prioritisation Score (1.0–5.0). Rank 1 is strictly labeled 'Recommended opportunity to validate'. Focus is strictly on User Problem Discovery & Friction Signals.")

    board = dash_service.get_opportunity_board()
    cards = board["opportunities"]

    for c in cards:
        r_num = c['rank']
        opp_id = c.get('opportunity_id', '')
        d_text = density_info.get(opp_id, c.get('scale_formatted', 'Grounded across canonical relevant user reviews.'))
        is_compounding = c.get('signal_type') == 'indirect_compounding'
        badge_color = "#D29922" if is_compounding else ("#E80071" if r_num == 1 else "#388BFD")
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


# VIEW 3: Ask Discovery Engine (Grounded Answer Display)
elif nav_selection == "💬 Ask Discovery Engine":
    st.cache_data.clear()
    st.cache_resource.clear()
    st.markdown("<h2 style='color: #FFFFFF !important;'>💬 Ask the Discovery Engine (Conversational Grounded RAG)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 16px !important; color: #8B949E !important;'>Ask PM discovery questions or click one of the 10 official research presets below.</p>", unsafe_allow_html=True)

    presets = PresetsCatalogue.get_presets()

    def set_ask_query(query_text):
        st.session_state["active_discovery_query"] = query_text

    if "active_discovery_query" not in st.session_state:
        st.session_state["active_discovery_query"] = "Why do shoppers hesitate to buy items saved in their wishlist?"

    st.markdown("<h3 style='color: #FFFFFF !important;'>💡 Official Research Presets</h3>", unsafe_allow_html=True)
    p_cols = st.columns(2)

    for idx, p in enumerate(presets):
        col = p_cols[idx % 2]
        col.button(
            f"📌 {p.prompt}",
            key=f"btn_preset_{p.preset_id}",
            on_click=set_ask_query,
            args=(p.prompt,)
        )

    st.text_input(
        "Or enter a custom discovery question:",
        key="active_discovery_query"
    )

    st.button("🚀 Execute Grounded RAG Query", type="primary")

    active_q = st.session_state.get("active_discovery_query")

    if active_q:
        st.html(f"""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px 18px; margin-top: 14px; margin-bottom: 14px;">
            <span style="font-size: 15px; color: #8B949E;">Active Research Question:</span><br/>
            <strong style="font-size: 18px; color: #58A6FF;">"{active_q}"</strong>
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
                    <div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid #21262D;">
                        <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #8B949E; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #58A6FF;"></span>
                            KEY BEHAVIORAL DISTINCTION
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #58A6FF; border-radius: 8px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #58A6FF; margin-bottom: 6px;">GENUINE PURCHASE INTENT</div>
                                    <div style="font-size: 14.5px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5; margin-top: 4px;">
                                        &ldquo;I want this, but I'm not ready to buy yet.&rdquo;
                                    </div>
                                </div>
                                <div style="font-size: 12px; color: #8B949E; border-top: 1px solid #21262D; padding-top: 8px; margin-top: 12px;">
                                    <strong style="color: #C9D1D9;">Signal:</strong> Specific future need / intention to purchase later
                                </div>
                            </div>
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #FF527B; border-radius: 8px; padding: 14px 16px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <div style="font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #FF527B; margin-bottom: 6px;">BOOKMARKING</div>
                                    <div style="font-size: 14.5px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5; margin-top: 4px;">
                                        &ldquo;I like this and don't want to lose it.&rdquo;
                                    </div>
                                </div>
                                <div style="font-size: 12px; color: #8B949E; border-top: 1px solid #21262D; padding-top: 8px; margin-top: 12px;">
                                    <strong style="color: #C9D1D9;">Signal:</strong> Browsing interest / no clear purchase timeline
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 14px; font-size: 12.5px; color: #8B949E; line-height: 1.45; border-top: 1px solid #21262D; padding-top: 10px;">
                            <span style="color: #C9D1D9; font-weight: 600;">These behaviours exist on a spectrum &mdash; a wishlisted item can reflect genuine purchase intent even when the purchase is postponed.</span>
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
                    <div style="margin-top: 22px; padding-top: 16px; border-top: 1px solid #21262D;">
                        <div style="background: #0D1117; border: 1px solid #30363D; border-left: 4px solid #58A6FF; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;">
                            <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #58A6FF; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #58A6FF;"></span>
                                KEY RESEARCH INSIGHT: EXTERNAL RESEARCH = CONFIDENCE VALIDATION
                            </div>
                            <div style="font-size: 14.5px; font-weight: 600; color: #FFFFFF; font-style: italic; line-height: 1.5;">
                                &ldquo;Users look outside the platform mainly to answer questions they cannot confidently resolve from the product page.&rdquo;
                            </div>
                        </div>

                        <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #8B949E; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                            <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #E80071;"></span>
                            RECURRING EXTERNAL INFORMATION NEEDS
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #58A6FF; border-radius: 8px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #58A6FF; margin-bottom: 6px;">Fit & Sizing</div>
                                <div style="font-size: 12.5px; color: #E6EDF3; line-height: 1.45;">
                                    Need confidence that the product will fit their body and measurements.
                                </div>
                            </div>
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #FF527B; border-radius: 8px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #FF527B; margin-bottom: 6px;">Real-world Appearance</div>
                                <div style="font-size: 12.5px; color: #E6EDF3; line-height: 1.45;">
                                    Need to understand how the product looks outside studio/product photography.
                                </div>
                            </div>
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #E5A83B; border-radius: 8px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #E5A83B; margin-bottom: 6px;">Quality & Material</div>
                                <div style="font-size: 12.5px; color: #E6EDF3; line-height: 1.45;">
                                    Need more confidence about fabric, construction, and how the product may feel or perform in real life.
                                </div>
                            </div>
                            <div style="background: #0D1117; border: 1px solid #30363D; border-top: 3px solid #3FB950; border-radius: 8px; padding: 14px 16px;">
                                <div style="font-size: 13.5px; font-weight: 800; color: #3FB950; margin-bottom: 6px;">Social Proof</div>
                                <div style="font-size: 12.5px; color: #E6EDF3; line-height: 1.45;">
                                    Look for experiences, reviews, or photos from other shoppers to validate the decision.
                                </div>
                            </div>
                        </div>
                    </div>
                    """

                # 1. Grounded Synthesized Answer Display Card
                formatted_answer = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #FFFFFF; font-weight: 700;">\1</strong>', sec['grounded_answer'])
                paragraphs = formatted_answer.split("\n\n")
                paragraphs_html = "".join([f'<p style="margin-top: 0; margin-bottom: 14px; font-size: 15.5px !important; font-weight: 400; color: #FFFFFF !important; line-height: 1.75;">{p.strip()}</p>' for p in paragraphs if p.strip()])
                
                answer_card_html = f"""
                <div class="grounded-answer-box">
                    <div>
                        {paragraphs_html}
                    </div>{bookmark_intent_cards_html}{external_info_cards_html}
                </div>
                """
                st.html(answer_card_html)









