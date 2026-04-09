"""
Proximity Analysis Module
Computes distances, closest approach, relative velocity, and collision probability.
"""

import numpy as np


def compute_distances(positions_1, positions_2):
    """
    Compute Euclidean distance between two satellite position arrays.

    Args:
        positions_1: numpy array of shape (N, 3) in km
        positions_2: numpy array of shape (N, 3) in km

    Returns:
        distances: numpy array of shape (N,) in km
    """
    diff = positions_1 - positions_2
    distances = np.sqrt(np.sum(diff ** 2, axis=1))
    return distances


def find_closest_approach(distances, datetimes):
    """
    Find the time and distance of closest approach.

    Args:
        distances: numpy array of distances in km
        datetimes: list of datetime objects

    Returns:
        dict with 'time', 'distance_km', 'distance_m', 'index'
    """
    min_idx = np.argmin(distances)
    min_distance_km = distances[min_idx]
    min_distance_m = min_distance_km * 1000.0

    return {
        "time": datetimes[min_idx],
        "distance_km": float(min_distance_km),
        "distance_m": float(min_distance_m),
        "index": int(min_idx),
    }


def compute_relative_velocity(velocities_1, velocities_2, index):
    """
    Compute relative velocity at a specific time index.

    Args:
        velocities_1: numpy array (N, 3) in km/s
        velocities_2: numpy array (N, 3) in km/s
        index: time step index

    Returns:
        dict with 'vector' (3,), 'magnitude_km_s', 'magnitude_m_s'
    """
    rel_vel = velocities_2[index] - velocities_1[index]
    magnitude = np.linalg.norm(rel_vel)

    return {
        "vector": rel_vel,
        "magnitude_km_s": float(magnitude),
        "magnitude_m_s": float(magnitude * 1000.0),
    }


def compute_relative_positions(positions_1, positions_2, velocities_1):
    """
    Compute relative positions of satellite 2 as seen from satellite 1
    in the RIC (Radial, In-track, Cross-track) frame.

    Args:
        positions_1: numpy array (N, 3) primary satellite positions
        positions_2: numpy array (N, 3) secondary satellite positions
        velocities_1: numpy array (N, 3) primary satellite velocities

    Returns:
        relative_ric: numpy array (N, 3) relative positions in RIC frame
    """
    N = positions_1.shape[0]
    relative_ric = np.zeros((N, 3))

    for i in range(N):
        r1 = positions_1[i]
        v1 = velocities_1[i]

        # RIC frame unit vectors
        r_hat = r1 / np.linalg.norm(r1)  # Radial
        h = np.cross(r1, v1)  # Angular momentum
        c_hat = h / np.linalg.norm(h)  # Cross-track
        i_hat = np.cross(c_hat, r_hat)  # In-track

        # Relative position in ECI
        delta_r = positions_2[i] - positions_1[i]

        # Project onto RIC
        relative_ric[i, 0] = np.dot(delta_r, r_hat)  # Radial
        relative_ric[i, 1] = np.dot(delta_r, i_hat)  # In-track
        relative_ric[i, 2] = np.dot(delta_r, c_hat)  # Cross-track

    return relative_ric

def apply_cw_maneuver(relative_ric, time_array_seconds, primary_positions, primary_velocities, dv_radial_ms=0, dv_intrack_ms=0, dv_crosstrack_ms=0):
    """
    Apply Clohessy-Wiltshire equations to propagate a maneuver in the RIC frame.
    
    Args:
        relative_ric: Unperturbed relative trajectory in RIC frame (N, 3) in km
        time_array_seconds: Array of elapsed time from maneuver epoch in seconds (N,)
        primary_positions: Primary sat positions (N, 3) in km
        primary_velocities: Primary sat velocities (N, 3) in km/s
        dv_radial_ms: Delta-V applied in Radial direction (m/s)
        dv_intrack_ms: Delta-V applied in In-track direction (m/s)
        dv_crosstrack_ms: Delta-V applied in Cross-track direction (m/s)
        
    Returns:
        perturbed_ric: New relative trajectory (N, 3) in km
    """
    if dv_radial_ms == 0 and dv_intrack_ms == 0 and dv_crosstrack_ms == 0:
        return relative_ric
        
    # Convert m/s to km/s
    dv_x = dv_radial_ms / 1000.0
    dv_y = dv_intrack_ms / 1000.0
    dv_z = dv_crosstrack_ms / 1000.0
    
    # Calculate Mean Motion (n) using initial state ||V|| / ||R|| for near-circular orbits
    r0 = np.linalg.norm(primary_positions[0])
    v0 = np.linalg.norm(primary_velocities[0])
    n = v0 / r0  # radians / sec
    
    perturbed_ric = np.copy(relative_ric)
    
    t = time_array_seconds
    nt = n * t
    sin_nt = np.sin(nt)
    cos_nt = np.cos(nt)
    
    # CW Equations for position change given initial velocity change
    dx = (dv_x / n) * sin_nt - (2 * dv_y / n) * (1 - cos_nt)
    dy = (2 * dv_x / n) * (1 - cos_nt) + (dv_y / n) * (4 * sin_nt - 3 * nt)
    dz = (dv_z / n) * sin_nt
    
    # Add deviations to the original unperturbed trajectory
    perturbed_ric[:, 0] += dx
    perturbed_ric[:, 1] += dy
    perturbed_ric[:, 2] += dz
    
    return perturbed_ric


