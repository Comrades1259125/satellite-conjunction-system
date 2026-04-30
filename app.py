"""
🛰️ Satellite Conjunction Analysis System
Main Streamlit Application

Analyzes trajectories and collision probability between two satellites.
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timezone

from skyfield.api import load

from core.tle_fetcher import (
    get_satellite,
    get_satellite_from_tle,
    get_available_satellites,
    get_tle_age,
)
from core.orbit_calculator import (
    compute_positions,
    compute_velocities,
    generate_time_array,
    compute_orbital_elements,
    compute_itrf_positions,
)
from core.proximity_analysis import (
    compute_distances,
    find_closest_approach,
    compute_relative_velocity,
    compute_relative_positions,
    compute_collision_probability,
    compute_collision_probability_over_time,
    get_risk_level,
    generate_covariance_heatmap_data,
    apply_cw_maneuver,
)
from ui.charts import (
    create_distance_chart,
    create_collision_heatmap,
    create_3d_relative_orbit,
    create_3d_earth_view,
)
from ui.alerts import (
    render_risk_banner,
    render_telemetry_table,
    render_metric_cards,
)
from core.translations import t
from core.report_generator import generate_pdf_report


# ─── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="Satellite Conjunction Analysis",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(180deg, #0D1117 0%, #0A0E14 50%, #0D1117 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: clamp(16px, 4vw, 32px) 0 clamp(12px, 3vw, 24px);
        margin-bottom: 16px;
    }
    .main-header h1 {
        font-size: clamp(24px, 5vw, 36px);
        font-weight: 900;
        background: linear-gradient(135deg, #00E5FF, #7C4DFF, #FF1744);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
    }
    .main-header p {
        color: #546E7A;
        font-size: clamp(11px, 2vw, 14px);
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0E14, #0D1117) !important;
        border-right: 1px solid rgba(0,229,255,0.08);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #00E5FF !important;
    }

    /* Cards */
    .analysis-section {
        background: rgba(13, 17, 23, 0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(12px, 2vw, 14px);
        color: #00E5FF;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(0,229,255,0.15);
    }

    /* Streamlit overrides */
    .stSelectbox label, .stSlider label, .stNumberInput label, .stTextArea label {
        color: #B0BEC5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(0,229,255,0.04);
        border: 1px solid rgba(0,229,255,0.1);
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #546E7A !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00E5FF !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Welcome Grid */
    .welcome-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        text-align: left;
        max-width: 500px;
        margin: 0 auto;
    }
    @media (max-width: 600px) {
        .welcome-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00B8D4, #0091EA) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        padding: clamp(10px, 2vw, 12px) clamp(16px, 4vw, 32px) !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        font-size: clamp(13px, 2vw, 16px) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,184,212,0.3) !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    .glow-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00E5FF40, transparent);
        margin: 24px 0;
        border: none;
    }

    /* Status animation */
    @keyframes pulse-glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .status-live {
        animation: pulse-glow 2s ease-in-out infinite;
    }

    /* ── Force ALL text to light colors on dark background ── */
    /* General text elements */
    .stApp, .stApp * {
        color-scheme: dark !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown span,
    .stMarkdown li, .stMarkdown ol, .stMarkdown ul,
    .stText, .stApp p, .stApp span {
        color: #E0E0E0 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #FFFFFF !important;
    }
    .stMarkdown strong, .stMarkdown b {
        color: #FFFFFF !important;
    }
    .stMarkdown a {
        color: #00E5FF !important;
    }

    /* Input labels and helper text */
    .stSelectbox label, .stSlider label, .stNumberInput label,
    .stTextArea label, .stTextInput label, .stDateInput label,
    .stTimeInput label, .stCheckbox label, .stRadio label,
    .stMultiSelect label, .stFileUploader label,
    .stColorPicker label {
        color: #B0BEC5 !important;
    }
    .stSelectbox [data-baseweb="select"] span,
    .stMultiSelect [data-baseweb="select"] span {
        color: #000000 !important;
    }
    input, textarea, select {
        color: #000000 !important;
    }
    .stTextInput input, .stNumberInput input,
    .stTextArea textarea, .stDateInput input,
    .stTimeInput input {
        color: #000000 !important;
    }

    /* Radio buttons & checkboxes */
    .stRadio > div > label > div:last-child,
    .stCheckbox > label > div:last-child {
        color: #000000 !important;
    }
    .stRadio > div[role="radiogroup"] label p,
    .stRadio > div[role="radiogroup"] label span,
    .stRadio > div[role="radiogroup"] label div {
        color: #000000 !important;
    }

    /* Expanders */
    .streamlit-expanderHeader, .streamlit-expanderHeader p,
    details summary span, details summary p {
        color: #E0E0E0 !important;
    }
    [data-testid="stExpander"] summary span {
        color: #E0E0E0 !important;
    }
    [data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
        color: #E0E0E0 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button,
    .stTabs [data-baseweb="tab"] {
        color: #B0BEC5 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00E5FF !important;
    }

    /* Toast / Alert messages */
    .stAlert p, .stAlert span,
    div[data-testid="stNotification"] p,
    div[data-testid="stNotification"] span,
    .stSuccess p, .stInfo p, .stWarning p, .stError p,
    .stException p {
        color: #E0E0E0 !important;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div {
        color: #B0BEC5 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #00E5FF !important;
    }

    /* Sidebar selectbox / input text — force black on light widget backgrounds */
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] span,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] div,
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stTextArea textarea,
    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] .stTimeInput input,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {
        color: #000000 !important;
    }
    /* Sidebar slider value text */
    section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMin"],
    section[data-testid="stSidebar"] .stSlider div[data-testid="stTickBarMax"],
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"],
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
        color: #000000 !important;
    }
    /* Sidebar radio button text */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label p,
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] label div {
        color: #000000 !important;
    }

    /* Selectbox / dropdown option text */
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [data-baseweb="popover"] ul li div,
    [data-baseweb="menu"] ul li div {
        color: #000000 !important;
    }

    /* Slider value text */
    .stSlider div[data-testid="stTickBarMin"],
    .stSlider div[data-testid="stTickBarMax"],
    .stSlider [data-baseweb="slider"] div {
        color: #B0BEC5 !important;
    }

    /* DataFrame / table text */
    .stDataFrame td, .stDataFrame th,
    .stTable td, .stTable th {
        color: #E0E0E0 !important;
    }

    /* Download button text */
    .stDownloadButton button span {
        color: #FFFFFF !important;
    }

    /* Spinner text */
    .stSpinner > div > span {
        color: #E0E0E0 !important;
    }

    /* Progress bar text */
    .stProgress > div > div > div > div {
        color: #E0E0E0 !important;
    }

    /* Caption and small text */
    .stCaption, small, .stApp small {
        color: #90A4AE !important;
    }

    /* Hide Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: visible !important;
        border: none !important;
        box-shadow: none !important;
    }
    header[data-testid="stHeader"] > div:first-child {
        background: transparent !important;
    }

    /* Sidebar toggle button always visible and clickable */
    button[data-testid="collapsedControl"] {
        visibility: visible !important;
        z-index: 9999 !important;
        position: fixed !important;
        top: 160px !important;
        left: 8px !important;
    }
    div[data-testid="collapsedControl"] {
        visibility: visible !important;
        z-index: 9999 !important;
        overflow: visible !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Language State ─────────────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state.lang = "en"

L = st.session_state.lang  # shortcut

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="main-header">
    <h1>{t("app_title", L)}</h1>
    <p>{t("app_subtitle", L)}</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar Configuration ────────────────────────────────────────────────────

with st.sidebar:
    # Language toggle at the very top
    lang_choice = st.selectbox(
        t("language_label", L),
        ["English", "ภาษาไทย"],
        index=0 if st.session_state.lang == "en" else 1,
        key="lang_select",
    )
    new_lang = "en" if lang_choice == "English" else "th"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    L = st.session_state.lang  # refresh after potential rerun

    app_mode = st.radio(
        t("app_mode", L),
        [t("mode_1on1", L), t("mode_scanner", L)],
        index=0,
    )



    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("config_title", L))
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # Input mode
    catalog_label = t("catalog_selection", L)
    manual_label = t("manual_tle", L)
    input_mode = st.radio(
        t("input_mode", L),
        [catalog_label, manual_label],
        index=0,
        help=t("input_mode_help", L),
    )

    if input_mode == catalog_label:
        satellites = get_available_satellites()
        sat1_name = st.selectbox(
            t("primary_satellite", L),
            satellites,
            index=satellites.index("ISS (ZARYA)") if "ISS (ZARYA)" in satellites else 0,
        )
        sat2_name = st.selectbox(
            t("secondary_satellite", L),
            satellites,
            index=satellites.index("COSMOS 2251 DEB") if "COSMOS 2251 DEB" in satellites else 1,
        )
        custom_tle = False
    else:
        st.markdown(t("primary_header", L))
        sat1_name = st.text_input(t("primary_name", L), value="SAT-1")
        sat1_line1 = st.text_area(
            t("tle_line1_primary", L),
            value="1 25544U 98067A   24045.54689014  .00024329  00000+0  42556-3 0  9992",
            height=68,
        )
        sat1_line2 = st.text_area(
            t("tle_line2_primary", L),
            value="2 25544  51.6410 138.2047 0002273 315.2168 162.4950 15.50562470439891",
            height=68,
        )

        st.markdown(t("secondary_header", L))
        sat2_name = st.text_input(t("secondary_name", L), value="SAT-2")
        sat2_line1 = st.text_area(
            t("tle_line1_secondary", L),
            value="1 34427U 93036SX  24041.83168981  .00000516  00000+0  16370-3 0  9994",
            height=68,
        )
        sat2_line2 = st.text_area(
            t("tle_line2_secondary", L),
            value="2 34427  74.0202 280.9182 0039927 149.3476 210.9684 14.35878847607451",
            height=68,
        )
        custom_tle = True

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("analysis_window", L))

    # Historical Mode Date Picker
    start_date = st.date_input(
        t("start_time_label", L),
        value=datetime.now(timezone.utc),
    )
    start_time_str = st.time_input("Time (UTC)", value=datetime.now(timezone.utc).time())
    
    # Combine date and time
    start_datetime = datetime.combine(start_date, start_time_str).replace(tzinfo=timezone.utc)


    duration_hours = st.slider(
        t("duration_label", L),
        min_value=1,
        max_value=72,
        value=24,
        step=1,
        help=t("duration_help", L),
    )

    step_minutes = st.slider(
        t("timestep_label", L),
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help=t("timestep_help", L),
    )

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("covariance_title", L))

    position_uncertainty = st.number_input(
        t("pos_uncertainty_label", L),
        min_value=0.001,
        max_value=10.0,
        value=0.1,
        step=0.01,
        format="%.3f",
        help=t("pos_uncertainty_help", L),
    )

    combined_radius = st.number_input(
        t("combined_radius_label", L),
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
        format="%.3f",
        help=t("combined_radius_help", L),
    )

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown(t("maneuver_title", L))
    
    dv_x = st.slider(t("dv_x", L), -50.0, 50.0, 0.0, step=0.1, format="%.1f")
    dv_y = st.slider(t("dv_y", L), -50.0, 50.0, 0.0, step=0.1, format="%.1f")
    dv_z = st.slider(t("dv_z", L), -50.0, 50.0, 0.0, step=0.1, format="%.1f")

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    run_analysis = st.button(t("run_button", L), use_container_width=True)

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 16px 0;
        color: #37474F;
        font-size: 11px;
        margin-top: 16px;
    ">
        Analysis time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}<br>
        {t("powered_by", L)}
    </div>
    """, unsafe_allow_html=True)


