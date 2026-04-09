"""
Alerts Module
Risk level indicators and alert system for the conjunction analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from core.translations import t


def render_risk_banner(risk_level, risk_color, risk_emoji, distance_km, min_distance_label="Minimum Distance"):
    """
    Render a large risk-level banner at the top of the dashboard.
    """
    glow_color = risk_color
    # Use color-based detection for gradient (risk_level may be translated)
    if risk_color == "#FF1744":
        bg_gradient = "linear-gradient(135deg, rgba(255,23,68,0.15), rgba(183,28,28,0.1))"
        border_color = "#FF1744"
        pulse_class = "pulse-critical"
    elif risk_color == "#FFC107":
        bg_gradient = "linear-gradient(135deg, rgba(255,193,7,0.12), rgba(245,127,23,0.08))"
        border_color = "#FFC107"
        pulse_class = "pulse-warning"
    else:
        bg_gradient = "linear-gradient(135deg, rgba(0,230,118,0.10), rgba(0,200,83,0.06))"
        border_color = "#00E676"
        pulse_class = "pulse-safe"

    st.markdown(f"""
    <div style="
        background: {bg_gradient};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: clamp(16px, 3vw, 24px) clamp(16px, 4vw, 32px);
        margin-bottom: 24px;
        text-align: center;
        box-shadow: 0 0 30px rgba({','.join(str(int(border_color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))}, 0.15);
    ">
        <div style="font-size: clamp(32px, 6vw, 48px); margin-bottom: 8px;">{risk_emoji}</div>
        <div style="
            font-size: clamp(20px, 4vw, 28px);
            font-weight: 800;
            color: {risk_color};
            letter-spacing: 4px;
            font-family: 'JetBrains Mono', monospace;
            text-shadow: 0 0 20px {glow_color}40;
        ">
            {risk_level}
        </div>
        <div style="
            font-size: 14px;
            color: #78909C;
            margin-top: 8px;
            font-family: 'Inter', sans-serif;
        ">
            {min_distance_label}: <span style="color: {risk_color}; font-weight: 700;">{distance_km:.3f} km</span>
            ({distance_km * 1000:.1f} m)
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_telemetry_table(closest_approach, relative_velocity, sat1_name, sat2_name, lang="en"):
    """
    Render the telemetry summary table at the closest approach point.
    """
    ca_time = closest_approach["time"]
    ca_dist_km = closest_approach["distance_km"]
    ca_dist_m = closest_approach["distance_m"]
    rel_vel_km_s = relative_velocity["magnitude_km_s"]
    rel_vel_m_s = relative_velocity["magnitude_m_s"]
    rel_vec = relative_velocity["vector"]

    data = {
        t("col_parameter", lang): [
            t("param_primary", lang),
            t("param_secondary", lang),
            t("param_tca", lang),
            t("param_miss_dist", lang),
            t("param_miss_dist_m", lang),
            t("param_rel_vel", lang),
            t("param_rel_vel_ms", lang),
            t("param_dvx", lang),
            t("param_dvy", lang),
            t("param_dvz", lang),
        ],
        t("col_value", lang): [
            sat1_name,
            sat2_name,
            ca_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            f"{ca_dist_km:.4f} km",
            f"{ca_dist_m:.2f} m",
            f"{rel_vel_km_s:.4f} km/s",
            f"{rel_vel_m_s:.2f} m/s",
            f"{rel_vec[0]:.6f} km/s",
            f"{rel_vec[1]:.6f} km/s",
            f"{rel_vec[2]:.6f} km/s",
        ],
    }

    df = pd.DataFrame(data)

    st.markdown("""
    <style>
    .telemetry-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 16px;
        color: #00E5FF;
        letter-spacing: 2px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    </style>
    <div class="telemetry-title">{t("telemetry_title", lang)}</div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            t("col_parameter", lang): st.column_config.TextColumn(t("col_parameter", lang), width="medium"),
            t("col_value", lang): st.column_config.TextColumn(t("col_value", lang), width="medium"),
        },
    )


def render_metric_cards(closest_approach, relative_velocity, risk_level_info, lang="en"):
    """
    Render summary metric cards in a row.
    """
    risk_name, risk_color, risk_emoji = risk_level_info
    ca_dist = closest_approach["distance_km"]
    ca_time = closest_approach["time"]
    rel_vel = relative_velocity["magnitude_km_s"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(0,176,255,0.04));
            border: 1px solid rgba(0,229,255,0.2);
            border-radius: 12px;
            padding: clamp(12px, 2vw, 20px);
            text-align: center;
        ">
            <div style="font-size: clamp(10px, 1.5vw, 12px); color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">{t("card_min_distance", lang)}</div>
            <div style="font-size: clamp(18px, 3vw, 24px); font-weight: 800; color: #00E5FF; font-family: 'JetBrains Mono', monospace; margin-top: 8px;">
                {ca_dist:.3f} km
            </div>
            <div style="font-size: 11px; color: #78909C; margin-top: 4px;">{ca_dist*1000:.1f} {t("meters", lang)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(124,77,255,0.08), rgba(101,31,255,0.04));
            border: 1px solid rgba(124,77,255,0.2);
            border-radius: 12px;
            padding: clamp(12px, 2vw, 20px);
            text-align: center;
        ">
            <div style="font-size: clamp(10px, 1.5vw, 12px); color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">{t("card_tca_time", lang)}</div>
            <div style="font-size: clamp(14px, 2.5vw, 18px); font-weight: 700; color: #B388FF; font-family: 'JetBrains Mono', monospace; margin-top: 8px;">
                {ca_time.strftime("%H:%M:%S")}
            </div>
            <div style="font-size: 11px; color: #78909C; margin-top: 4px;">{ca_time.strftime("%Y-%m-%d")} UTC</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,145,0,0.08), rgba(245,124,0,0.04));
            border: 1px solid rgba(255,145,0,0.2);
            border-radius: 12px;
            padding: clamp(12px, 2vw, 20px);
            text-align: center;
        ">
            <div style="font-size: clamp(10px, 1.5vw, 12px); color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">{t("card_rel_velocity", lang)}</div>
            <div style="font-size: clamp(18px, 3vw, 24px); font-weight: 800; color: #FF9100; font-family: 'JetBrains Mono', monospace; margin-top: 8px;">
                {rel_vel:.2f}
            </div>
            <div style="font-size: 11px; color: #78909C; margin-top: 4px;">km/s ({rel_vel*1000:.0f} m/s)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {risk_color}14, {risk_color}08);
            border: 1px solid {risk_color}33;
            border-radius: 12px;
            padding: clamp(12px, 2vw, 20px);
            text-align: center;
        ">
            <div style="font-size: clamp(10px, 1.5vw, 12px); color: #546E7A; text-transform: uppercase; letter-spacing: 1px;">{t("card_risk_level", lang)}</div>
            <div style="font-size: clamp(20px, 4vw, 28px); margin-top: 8px;">{risk_emoji}</div>
            <div style="font-size: clamp(12px, 2vw, 14px); font-weight: 800; color: {risk_color}; letter-spacing: 2px; font-family: 'JetBrains Mono', monospace;">{risk_name}</div>
        </div>
        """, unsafe_allow_html=True)
