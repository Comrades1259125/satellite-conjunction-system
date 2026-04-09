"""
Charts Module
Creates all Plotly visualizations for the Conjunction Analysis dashboard.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.translations import t


def create_distance_chart(datetimes, distances, closest_approach, lang="en"):
    """
    Graph 1: Distance over Time line chart.
    Shows the Euclidean distance between two satellites over the analysis window.
    """
    # Determine risk zones
    fig = go.Figure()

    # Add risk zone backgrounds
    fig.add_hrect(
        y0=0, y1=2,
        fillcolor="rgba(255, 23, 68, 0.08)",
        line_width=0,
        annotation_text=t("chart_critical_zone", lang),
        annotation_position="top left",
        annotation_font=dict(color="#FF1744", size=10),
    )
    fig.add_hrect(
        y0=2, y1=10,
        fillcolor="rgba(255, 193, 7, 0.06)",
        line_width=0,
        annotation_text=t("chart_warning_zone", lang),
        annotation_position="top left",
        annotation_font=dict(color="#FFC107", size=10),
    )

    # Color the line by risk level
    colors = []
    for d in distances:
        if d < 2:
            colors.append("#FF1744")
        elif d < 10:
            colors.append("#FFC107")
        else:
            colors.append("#00E5FF")

    # Main distance line
    fig.add_trace(go.Scatter(
        x=datetimes,
        y=distances,
        mode="lines",
        name=t("chart_distance_trace", lang),
        line=dict(color="#00E5FF", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 229, 255, 0.05)",
        hovertemplate="<b>Time:</b> %{x|%Y-%m-%d %H:%M UTC}<br>"
                      "<b>Distance:</b> %{y:.3f} km<br>"
                      "<extra></extra>",
    ))

    # Mark closest approach
    ca_time = closest_approach["time"]
    ca_dist = closest_approach["distance_km"]
    fig.add_trace(go.Scatter(
        x=[ca_time],
        y=[ca_dist],
        mode="markers+text",
        name=t("chart_closest_approach", lang),
        marker=dict(
            color="#FF1744",
            size=14,
            symbol="diamond",
            line=dict(color="white", width=2),
        ),
        text=[f"  TCA: {ca_dist:.3f} km"],
        textposition="top right",
        textfont=dict(color="#FF1744", size=12, family="JetBrains Mono"),
        hovertemplate="<b>⚠️ CLOSEST APPROACH</b><br>"
                      "<b>Time:</b> %{x|%Y-%m-%d %H:%M:%S UTC}<br>"
                      "<b>Distance:</b> %{y:.3f} km (%{customdata:.1f} m)<br>"
                      "<extra></extra>",
        customdata=[ca_dist * 1000],
    ))

    # Add threshold lines
    fig.add_hline(y=2, line_dash="dash", line_color="#FF1744", line_width=1,
                  annotation_text=t("chart_2km_threshold", lang), annotation_font_color="#FF1744")
    fig.add_hline(y=10, line_dash="dash", line_color="#FFC107", line_width=1,
                  annotation_text=t("chart_10km_threshold", lang), annotation_font_color="#FFC107")

    fig.update_layout(
        title=dict(
            text=t("chart_distance_title", lang),
            font=dict(size=18, color="#E0E0E0", family="Inter"),
        ),
        xaxis_title=t("chart_x_time", lang),
        yaxis_title=t("chart_y_distance", lang),
        template="plotly_dark",
        paper_bgcolor="rgba(13, 17, 23, 0.95)",
        plot_bgcolor="rgba(13, 17, 23, 0.8)",
        font=dict(family="Inter, sans-serif", color="#B0BEC5"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            showgrid=True,
            zeroline=False,
            type="log" if max(distances) > 1000 else "linear",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(size=11),
        ),
        height=500,
        margin=dict(l=60, r=30, t=60, b=50),
    )

    return fig


def create_collision_heatmap(heatmap_data, uncertainty_levels, time_indices, datetimes, lang="en"):
    """
    Graph 2: Collision Probability Heatmap.
    Shows how probability varies with time and position uncertainty.
    """
    # Get subset of datetime labels
    time_labels = [datetimes[i].strftime("%H:%M") for i in time_indices]

    # Use log scale for better visualization
    log_data = np.log10(heatmap_data + 1e-30)

    fig = go.Figure(data=go.Heatmap(
        z=log_data,
        x=time_labels,
        y=[f"{u:.3f}" for u in uncertainty_levels],
        colorscale=[
            [0.0, "rgba(13, 17, 23, 1)"],
            [0.2, "#0D47A1"],
            [0.4, "#1565C0"],
            [0.5, "#00BCD4"],
            [0.6, "#FFC107"],
            [0.8, "#FF5722"],
            [1.0, "#FF1744"],
        ],
        colorbar=dict(
            title=dict(text="log₁₀(Pc)", font=dict(color="#B0BEC5")),
            tickfont=dict(color="#B0BEC5"),
            bgcolor="rgba(0,0,0,0.3)",
        ),
        hovertemplate="<b>Time:</b> %{x} UTC<br>"
                      "<b>Uncertainty:</b> %{y} km<br>"
                      "<b>log₁₀(Pc):</b> %{z:.2f}<br>"
                      "<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=t("chart_heatmap_title", lang),
            font=dict(size=18, color="#E0E0E0", family="Inter"),
        ),
        xaxis_title=t("chart_x_time", lang),
        yaxis_title=t("chart_y_uncertainty", lang),
        template="plotly_dark",
        paper_bgcolor="rgba(13, 17, 23, 0.95)",
        plot_bgcolor="rgba(13, 17, 23, 0.8)",
        font=dict(family="Inter, sans-serif", color="#B0BEC5"),
        height=450,
        margin=dict(l=80, r=30, t=60, b=50),
        xaxis=dict(
            tickangle=-45,
            dtick=max(1, len(time_labels) // 20),
        ),
    )

    return fig


def create_3d_relative_orbit(relative_ric, closest_approach_idx, lang="en", perturbed_ric=None):
    """
    Graph 3: 3D Relative Orbit in RIC frame.
    Shows the trajectory of satellite 2 relative to satellite 1.
    """
    R = relative_ric[:, 0]
    I = relative_ric[:, 1]
    C = relative_ric[:, 2]

    # Distance from origin for coloring
    dist = np.sqrt(R**2 + I**2 + C**2)

    fig = go.Figure()

    # Orbit trajectory (Unperturbed)
    fig.add_trace(go.Scatter3d(
        x=I, y=C, z=R,
        mode="lines",
        name=t("chart_3d_trajectory", lang),
        line=dict(
            color=dist,
            colorscale=[
                [0, "#FF1744"],
                [0.3, "#FF9100"],
                [0.5, "#FFC107"],
                [0.7, "#00BCD4"],
                [1.0, "#00E5FF"],
            ],
            width=4 if perturbed_ric is None else 2,
        ),
        opacity=0.5 if perturbed_ric is not None else 1.0,
        hovertemplate="<b>In-track:</b> %{x:.2f} km<br>"
                      "<b>Cross-track:</b> %{y:.2f} km<br>"
                      "<b>Radial:</b> %{z:.2f} km<br>"
                      "<extra>Original</extra>",
    ))
    
    # Maneuvered Trajectory (if any)
    if perturbed_ric is not None:
        PR = perturbed_ric[:, 0]
        PI = perturbed_ric[:, 1]
        PC = perturbed_ric[:, 2]
        p_dist = np.sqrt(PR**2 + PI**2 + PC**2)
        
        fig.add_trace(go.Scatter3d(
            x=PI, y=PC, z=PR,
            mode="lines",
            name="Maneuver Trajectory",
            line=dict(
                color="#00E676", # Green trace for evasive path
                width=5,
                dash='solid'
            ),
            hovertemplate="<b>In-track:</b> %{x:.2f} km<br>"
                          "<b>Cross-track:</b> %{y:.2f} km<br>"
                          "<b>Radial:</b> %{z:.2f} km<br>"
                          "<extra>Post-Maneuver</extra>",
        ))

    # Origin (Primary satellite position)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers+text",
        name=t("chart_3d_primary", lang),
        marker=dict(size=8, color="#00E5FF", symbol="diamond"),
        text=["SAT-1"],
        textfont=dict(color="#00E5FF", size=12),
        textposition="top center",
    ))

    # Closest approach point
    fig.add_trace(go.Scatter3d(
        x=[I[closest_approach_idx]],
        y=[C[closest_approach_idx]],
        z=[R[closest_approach_idx]],
        mode="markers+text",
        name=t("chart_closest_approach", lang),
        marker=dict(
            size=10,
            color="#FF1744",
            symbol="x",
            line=dict(color="white", width=2),
        ),
        text=["TCA"],
        textfont=dict(color="#FF1744", size=12),
        textposition="top center",
    ))

    # Start point
    fig.add_trace(go.Scatter3d(
        x=[I[0]], y=[C[0]], z=[R[0]],
        mode="markers+text",
        name=t("chart_3d_start", lang),
        marker=dict(size=6, color="#00E676", symbol="circle"),
        text=[t("chart_3d_start", lang).upper()],
        textfont=dict(color="#00E676", size=10),
        textposition="bottom center",
    ))

    # End point
    fig.add_trace(go.Scatter3d(
        x=[I[-1]], y=[C[-1]], z=[R[-1]],
        mode="markers+text",
        name=t("chart_3d_end", lang),
        marker=dict(size=6, color="#7C4DFF", symbol="circle"),
        text=[t("chart_3d_end", lang).upper()],
        textfont=dict(color="#7C4DFF", size=10),
        textposition="bottom center",
    ))

    fig.update_layout(
        title=dict(
            text=t("chart_3d_title", lang),
            font=dict(size=18, color="#E0E0E0", family="Inter"),
        ),
        scene=dict(
            xaxis_title=t("chart_3d_intrack", lang),
            yaxis_title=t("chart_3d_crosstrack", lang),
            zaxis_title=t("chart_3d_radial", lang),
            bgcolor="rgba(13, 17, 23, 0.95)",
            xaxis=dict(
                backgroundcolor="rgba(13, 17, 23, 0.8)",
                gridcolor="rgba(255,255,255,0.08)",
                showbackground=True,
                color="#B0BEC5",
            ),
            yaxis=dict(
                backgroundcolor="rgba(13, 17, 23, 0.8)",
                gridcolor="rgba(255,255,255,0.08)",
                showbackground=True,
                color="#B0BEC5",
            ),
            zaxis=dict(
                backgroundcolor="rgba(13, 17, 23, 0.8)",
                gridcolor="rgba(255,255,255,0.08)",
                showbackground=True,
                color="#B0BEC5",
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
            ),
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(13, 17, 23, 0.95)",
        font=dict(family="Inter, sans-serif", color="#B0BEC5"),
        height=600,
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(size=11),
            x=0.02, y=0.98,
        ),
    )

    return fig

def create_3d_earth_view(pos_itrf1, pos_itrf2, sat1_name, sat2_name, closest_idx, lang="en"):
    """
    Graph 4: 3D Earth Orbit (ECEF/ITRF frame).
    Plots paths around an approximate Earth sphere to show geographical context.
    """
    fig = go.Figure()

    # Earth Sphere (approximate)
    R_earth = 6371.0
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = R_earth * np.outer(np.cos(u), np.sin(v))
    y = R_earth * np.outer(np.sin(u), np.sin(v))
    z = R_earth * np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(go.Surface(
        x=x, y=y, z=z,
        colorscale=[[0, '#001E36'], [1, '#00BCD4']],
        showscale=False,
        opacity=0.15,
        name="Earth",
        hoverinfo="skip"
    ))

    # Sat 1 Trajectory
    fig.add_trace(go.Scatter3d(
        x=pos_itrf1[:,0], y=pos_itrf1[:,1], z=pos_itrf1[:,2],
        mode="lines",
        name=sat1_name,
        line=dict(color="#00E5FF", width=3)
    ))

    # Sat 2 Trajectory
    fig.add_trace(go.Scatter3d(
        x=pos_itrf2[:,0], y=pos_itrf2[:,1], z=pos_itrf2[:,2],
        mode="lines",
        name=sat2_name,
        line=dict(color="#B388FF", width=3)
    ))

    # TCA Point
    fig.add_trace(go.Scatter3d(
        x=[pos_itrf1[closest_idx,0]],
        y=[pos_itrf1[closest_idx,1]],
        z=[pos_itrf1[closest_idx,2]],
        mode="markers+text",
        name="TCA",
        marker=dict(size=6, color="#FF1744", symbol="x"),
        text=["TCA"],
        textposition="top center",
        textfont=dict(color="#FF1744", size=14)
    ))
    
    fig.update_layout(
        title=dict(
            text=t("earth_3d_title", lang),
            font=dict(size=18, color="#E0E0E0", family="Inter"),
        ),
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False),
            yaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False),
            zaxis=dict(showbackground=False, showticklabels=False, title="", showgrid=False),
            bgcolor="rgba(13, 17, 23, 0.95)",
            aspectmode='data',
            camera=dict(
                eye=dict(
                    x=1.2 * pos_itrf1[closest_idx,0]/R_earth,
                    y=1.2 * pos_itrf1[closest_idx,1]/R_earth,
                    z=1.2 * pos_itrf1[closest_idx,2]/R_earth
                )
            )
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(13, 17, 23, 0.95)",
        margin=dict(l=0, r=0, t=60, b=0),
        height=500,
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.1)",
            x=0.02, y=0.98
        )
    )
    return fig