# ─── Main Analysis ────────────────────────────────────────────────────────────

if run_analysis:
    if app_mode == t("mode_scanner", L):
        from core.scanner import run_catalog_scan
        with st.spinner(t("scanning", L, count=len(get_available_satellites()) - 1)):
            try:
                ts = load.timescale()
                if custom_tle:
                    sat1 = get_satellite_from_tle(sat1_name, sat1_line1, sat1_line2, ts)
                else:
                    sat1 = get_satellite(sat1_name, ts)
                
                time_array, datetimes_list = generate_time_array(ts, duration_hours, step_minutes, start_time=start_datetime)
                threats = run_catalog_scan(sat1_name, sat1, ts, time_array)
                
                st.success(f"✅ Scan complete. Found {len(threats)} potential threats.")
                st.markdown(f'<div class="section-title">{t("scan_title", L)}</div>', unsafe_allow_html=True)
                
                if threats:
                    df = pd.DataFrame([
                        {
                            "Threat Satellite": t["name"], 
                            "Min Distance (km)": float(f"{t['min_distance_km']:.2f}"), 
                            "TCA Time": datetimes_list[t["tca_idx"]].strftime("%Y-%m-%d %H:%M UTC")
                        } 
                        for t in threats[:10]
                    ])
                    # Style the dataframe using pandas styling
                    styled_df = df.style.map(lambda v: 'color: #FF1744; font-weight: bold;' if isinstance(v, float) and v < 10.0 else ('color: #FFC107;' if isinstance(v, float) and v < 50.0 else ''))
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.info("No nearby satellites found in the catalog over this window.")
            except Exception as e:
                st.error(t("analysis_error", L, error=str(e)))
        st.stop()
        
    try:
        # ── Load satellites ──
        with st.spinner(t("loading_tle", L)):
            ts = load.timescale()

            if custom_tle:
                sat1 = get_satellite_from_tle(sat1_name, sat1_line1, sat1_line2, ts)
                sat2 = get_satellite_from_tle(sat2_name, sat2_line1, sat2_line2, ts)
            else:
                sat1 = get_satellite(sat1_name, ts)
                sat2 = get_satellite(sat2_name, ts)

        st.success(t("loaded_success", L, sat1=sat1_name, sat2=sat2_name))

        # TLE Freshness
        age1 = get_tle_age(sat1)
        age2 = get_tle_age(sat2)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status1 = t("tle_fresh", L) if age1 < 3 else t("tle_warning", L) if age1 < 7 else t("tle_stale", L)
            st.info(f"**{sat1_name}** {t('tle_freshness', L)}: {age1:.1f} days ({status1})")
        with col_f2:
            status2 = t("tle_fresh", L) if age2 < 3 else t("tle_warning", L) if age2 < 7 else t("tle_stale", L)
            st.info(f"**{sat2_name}** {t('tle_freshness', L)}: {age2:.1f} days ({status2})")

        # ── Generate time array ──
        with st.spinner(t("generating_timeline", L, hours=duration_hours, step=step_minutes)):
            time_array, datetimes_list = generate_time_array(ts, duration_hours, step_minutes, start_time=start_datetime)
            total_steps = len(datetimes_list)

        # ── Compute positions & velocities ──
        with st.spinner(t("computing_positions", L)):
            progress = st.progress(0, text=t("computing_sat_pos", L, name=sat1_name))
            pos1 = compute_positions(sat1, ts, time_array)
            progress.progress(20, text=t("computing_sat_pos", L, name=sat2_name))
            pos2 = compute_positions(sat2, ts, time_array)
            progress.progress(40, text=t("computing_sat_vel", L, name=sat1_name))
            vel1 = compute_velocities(sat1, ts, time_array)
            progress.progress(60, text=t("computing_sat_vel", L, name=sat2_name))
            vel2 = compute_velocities(sat2, ts, time_array)
            progress.progress(80, text="Computing Earth-Fixed (ITRF) coordinates...")
            itrf1 = compute_itrf_positions(sat1, ts, time_array)
            itrf2 = compute_itrf_positions(sat2, ts, time_array)
            progress.progress(100, text=t("positions_done", L))

        # ── Proximity analysis ──
        with st.spinner(t("analyzing_proximity", L)):
            distances = compute_distances(pos1, pos2)
            closest = find_closest_approach(distances, datetimes_list)
            rel_vel = compute_relative_velocity(vel1, vel2, closest["index"])
            risk_name, risk_color, risk_emoji = get_risk_level(closest["distance_km"])

            # Collision probability at TCA
            pc_at_tca = compute_collision_probability(
                closest["distance_km"], position_uncertainty, combined_radius
            )

            # Collision probabilities over time
            pc_over_time = compute_collision_probability_over_time(
                distances, position_uncertainty, combined_radius
            )

            # Relative positions in RIC frame
            relative_ric = compute_relative_positions(pos1, pos2, vel1)
            
            # Apply Maneuver (if any)
            import numpy as np
            dt_seconds = np.array([(dt - datetimes_list[0]).total_seconds() for dt in datetimes_list])
            perturbed_ric = apply_cw_maneuver(
                relative_ric, 
                dt_seconds, 
                pos1, 
                vel1, 
                dv_radial_ms=dv_z,
                dv_intrack_ms=dv_x,
                dv_crosstrack_ms=dv_y,
            )
            
            # If no maneuver was inputted, perturbed_ric is effectively the same, pass None
            if dv_x == 0 and dv_y == 0 and dv_z == 0:
                perturbed_ric = None

            # Heatmap data
            heatmap_data, uncertainty_levels, time_indices = generate_covariance_heatmap_data(
                distances, datetimes_list, position_uncertainty, combined_radius
            )

        # ── Clear progress bar ──
        progress.empty()

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Risk Banner (translated) ──
        risk_display = t(f"risk_{risk_name.lower()}", L)
        render_risk_banner(risk_display, risk_color, risk_emoji, closest["distance_km"], t("min_distance_label", L))

        # ── Metric Cards (translated) ──
        render_metric_cards(closest, rel_vel, (risk_display, risk_color, risk_emoji), L)

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Collision Probability at TCA ──
        col_pc1, col_pc2 = st.columns(2)
        with col_pc1:
            st.markdown(f"""
            <div style="
                background: rgba(124,77,255,0.06);
                border: 1px solid rgba(124,77,255,0.2);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            ">
                <div style="font-size: 12px; color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">
                    {t("pc_at_tca_title", L)}
                </div>
                <div style="
                    font-size: clamp(20px, 4vw, 28px); font-weight: 800;
                    color: {'#FF1744' if pc_at_tca > 1e-4 else '#FFC107' if pc_at_tca > 1e-7 else '#00E676'};
                    font-family: 'JetBrains Mono', monospace;
                    margin-top: 8px;
                ">
                    {pc_at_tca:.4e}
                </div>
                <div style="font-size: 11px; color: #78909C; margin-top: 4px;">
                    σ = {position_uncertainty} km | R = {combined_radius} km
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_pc2:
            max_pc = float(np.max(pc_over_time))
            st.markdown(f"""
            <div style="
                background: rgba(255,145,0,0.06);
                border: 1px solid rgba(255,145,0,0.2);
                border-radius: 12px;
                padding: clamp(12px, 3vw, 20px);
                text-align: center;
            ">
                <div style="font-size: 12px; color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">
                    {t("max_pc_title", L)}
                </div>
                <div style="
                    font-size: clamp(20px, 4vw, 28px); font-weight: 800;
                    color: {'#FF1744' if max_pc > 1e-4 else '#FFC107' if max_pc > 1e-7 else '#00E676'};
                    font-family: 'JetBrains Mono', monospace;
                    margin-top: 8px;
                ">
                    {max_pc:.4e}
                </div>
                <div style="font-size: 11px; color: #78909C; margin-top: 4px;">
                    {t("over_window", L, hours=duration_hours)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Graph 1: Distance Over Time ──
        st.markdown(f'<div class="section-title">{t("distance_section", L)}</div>', unsafe_allow_html=True)
        fig_distance = create_distance_chart(datetimes_list, distances, closest, L)
        st.plotly_chart(fig_distance, use_container_width=True, key="distance_chart")

        # ── Graph 2: Collision Probability Heatmap ──
        st.markdown(f'<div class="section-title">{t("heatmap_section", L)}</div>', unsafe_allow_html=True)
        fig_heatmap = create_collision_heatmap(heatmap_data, uncertainty_levels, time_indices, datetimes_list, L)
        st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_chart")

        # ── Graph 3: 3D Relative Orbit ──
        st.markdown(f'<div class="section-title">{t("ric_section", L)}</div>', unsafe_allow_html=True)
        fig_3d = create_3d_relative_orbit(relative_ric, closest["index"], L, perturbed_ric=perturbed_ric)
        st.plotly_chart(fig_3d, use_container_width=True, key="3d_orbit_chart")

        # ── Graph 4: 3D Earth Orbit View ──
        st.markdown(f'<div class="section-title">{t("earth_3d_title", L)}</div>', unsafe_allow_html=True)
        fig_earth = create_3d_earth_view(itrf1, itrf2, sat1_name, sat2_name, closest["index"], L)
        st.plotly_chart(fig_earth, use_container_width=True, key="3d_earth_chart")

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Telemetry Table ──
        st.markdown(f'<div class="section-title">{t("telemetry_section", L)}</div>', unsafe_allow_html=True)
        render_telemetry_table(closest, rel_vel, sat1_name, sat2_name, L)

        # ── Altitude info ──
        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{t("orbital_section", L)}</div>', unsafe_allow_html=True)

        alt1 = compute_orbital_elements(sat1, ts, time_array)
        alt2 = compute_orbital_elements(sat2, ts, time_array)

        ca_idx = closest["index"]
        col_o1, col_o2 = st.columns(2)

        with col_o1:
            st.markdown(f"""
            <div style="
                background: rgba(0,229,255,0.05);
                border: 1px solid rgba(0,229,255,0.15);
                border-radius: 12px;
                padding: 20px;
            ">
                <div style="font-size: 14px; color: #00E5FF; font-weight: 700; margin-bottom: 12px;">
                    🛰️ {sat1_name}
                </div>
                <div style="color: #B0BEC5; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 2;">
                    {t("altitude_tca", L)}: <span style="color: #00E5FF;">{alt1[ca_idx]:.2f} km</span><br>
                    {t("position_x", L)}: <span style="color: #80CBC4;">{pos1[ca_idx, 0]:.3f} km</span><br>
                    {t("position_y", L)}: <span style="color: #80CBC4;">{pos1[ca_idx, 1]:.3f} km</span><br>
                    {t("position_z", L)}: <span style="color: #80CBC4;">{pos1[ca_idx, 2]:.3f} km</span><br>
                    {t("velocity", L)}: <span style="color: #FF9100;">{np.linalg.norm(vel1[ca_idx]):.4f} km/s</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_o2:
            st.markdown(f"""
            <div style="
                background: rgba(124,77,255,0.05);
                border: 1px solid rgba(124,77,255,0.15);
                border-radius: 12px;
                padding: 20px;
            ">
                <div style="font-size: 14px; color: #B388FF; font-weight: 700; margin-bottom: 12px;">
                    🛰️ {sat2_name}
                </div>
                <div style="color: #B0BEC5; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 2;">
                    {t("altitude_tca", L)}: <span style="color: #B388FF;">{alt2[ca_idx]:.2f} km</span><br>
                    {t("position_x", L)}: <span style="color: #CE93D8;">{pos2[ca_idx, 0]:.3f} km</span><br>
                    {t("position_y", L)}: <span style="color: #CE93D8;">{pos2[ca_idx, 1]:.3f} km</span><br>
                    {t("position_z", L)}: <span style="color: #CE93D8;">{pos2[ca_idx, 2]:.3f} km</span><br>
                    {t("velocity", L)}: <span style="color: #FF9100;">{np.linalg.norm(vel2[ca_idx]):.4f} km/s</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Export Data ──
        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        with st.expander(t("export_section", L)):
            export_df = pd.DataFrame({
                "Time (UTC)": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetimes_list],
                "Distance (km)": distances,
                f"{sat1_name} X (km)": pos1[:, 0],
                f"{sat1_name} Y (km)": pos1[:, 1],
                f"{sat1_name} Z (km)": pos1[:, 2],
                f"{sat2_name} X (km)": pos2[:, 0],
                f"{sat2_name} Y (km)": pos2[:, 1],
                f"{sat2_name} Z (km)": pos2[:, 2],
                "Collision Probability": pc_over_time,
            })
            st.dataframe(export_df, use_container_width=True, height=300)

            csv = export_df.to_csv(index=False).encode('utf-8')
            
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.download_button(
                    label=t("download_csv", L),
                    data=csv,
                    file_name=f"conjunction_analysis_{sat1_name}_{sat2_name}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            
            with col_ex2:
                with st.spinner(t("generate_pdf_report", L) if "generate_pdf_report" in st.session_state.get('lang_dict', {}) else "Preparing PDF..."):
                    tca_str = closest["time"].strftime('%Y-%m-%d %H:%M:%S UTC')
                    pdf_bytes = generate_pdf_report(
                        sat1_name, sat2_name, max_pc, risk_display, 
                        closest["distance_km"], tca_str, 
                        fig_distance, fig_heatmap, fig_3d, fig_earth
                    )
                st.download_button(
                    label=t("download_pdf", L),
                    data=pdf_bytes,
                    file_name=f"report_{sat1_name}_{sat2_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    except Exception as e:
        st.error(t("analysis_error", L, error=str(e)))
        st.exception(e)

else:
    # ── Welcome Screen ──
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 40px;
        margin: 40px auto;
        max-width: 700px;
    ">
        <div style="font-size: 72px; margin-bottom: 24px;">🛰️</div>
        <h2 style="
            color: #E0E0E0;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
        ">
            {t("welcome_title", L)}
        </h2>
        <p style="
            color: #78909C;
            font-size: 15px;
            line-height: 1.8;
            margin-bottom: 32px;
        ">
            {t("welcome_desc", L)}
        </p>
        <div class="welcome-grid">
            <div style="
                background: rgba(0,229,255,0.04);
                border: 1px solid rgba(0,229,255,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #00E5FF; font-size: 20px; margin-bottom: 6px;">📏</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">{t("feature_proximity", L)}</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">{t("feature_proximity_desc", L)}</div>
            </div>
            <div style="
                background: rgba(124,77,255,0.04);
                border: 1px solid rgba(124,77,255,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #B388FF; font-size: 20px; margin-bottom: 6px;">🎯</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">{t("feature_collision", L)}</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">{t("feature_collision_desc", L)}</div>
            </div>
            <div style="
                background: rgba(0,230,118,0.04);
                border: 1px solid rgba(0,230,118,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #00E676; font-size: 20px; margin-bottom: 6px;">🌐</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">{t("feature_3d", L)}</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">{t("feature_3d_desc", L)}</div>
            </div>
            <div style="
                background: rgba(255,145,0,0.04);
                border: 1px solid rgba(255,145,0,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #FF9100; font-size: 20px; margin-bottom: 6px;">⚠️</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">{t("feature_alert", L)}</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">{t("feature_alert_desc", L)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
