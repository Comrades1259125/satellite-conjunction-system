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
)
from core.orbit_calculator import (
    compute_positions,
    compute_velocities,
    generate_time_array,
    compute_orbital_elements,
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
)
from ui.charts import (
    create_distance_chart,
    create_collision_heatmap,
    create_3d_relative_orbit,
)
from ui.alerts import (
    render_risk_banner,
    render_telemetry_table,
    render_metric_cards,
)


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
        top: 8px !important;
        left: 8px !important;
    }
    div[data-testid="collapsedControl"] {
        visibility: visible !important;
        z-index: 9999 !important;
        overflow: visible !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🛰️ Satellite Conjunction Analysis</h1>
    <p>Real-time Proximity Assessment & Collision Probability</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar Configuration ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎛️ Configuration")
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # Input mode
    input_mode = st.radio(
        "Input Mode",
        ["Catalog Selection", "Manual TLE Entry"],
        index=0,
        help="Select satellites from the catalog or enter custom TLE data.",
    )

    if input_mode == "Catalog Selection":
        satellites = get_available_satellites()
        sat1_name = st.selectbox(
            "🛰️ Primary Satellite",
            satellites,
            index=satellites.index("ISS (ZARYA)") if "ISS (ZARYA)" in satellites else 0,
        )
        sat2_name = st.selectbox(
            "🛰️ Secondary Satellite",
            satellites,
            index=satellites.index("COSMOS 2251 DEB") if "COSMOS 2251 DEB" in satellites else 1,
        )
        custom_tle = False
    else:
        st.markdown("#### Primary Satellite")
        sat1_name = st.text_input("Name (Primary)", value="SAT-1")
        sat1_line1 = st.text_area(
            "TLE Line 1 (Primary)",
            value="1 25544U 98067A   24045.54689014  .00024329  00000+0  42556-3 0  9992",
            height=68,
        )
        sat1_line2 = st.text_area(
            "TLE Line 2 (Primary)",
            value="2 25544  51.6410 138.2047 0002273 315.2168 162.4950 15.50562470439891",
            height=68,
        )

        st.markdown("#### Secondary Satellite")
        sat2_name = st.text_input("Name (Secondary)", value="SAT-2")
        sat2_line1 = st.text_area(
            "TLE Line 1 (Secondary)",
            value="1 34427U 93036SX  24041.83168981  .00000516  00000+0  16370-3 0  9994",
            height=68,
        )
        sat2_line2 = st.text_area(
            "TLE Line 2 (Secondary)",
            value="2 34427  74.0202 280.9182 0039927 149.3476 210.9684 14.35878847607451",
            height=68,
        )
        custom_tle = True

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown("## ⏱️ Analysis Window")

    duration_hours = st.slider(
        "Duration (hours)",
        min_value=1,
        max_value=72,
        value=24,
        step=1,
        help="Duration of the analysis window.",
    )

    step_minutes = st.slider(
        "Time Step (minutes)",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        help="Resolution of the time steps.",
    )

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📐 Covariance Settings")

    position_uncertainty = st.number_input(
        "Position Uncertainty σ (km)",
        min_value=0.001,
        max_value=10.0,
        value=0.1,
        step=0.01,
        format="%.3f",
        help="Combined 1-sigma position uncertainty for both objects.",
    )

    combined_radius = st.number_input(
        "Combined Hard-Body Radius (km)",
        min_value=0.001,
        max_value=1.0,
        value=0.01,
        step=0.001,
        format="%.3f",
        help="Sum of the physical radii of both objects.",
    )

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    run_analysis = st.button("🚀 RUN CONJUNCTION ANALYSIS", use_container_width=True)

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 16px 0;
        color: #37474F;
        font-size: 11px;
        margin-top: 16px;
    ">
        Analysis time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}<br>
        Powered by Skyfield + Plotly
    </div>
    """, unsafe_allow_html=True)


# ─── Main Analysis ────────────────────────────────────────────────────────────

if run_analysis:
    try:
        # ── Load satellites ──
        with st.spinner("🔄 Loading satellite TLE data..."):
            ts = load.timescale()

            if custom_tle:
                sat1 = get_satellite_from_tle(sat1_name, sat1_line1, sat1_line2, ts)
                sat2 = get_satellite_from_tle(sat2_name, sat2_line1, sat2_line2, ts)
            else:
                sat1 = get_satellite(sat1_name, ts)
                sat2 = get_satellite(sat2_name, ts)

        st.success(f"✅ Loaded: **{sat1_name}** & **{sat2_name}**")

        # ── Generate time array ──
        with st.spinner(f"⏳ Generating {duration_hours}h timeline ({step_minutes}min steps)..."):
            time_array, datetimes_list = generate_time_array(ts, duration_hours, step_minutes)
            total_steps = len(datetimes_list)

        # ── Compute positions & velocities ──
        with st.spinner("📡 Computing orbital positions..."):
            progress = st.progress(0, text=f"Computing {sat1_name} positions...")
            pos1 = compute_positions(sat1, ts, time_array)
            progress.progress(25, text=f"Computing {sat2_name} positions...")
            pos2 = compute_positions(sat2, ts, time_array)
            progress.progress(50, text=f"Computing {sat1_name} velocities...")
            vel1 = compute_velocities(sat1, ts, time_array)
            progress.progress(75, text=f"Computing {sat2_name} velocities...")
            vel2 = compute_velocities(sat2, ts, time_array)
            progress.progress(100, text="✅ Positions computed!")

        # ── Proximity analysis ──
        with st.spinner("📏 Analyzing proximity..."):
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

            # Heatmap data
            heatmap_data, uncertainty_levels, time_indices = generate_covariance_heatmap_data(
                distances, datetimes_list, position_uncertainty, combined_radius
            )

        # ── Clear progress bar ──
        progress.empty()

        # ═══════════════════════════════════════════════════════════════════
        # RESULTS
        # ═══════════════════════════════════════════════════════════════════

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Risk Banner ──
        render_risk_banner(risk_name, risk_color, risk_emoji, closest["distance_km"])

        # ── Metric Cards ──
        render_metric_cards(closest, rel_vel, (risk_name, risk_color, risk_emoji))

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
                    Collision Probability @ TCA
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
                    Max Collision Probability (window)
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
                    Over {duration_hours}h analysis window
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Graph 1: Distance Over Time ──
        st.markdown('<div class="section-title">📡 Distance Over Time</div>', unsafe_allow_html=True)
        fig_distance = create_distance_chart(datetimes_list, distances, closest)
        st.plotly_chart(fig_distance, use_container_width=True, key="distance_chart")

        # ── Graph 2: Collision Probability Heatmap ──
        st.markdown('<div class="section-title">🎯 Collision Probability Heatmap</div>', unsafe_allow_html=True)
        fig_heatmap = create_collision_heatmap(heatmap_data, uncertainty_levels, time_indices, datetimes_list)
        st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap_chart")

        # ── Graph 3: 3D Relative Orbit ──
        st.markdown('<div class="section-title">🌐 3D Relative Orbit (RIC Frame)</div>', unsafe_allow_html=True)
        fig_3d = create_3d_relative_orbit(relative_ric, closest["index"])
        st.plotly_chart(fig_3d, use_container_width=True, key="3d_orbit_chart")

        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        # ── Telemetry Table ──
        st.markdown('<div class="section-title">📊 Telemetry Summary</div>', unsafe_allow_html=True)
        render_telemetry_table(closest, rel_vel, sat1_name, sat2_name)

        # ── Altitude info ──
        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🌍 Orbital Parameters at TCA</div>', unsafe_allow_html=True)

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
                    Altitude @ TCA: <span style="color: #00E5FF;">{alt1[ca_idx]:.2f} km</span><br>
                    Position X: <span style="color: #80CBC4;">{pos1[ca_idx, 0]:.3f} km</span><br>
                    Position Y: <span style="color: #80CBC4;">{pos1[ca_idx, 1]:.3f} km</span><br>
                    Position Z: <span style="color: #80CBC4;">{pos1[ca_idx, 2]:.3f} km</span><br>
                    Velocity: <span style="color: #FF9100;">{np.linalg.norm(vel1[ca_idx]):.4f} km/s</span>
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
                    Altitude @ TCA: <span style="color: #B388FF;">{alt2[ca_idx]:.2f} km</span><br>
                    Position X: <span style="color: #CE93D8;">{pos2[ca_idx, 0]:.3f} km</span><br>
                    Position Y: <span style="color: #CE93D8;">{pos2[ca_idx, 1]:.3f} km</span><br>
                    Position Z: <span style="color: #CE93D8;">{pos2[ca_idx, 2]:.3f} km</span><br>
                    Velocity: <span style="color: #FF9100;">{np.linalg.norm(vel2[ca_idx]):.4f} km/s</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Export Data ──
        st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

        with st.expander("📥 Export Analysis Data"):
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

            csv = export_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"conjunction_analysis_{sat1_name}_{sat2_name}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    except Exception as e:
        st.error(f"❌ Analysis Error: {str(e)}")
        st.exception(e)

else:
    # ── Welcome Screen ──
    st.markdown("""
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
            Satellite Conjunction Analysis System
        </h2>
        <p style="
            color: #78909C;
            font-size: 15px;
            line-height: 1.8;
            margin-bottom: 32px;
        ">
            Select two satellites from the sidebar catalog or enter custom TLE data,
            then click <strong style="color: #00E5FF;">RUN CONJUNCTION ANALYSIS</strong>
            to compute orbital trajectories, proximity distances, and collision probability.
        </p>
        <div class="welcome-grid">
            <div style="
                background: rgba(0,229,255,0.04);
                border: 1px solid rgba(0,229,255,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #00E5FF; font-size: 20px; margin-bottom: 6px;">📏</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">Proximity Analysis</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">Euclidean distance at every time step</div>
            </div>
            <div style="
                background: rgba(124,77,255,0.04);
                border: 1px solid rgba(124,77,255,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #B388FF; font-size: 20px; margin-bottom: 6px;">🎯</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">Collision Probability</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">Pc estimation with covariance model</div>
            </div>
            <div style="
                background: rgba(0,230,118,0.04);
                border: 1px solid rgba(0,230,118,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #00E676; font-size: 20px; margin-bottom: 6px;">🌐</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">3D Relative Orbit</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">RIC frame visualization</div>
            </div>
            <div style="
                background: rgba(255,145,0,0.04);
                border: 1px solid rgba(255,145,0,0.1);
                border-radius: 10px;
                padding: 16px;
            ">
                <div style="color: #FF9100; font-size: 20px; margin-bottom: 6px;">⚠️</div>
                <div style="color: #B0BEC5; font-size: 13px; font-weight: 600;">Alert System</div>
                <div style="color: #546E7A; font-size: 11px; margin-top: 4px;">Green / Yellow / Red risk bands</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
