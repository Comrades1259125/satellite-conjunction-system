"""
Scanner Module
Scans a primary satellite against the entire loaded catalog to find top threats.
"""
from core.tle_fetcher import get_available_satellites, get_satellite
from core.orbit_calculator import compute_positions
from core.proximity_analysis import compute_distances
import numpy as np

def run_catalog_scan(primary_name, primary_sat, ts, time_array):
    """
    Scans the primary satellite against the rest of the available catalog over the time array.
    Returns a sorted list of dictionaries with closest approach information.
    """
    catalog = get_available_satellites()
    
    # Pre-compute primary positions
    pos1 = compute_positions(primary_sat, ts, time_array)
    
    threats = []
    
    for sat2_name in catalog:
        if sat2_name == primary_name:
            continue
            
        try:
            sat2 = get_satellite(sat2_name, ts)
            pos2 = compute_positions(sat2, ts, time_array)
            distances = compute_distances(pos1, pos2)
            
            min_idx = np.argmin(distances)
            min_dist = distances[min_idx]
            
            # Save the threat
            threats.append({
                "name": sat2_name,
                "min_distance_km": float(min_dist),
                "tca_idx": int(min_idx),
            })
        except Exception as e:
            # Skip if satellite fails to load
            print(f"Skipping {sat2_name} during scan: {e}")
            continue
            
    # Sort threats by minimum distance ascending
    threats.sort(key=lambda x: x["min_distance_km"])
    return threats