def compute_collision_probability(
    distance_km,
    position_uncertainty_km=0.1,
    combined_radius_km=0.01,
):
    """
    Compute simplified collision probability using a 2D encounter model.
    
    This uses the Alfano/Chan approximation where the probability is
    modeled as a 2D Gaussian distribution in the encounter plane.

    Args:
        distance_km: miss distance in km
        position_uncertainty_km: combined 1-sigma position uncertainty (km)
        combined_radius_km: combined hard-body radius of both objects (km)

    Returns:
        probability: collision probability (0 to 1)
    """
    if position_uncertainty_km <= 0:
        return 0.0

    sigma = position_uncertainty_km
    r = combined_radius_km

    # Simplified 2D circular Gaussian model
    # Pc = (r^2 / (2 * sigma^2)) * exp(-d^2 / (2 * sigma^2))
    d = distance_km
    exponent = -(d ** 2) / (2 * sigma ** 2)
    pc = (r ** 2 / (2 * sigma ** 2)) * np.exp(exponent)

    return float(min(pc, 1.0))


def compute_collision_probability_over_time(
    distances,
    position_uncertainty_km=0.1,
    combined_radius_km=0.01,
):
    """
    Compute collision probability at each time step.

    Args:
        distances: numpy array of distances in km
        position_uncertainty_km: combined 1-sigma position uncertainty (km)
        combined_radius_km: combined hard-body radius (km)

    Returns:
        probabilities: numpy array of probabilities
    """
    probabilities = np.array([
        compute_collision_probability(d, position_uncertainty_km, combined_radius_km)
        for d in distances
    ])
    return probabilities


def get_risk_level(distance_km):
    """
    Determine risk level based on distance.

    Returns:
        tuple: (level_name, color, emoji)
    """
    if distance_km < 2.0:
        return ("CRITICAL", "#FF1744", "🔴")
    elif distance_km < 10.0:
        return ("WARNING", "#FFC107", "🟡")
    else:
        return ("SAFE", "#00E676", "🟢")


def generate_covariance_heatmap_data(
    distances,
    datetimes,
    base_uncertainty_km=0.1,
    combined_radius_km=0.01,
    uncertainty_growth_rate=0.001,
):
    """
    Generate data for collision probability heatmap.
    Models how collision probability changes with both time and
    varying position uncertainty (covariance growth).

    Args:
        distances: numpy array of distances
        datetimes: list of datetimes
        base_uncertainty_km: initial position uncertainty
        uncertainty_growth_rate: rate of uncertainty growth per minute

    Returns:
        heatmap_data: 2D numpy array (uncertainty_levels x time_steps)
        uncertainty_levels: numpy array of uncertainty values
        time_indices: indices into original time array (subsampled)
    """
    # Subsample time (every 10 steps) for reasonable heatmap size
    step = max(1, len(distances) // 144)
    time_indices = np.arange(0, len(distances), step)
    sub_distances = distances[time_indices]

    # Create range of uncertainty values
    uncertainty_levels = np.linspace(
        base_uncertainty_km * 0.5,
        base_uncertainty_km * 5.0,
        50,
    )

    heatmap_data = np.zeros((len(uncertainty_levels), len(time_indices)))

    for i, sigma in enumerate(uncertainty_levels):
        for j, d in enumerate(sub_distances):
            heatmap_data[i, j] = compute_collision_probability(
                d, sigma, combined_radius_km=combined_radius_km
            )

    return heatmap_data, uncertainty_levels, time_indices
