"""
Translations Module
Thai/English language support for the Satellite Conjunction Analysis System.
"""

TRANSLATIONS = {
    "en": {
        # ── Header ──
        "app_title": "🛰️ Satellite Conjunction Analysis",
        "app_subtitle": "Real-time Proximity Assessment & Collision Probability",

        # ── Sidebar ──
        "config_title": "## 🎛️ Configuration",
        "input_mode": "Input Mode",
        "catalog_selection": "Catalog Selection",
        "manual_tle": "Manual TLE Entry",
        "primary_satellite": "🛰️ Primary Satellite",
        "secondary_satellite": "🛰️ Secondary Satellite",
        "primary_name": "Name (Primary)",
        "secondary_name": "Name (Secondary)",
        "tle_line1_primary": "TLE Line 1 (Primary)",
        "tle_line2_primary": "TLE Line 2 (Primary)",
        "tle_line1_secondary": "TLE Line 1 (Secondary)",
        "tle_line2_secondary": "TLE Line 2 (Secondary)",
        "primary_header": "#### Primary Satellite",
        "secondary_header": "#### Secondary Satellite",
        "input_mode_help": "Select satellites from the catalog or enter custom TLE data.",
        "analysis_window": "## ⏱️ Analysis Window",
        "duration_label": "Duration (hours)",
        "duration_help": "Duration of the analysis window.",
        "timestep_label": "Time Step (minutes)",
        "timestep_help": "Resolution of the time steps.",
        "covariance_title": "## 📐 Covariance Settings",
        "pos_uncertainty_label": "Position Uncertainty σ (km)",
        "pos_uncertainty_help": "Combined 1-sigma position uncertainty for both objects.",
        "combined_radius_label": "Combined Hard-Body Radius (km)",
        "combined_radius_help": "Sum of the physical radii of both objects.",
        "run_button": "🚀 RUN CONJUNCTION ANALYSIS",
        "powered_by": "Powered by Skyfield + Plotly",
        "language_label": "🌐 Language / ภาษา",

        # ── Analysis ──
        "loading_tle": "🔄 Loading satellite TLE data...",
        "loaded_success": "✅ Loaded: **{sat1}** & **{sat2}**",
        "generating_timeline": "⏳ Generating {hours}h timeline ({step}min steps)...",
        "computing_positions": "📡 Computing orbital positions...",
        "computing_sat_pos": "Computing {name} positions...",
        "computing_sat_vel": "Computing {name} velocities...",
        "positions_done": "✅ Positions computed!",
        "analyzing_proximity": "📏 Analyzing proximity...",
        "analysis_error": "❌ Analysis Error: {error}",

        # ── Results ──
        "pc_at_tca_title": "Collision Probability @ TCA",
        "max_pc_title": "Max Collision Probability (window)",
        "over_window": "Over {hours}h analysis window",
        "distance_section": "📡 Distance Over Time",
        "heatmap_section": "🎯 Collision Probability Heatmap",
        "ric_section": "🌐 3D Relative Orbit (RIC Frame)",
        "telemetry_section": "📊 Telemetry Summary",
        "orbital_section": "🌍 Orbital Parameters at TCA",
        "export_section": "📥 Export Analysis Data",
        "download_csv": "⬇️ Download CSV",

        # ── Risk Levels ──
        "min_distance_label": "Minimum Distance",
        "risk_critical": "CRITICAL",
        "risk_warning": "WARNING",
        "risk_safe": "SAFE",

        # ── Metric Cards ──
        "card_min_distance": "Min Distance",
        "card_tca_time": "TCA Time",
        "card_rel_velocity": "Rel. Velocity",
        "card_risk_level": "Risk Level",
        "meters": "meters",

        # ── Telemetry Table ──
        "param_primary": "🛰️ Primary Object",
        "param_secondary": "🛰️ Secondary Object",
        "param_tca": "⏱️ Time of Closest Approach (TCA)",
        "param_miss_dist": "📏 Miss Distance",
        "param_miss_dist_m": "📏 Miss Distance (meters)",
        "param_rel_vel": "💨 Relative Velocity",
        "param_rel_vel_ms": "💨 Relative Velocity (m/s)",
        "param_dvx": "↔️ ΔVx",
        "param_dvy": "↕️ ΔVy",
        "param_dvz": "🔄 ΔVz",
        "col_parameter": "Parameter",
        "col_value": "Value",
        "telemetry_title": "📊 Telemetry Summary @ TCA",

        # ── Orbital Parameters ──
        "altitude_tca": "Altitude @ TCA",
        "position_x": "Position X",
        "position_y": "Position Y",
        "position_z": "Position Z",
        "velocity": "Velocity",

        # ── Charts ──
        "chart_distance_title": "📡 Satellite Separation Distance Over Time",
        "chart_x_time": "Time (UTC)",
        "chart_y_distance": "Distance (km)",
        "chart_distance_trace": "Distance",
        "chart_closest_approach": "Closest Approach",
        "chart_critical_zone": "CRITICAL ZONE",
        "chart_warning_zone": "WARNING ZONE",
        "chart_2km_threshold": "2 km threshold",
        "chart_10km_threshold": "10 km threshold",
        "chart_heatmap_title": "🎯 Collision Probability Heatmap (Pc vs Covariance)",
        "chart_y_uncertainty": "Position Uncertainty σ (km)",
        "chart_3d_title": "🌐 3D Relative Orbit (RIC Frame — as seen from SAT-1)",
        "chart_3d_trajectory": "Relative Trajectory",
        "chart_3d_primary": "Primary (SAT-1)",
        "chart_3d_intrack": "In-track (km)",
        "chart_3d_crosstrack": "Cross-track (km)",
        "chart_3d_radial": "Radial (km)",
        "chart_3d_start": "Start",
        "chart_3d_end": "End",

        # ── Welcome ──
        "welcome_title": "Satellite Conjunction Analysis System",
        "welcome_desc": "Select two satellites from the sidebar catalog or enter custom TLE data, then click <strong style=\"color: #00E5FF;\">RUN CONJUNCTION ANALYSIS</strong> to compute orbital trajectories, proximity distances, and collision probability.",
        "feature_proximity": "Proximity Analysis",
        "feature_proximity_desc": "Euclidean distance at every time step",
        "feature_collision": "Collision Probability",
        "feature_collision_desc": "Pc estimation with covariance model",
        "feature_3d": "3D Relative Orbit",
        "feature_3d_desc": "RIC frame visualization",
        "feature_alert": "Alert System",
        "feature_alert_desc": "Green / Yellow / Red risk bands",

        # ── Advanced Features ──
        "app_mode": "App Mode",
        "mode_1on1": "1-on-1 Analysis",
        "mode_scanner": "Broad Catalog Scanner",
        "start_time_label": "Start Time (UTC)",
        "tle_freshness": "TLE Freshness",
        "tle_fresh": "🟢 Fresh",
        "tle_warning": "🟡 Aging",
        "tle_stale": "🔴 Stale",
        "maneuver_title": "## 🚀 Maneuver Configurator",
        "dv_x": "Delta-V In-track (m/s)",
        "dv_y": "Delta-V Cross-track (m/s)",
        "dv_z": "Delta-V Radial (m/s)",
        "earth_3d_title": "🌍 3D Earth Orbit View (ITRF)",
        "scan_title": "🛰️ Top Catalog Threats",
        "scanning": "Scanning {count} satellites...",
        "export_pdf": "📄 Export PDF Report",
    },

    "th": {
        # ── Header ──
        "app_title": "🛰️ ระบบวิเคราะห์การเข้าใกล้ของดาวเทียม",
        "app_subtitle": "ประเมินความใกล้ชิดและความน่าจะเป็นการชนแบบเรียลไทม์",

        # ── Sidebar ──
        "config_title": "## 🎛️ ตั้งค่า",
        "input_mode": "โหมดป้อนข้อมูล",
        "catalog_selection": "เลือกจากแคตตาล็อก",
        "manual_tle": "ป้อน TLE เอง",
        "primary_satellite": "🛰️ ดาวเทียมหลัก",
        "secondary_satellite": "🛰️ ดาวเทียมรอง",
        "primary_name": "ชื่อ (ดาวเทียมหลัก)",
        "secondary_name": "ชื่อ (ดาวเทียมรอง)",
        "tle_line1_primary": "TLE บรรทัด 1 (หลัก)",
        "tle_line2_primary": "TLE บรรทัด 2 (หลัก)",
        "tle_line1_secondary": "TLE บรรทัด 1 (รอง)",
        "tle_line2_secondary": "TLE บรรทัด 2 (รอง)",
        "primary_header": "#### ดาวเทียมหลัก",
        "secondary_header": "#### ดาวเทียมรอง",
        "input_mode_help": "เลือกดาวเทียมจากแคตตาล็อก หรือป้อนข้อมูล TLE เอง",
        "analysis_window": "## ⏱️ ช่วงเวลาวิเคราะห์",
        "duration_label": "ระยะเวลา (ชั่วโมง)",
        "duration_help": "ระยะเวลาของการวิเคราะห์",
        "timestep_label": "ช่วงเวลา (นาที)",
        "timestep_help": "ความละเอียดของช่วงเวลา",
        "covariance_title": "## 📐 ตั้งค่าความแปรปรวนร่วม",
        "pos_uncertainty_label": "ความไม่แน่นอนตำแหน่ง σ (km)",
        "pos_uncertainty_help": "ค่าความไม่แน่นอนตำแหน่ง 1-sigma รวมของทั้ง 2 วัตถุ",
        "combined_radius_label": "รัศมีรวม Hard-Body (km)",
        "combined_radius_help": "ผลรวมของรัศมีกายภาพของวัตถุทั้ง 2 ชิ้น",
        "run_button": "🚀 เริ่มวิเคราะห์การเข้าใกล้",
        "powered_by": "ขับเคลื่อนโดย Skyfield + Plotly",
        "language_label": "🌐 Language / ภาษา",

        # ── Analysis ──
        "loading_tle": "🔄 กำลังโหลดข้อมูล TLE ดาวเทียม...",
        "loaded_success": "✅ โหลดแล้ว: **{sat1}** และ **{sat2}**",
        "generating_timeline": "⏳ กำลังสร้างไทม์ไลน์ {hours} ชม. (ทุก {step} นาที)...",
        "computing_positions": "📡 กำลังคำนวณตำแหน่งวงโคจร...",
        "computing_sat_pos": "กำลังคำนวณตำแหน่ง {name}...",
        "computing_sat_vel": "กำลังคำนวณความเร็ว {name}...",
        "positions_done": "✅ คำนวณตำแหน่งเสร็จสิ้น!",
        "analyzing_proximity": "📏 กำลังวิเคราะห์ความใกล้ชิด...",
        "analysis_error": "❌ เกิดข้อผิดพลาดในการวิเคราะห์: {error}",

        # ── Results ──
        "pc_at_tca_title": "ความน่าจะเป็นการชน ณ TCA",
        "max_pc_title": "ความน่าจะเป็นการชนสูงสุด (ทั้งช่วง)",
        "over_window": "ตลอดช่วงวิเคราะห์ {hours} ชม.",
        "distance_section": "📡 ระยะห่างตามเวลา",
        "heatmap_section": "🎯 แผนที่ความร้อนความน่าจะเป็นการชน",
        "ric_section": "🌐 วงโคจรสัมพัทธ์ 3 มิติ (กรอบ RIC)",
        "telemetry_section": "📊 สรุปข้อมูลเทเลเมทรี",
        "orbital_section": "🌍 พารามิเตอร์วงโคจร ณ TCA",
        "export_section": "📥 ส่งออกข้อมูลวิเคราะห์",
        "download_csv": "⬇️ ดาวน์โหลด CSV",

        # ── Risk Levels ──
        "min_distance_label": "ระยะห่างต่ำสุด",
        "risk_critical": "วิกฤต",
        "risk_warning": "เตือน",
        "risk_safe": "ปลอดภัย",

        # ── Metric Cards ──
        "card_min_distance": "ระยะต่ำสุด",
        "card_tca_time": "เวลา TCA",
        "card_rel_velocity": "ความเร็วสัมพัทธ์",
        "card_risk_level": "ระดับความเสี่ยง",
        "meters": "เมตร",

        # ── Telemetry Table ──
        "param_primary": "🛰️ วัตถุหลัก",
        "param_secondary": "🛰️ วัตถุรอง",
        "param_tca": "⏱️ เวลาเข้าใกล้สุด (TCA)",
        "param_miss_dist": "📏 ระยะห่าง",
        "param_miss_dist_m": "📏 ระยะห่าง (เมตร)",
        "param_rel_vel": "💨 ความเร็วสัมพัทธ์",
        "param_rel_vel_ms": "💨 ความเร็วสัมพัทธ์ (m/s)",
        "param_dvx": "↔️ ΔVx",
        "param_dvy": "↕️ ΔVy",
        "param_dvz": "🔄 ΔVz",
        "col_parameter": "พารามิเตอร์",
        "col_value": "ค่า",
        "telemetry_title": "📊 สรุปเทเลเมทรี ณ TCA",

        # ── Orbital Parameters ──
        "altitude_tca": "ความสูง ณ TCA",
        "position_x": "ตำแหน่ง X",
        "position_y": "ตำแหน่ง Y",
        "position_z": "ตำแหน่ง Z",
        "velocity": "ความเร็ว",

        # ── Charts ──
        "chart_distance_title": "📡 ระยะห่างระหว่างดาวเทียมตามเวลา",
        "chart_x_time": "เวลา (UTC)",
        "chart_y_distance": "ระยะห่าง (km)",
        "chart_distance_trace": "ระยะห่าง",
        "chart_closest_approach": "จุดเข้าใกล้สุด",
        "chart_critical_zone": "โซนวิกฤต",
        "chart_warning_zone": "โซนเตือน",
        "chart_2km_threshold": "เกณฑ์ 2 km",
        "chart_10km_threshold": "เกณฑ์ 10 km",
        "chart_heatmap_title": "🎯 แผนที่ความร้อน Pc (Pc เทียบกับ Covariance)",
        "chart_y_uncertainty": "ความไม่แน่นอนตำแหน่ง σ (km)",
        "chart_3d_title": "🌐 วงโคจรสัมพัทธ์ 3 มิติ (กรอบ RIC — มองจาก SAT-1)",
        "chart_3d_trajectory": "เส้นทางสัมพัทธ์",
        "chart_3d_primary": "ดาวเทียมหลัก (SAT-1)",
        "chart_3d_intrack": "In-track (km)",
        "chart_3d_crosstrack": "Cross-track (km)",
        "chart_3d_radial": "Radial (km)",
        "chart_3d_start": "เริ่มต้น",
        "chart_3d_end": "สิ้นสุด",

        # ── Welcome ──
        "welcome_title": "ระบบวิเคราะห์การเข้าใกล้ของดาวเทียม",
        "welcome_desc": "เลือกดาวเทียม 2 ดวงจากแถบด้านข้าง หรือป้อนข้อมูล TLE เอง จากนั้นกด <strong style=\"color: #00E5FF;\">เริ่มวิเคราะห์การเข้าใกล้</strong> เพื่อคำนวณวงโคจร ระยะห่าง และความน่าจะเป็นการชน",
        "feature_proximity": "วิเคราะห์ความใกล้ชิด",
        "feature_proximity_desc": "ระยะห่างยูคลิเดียนทุก time step",
        "feature_collision": "ความน่าจะเป็นการชน",
        "feature_collision_desc": "ประมาณค่า Pc ด้วยแบบจำลอง covariance",
        "feature_3d": "วงโคจรสัมพัทธ์ 3D",
        "feature_3d_desc": "แสดงผลในกรอบ RIC",
        "feature_alert": "ระบบแจ้งเตือน",
        "feature_alert_desc": "แถบระดับ เขียว / เหลือง / แดง",

        # ── Advanced Features ──
        "app_mode": "โหมดแอปพลิเคชัน",
        "mode_1on1": "วิเคราะห์เจาะลึก 1-ต่อ-1",
        "mode_scanner": "สแกนหาภัยคุกคามรอบตัว",
        "start_time_label": "เวลาเริ่มต้น (UTC)",
        "tle_freshness": "ความใหม่ของข้อมูล TLE",
        "tle_fresh": "🟢 ใหม่",
        "tle_warning": "🟡 เริ่มเก่า",
        "tle_stale": "🔴 เก่าเกินไป",
        "maneuver_title": "## 🚀 ระบบจำลองหลบหลีก (Maneuver)",
        "dv_x": "Delta-V In-track (m/s)",
        "dv_y": "Delta-V Cross-track (m/s)",
        "dv_z": "Delta-V Radial (m/s)",
        "earth_3d_title": "🌍 วงโคจร 3 มิติบนผิวโลก (กรอบ ITRF)",
        "scan_title": "🛰️ ภัยคุกคามสูงสุดจากแคตตาล็อก",
        "scanning": "กำลังสแกนดาวเทียม {count} ดวง...",
        "export_pdf": "📄 ส่งออกรายงาน PDF",
    },
}


def t(key, lang="en", **kwargs):
    """Get translated string by key and language, with optional format kwargs."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
