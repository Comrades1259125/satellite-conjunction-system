"""System validation test script"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from datetime import datetime, timedelta, timezone

from core.proximity_analysis import (
    compute_distances, find_closest_approach, compute_relative_velocity,
    compute_relative_positions, compute_collision_probability,
    compute_collision_probability_over_time, get_risk_level,
    generate_covariance_heatmap_data,
)
from core.orbit_calculator import (
    compute_positions, compute_velocities, generate_time_array,
    compute_orbital_elements,
)
from core.tle_fetcher import (
    get_satellite, get_satellite_from_tle, get_available_satellites,
)
from skyfield.api import load

issues = []

# ═══════════════════════════════════════════
# 1. TLE Fetcher Tests
# ═══════════════════════════════════════════
print("=" * 60)
print("1. TLE FETCHER TESTS")
print("=" * 60)

sats = get_available_satellites()
print(f"Available satellites: {len(sats)}")
for s in sats:
    print(f"  - {s}")

# Check COSMOS 2251 DEB default in app.py
if "COSMOS 2251 DEB" not in sats:
    issues.append("[CRITICAL] 'COSMOS 2251 DEB' is set as default in app.py sidebar but NOT in SATELLITE_CATALOG!")

ts = load.timescale()

# Test loading each satellite from fallback
for name in sats:
    try:
        sat = get_satellite(name, ts)
        print(f"  [OK] Loaded: {name}")
    except Exception as e:
        issues.append(f"[ERROR] Failed to load satellite '{name}': {e}")
        print(f"  [FAIL] {name}: {e}")

# Test manual TLE
try:
    manual_sat = get_satellite_from_tle(
        "TEST-SAT",
        "1 25544U 98067A   24045.54689014  .00024329  00000+0  42556-3 0  9992",
        "2 25544  51.6410 138.2047 0002273 315.2168 162.4950 15.50562470439891",
        ts
    )
    print(f"  [OK] Manual TLE loaded: {manual_sat.name}")
except Exception as e:
    issues.append(f"[ERROR] Manual TLE loading failed: {e}")

# ═══════════════════════════════════════════
# 2. Orbit Calculator Tests
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("2. ORBIT CALCULATOR TESTS")
print("=" * 60)

sat1 = get_satellite("ISS (ZARYA)", ts)

# Test time array
ta, dts = generate_time_array(ts, 24, 1)
expected_steps = 24 * 60 // 1 + 1
print(f"Time array: {len(dts)} steps (expected {expected_steps})")
if len(dts) != expected_steps:
    issues.append(f"[WARNING] Time array has {len(dts)} steps, expected {expected_steps}")

# Test positions
pos1 = compute_positions(sat1, ts, ta)
print(f"Position shape: {pos1.shape}")
if pos1.shape != (len(dts), 3):
    issues.append(f"[ERROR] Position shape mismatch: {pos1.shape} vs expected ({len(dts)}, 3)")

# Verify positions are in reasonable range (Earth orbit)
dist_from_center = np.linalg.norm(pos1, axis=1)
print(f"Distance from Earth center: {dist_from_center.min():.1f} - {dist_from_center.max():.1f} km")
if dist_from_center.min() < 6371:
    issues.append("[CRITICAL] Position below Earth surface!")
if dist_from_center.max() > 50000:
    issues.append("[WARNING] Position unreasonably far from Earth for LEO satellite")

# Test velocities
vel1 = compute_velocities(sat1, ts, ta)
print(f"Velocity shape: {vel1.shape}")
speed = np.linalg.norm(vel1, axis=1)
print(f"Speed range: {speed.min():.4f} - {speed.max():.4f} km/s")
if speed.min() < 5.0 or speed.max() > 12.0:
    issues.append(f"[WARNING] ISS speed outside expected range (5-12 km/s): {speed.min():.4f}-{speed.max():.4f}")

# Test altitudes
alts = compute_orbital_elements(sat1, ts, ta)
print(f"Altitude range: {alts.min():.1f} - {alts.max():.1f} km")
if alts.min() < 0:
    issues.append("[CRITICAL] Negative altitude detected!")
if alts.min() < 300 or alts.max() > 500:
    issues.append(f"[WARNING] ISS altitude outside typical range (300-500 km): {alts.min():.1f}-{alts.max():.1f}")

# Verify coordinate frame documentation is correct (was previously saying ITRF)
print("\n  Checking coordinate frame documentation...")
import inspect
src = inspect.getsource(compute_positions)
if 'ITRF' in src:
    issues.append("[INFO] orbit_calculator.py docstrings still say 'ITRF' but satellite.at() returns GCRS coordinates.")
    print("  [WARN] Docstring still mentions ITRF")
else:
    print("  [OK] Docstring correctly references GCRS")

# ═══════════════════════════════════════════
# 3. Proximity Analysis Tests  
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("3. PROXIMITY ANALYSIS TESTS")
print("=" * 60)

sat2 = get_satellite("NOAA 19", ts)
pos2 = compute_positions(sat2, ts, ta)
vel2 = compute_velocities(sat2, ts, ta)

# Test distances
dists = compute_distances(pos1, pos2)
print(f"Distance range: {dists.min():.1f} - {dists.max():.1f} km")

# Test closest approach
ca = find_closest_approach(dists, dts)
print(f"Closest approach: {ca['distance_km']:.3f} km at index {ca['index']}")
print(f"TCA time: {ca['time']}")

# Verify distance_m is correct
if abs(ca['distance_m'] - ca['distance_km'] * 1000) > 0.001:
    issues.append("[ERROR] distance_m inconsistent with distance_km!")

# Test relative velocity
rv = compute_relative_velocity(vel1, vel2, ca['index'])
print(f"Relative velocity: {rv['magnitude_km_s']:.4f} km/s")
if abs(rv['magnitude_m_s'] - rv['magnitude_km_s'] * 1000) > 0.001:
    issues.append("[ERROR] magnitude_m_s inconsistent with magnitude_km_s!")

# Test RIC frame
ric = compute_relative_positions(pos1, pos2, vel1)
print(f"RIC shape: {ric.shape}")
# Verify RIC distance ≈ Euclidean distance (should be very close)
ric_dist = np.linalg.norm(ric, axis=1)
eucl_dist = dists
max_diff = np.max(np.abs(ric_dist - eucl_dist))
print(f"Max RIC vs Euclidean distance difference: {max_diff:.6f} km")
if max_diff > 0.01:
    issues.append(f"[WARNING] RIC distance differs from Euclidean by {max_diff:.6f} km (should be ~0)")

# Test collision probability
print("\n  Collision Probability Tests:")
pc0 = compute_collision_probability(0.0, 0.1, 0.01)
print(f"  Pc(d=0, sigma=0.1, r=0.01) = {pc0:.6e}")
# At d=0, Pc = r^2 / (2*sigma^2) = 0.01^2 / (2*0.1^2) = 0.0001/0.02 = 0.005
expected_pc0 = 0.01**2 / (2 * 0.1**2)
if abs(pc0 - expected_pc0) > 1e-10:
    issues.append(f"[ERROR] Pc at d=0 wrong: {pc0} vs expected {expected_pc0}")

pc1 = compute_collision_probability(0.001, 0.1, 0.01)
print(f"  Pc(d=0.001, sigma=0.1, r=0.01) = {pc1:.6e}")

# Test risk levels
risk_tests = [
    (0.5, "CRITICAL"),
    (1.99, "CRITICAL"),
    (2.0, "WARNING"),   # boundary
    (5.0, "WARNING"),
    (9.99, "WARNING"),
    (10.0, "SAFE"),     # boundary
    (100.0, "SAFE"),
]
for d, expected in risk_tests:
    name, color, emoji = get_risk_level(d)
    status = "OK" if name == expected else "FAIL"
    if name != expected:
        issues.append(f"[ERROR] Risk level for d={d}: got '{name}', expected '{expected}'")
    print(f"  [{status}] d={d}km -> {name}")

# ═══════════════════════════════════════════
# 4. Heatmap Data Test
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("4. HEATMAP & DATA CONSISTENCY TESTS")
print("=" * 60)

hm, ul, ti = generate_covariance_heatmap_data(dists, dts, 0.1, 0.01)
print(f"Heatmap shape: {hm.shape}")
print(f"Uncertainty range: {ul[0]:.3f} - {ul[-1]:.3f} km")
print(f"Time indices: {len(ti)} points")

# Verify that generate_covariance_heatmap_data accepts combined_radius_km parameter
import inspect
sig = inspect.signature(generate_covariance_heatmap_data)
if 'combined_radius_km' in sig.parameters:
    print("  [OK] generate_covariance_heatmap_data accepts combined_radius_km parameter")
else:
    issues.append("[BUG] generate_covariance_heatmap_data() does not accept combined_radius_km parameter")

# Test collision probability over time
pc_time = compute_collision_probability_over_time(dists, 0.1, 0.01)
print(f"Pc over time: {len(pc_time)} values, max={max(pc_time):.6e}")

# ═══════════════════════════════════════════
# 5. Cross-module Consistency Tests
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("5. CROSS-MODULE CONSISTENCY TESTS")
print("=" * 60)

# Verify unused scipy.stats.norm import has been removed
print("  Checking for unused imports...")
with open('core/proximity_analysis.py', 'r') as f:
    pa_source = f.read()
if 'from scipy.stats import norm' in pa_source:
    issues.append("[MINOR] proximity_analysis.py still imports 'scipy.stats.norm' but never uses it (dead import)")
    print("  [WARN] Unused scipy.stats.norm import still present")
else:
    print("  [OK] No unused scipy.stats.norm import")

# Verify outer duplicate files have been cleaned up
import os
outer_app = os.path.exists('../app.py')
outer_core = os.path.exists('../core')
outer_ui = os.path.exists('../ui')
if outer_app or outer_core or outer_ui:
    issues.append("[WARNING] Duplicate project files still exist in parent directory (../). These should be removed.")
    print(f"  [WARN] Outer duplicates found: app.py={outer_app}, core/={outer_core}, ui/={outer_ui}")
else:
    print("  [OK] No outer duplicate files found")

# ═══════════════════════════════════════════
# 6. App.py Logic Checks
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("6. APP.PY LOGIC CHECKS")
print("=" * 60)

# Verify COSMOS 2251 DEB is now in catalog
if 'COSMOS 2251 DEB' in get_available_satellites():
    print("  [OK] COSMOS 2251 DEB is in catalog")
else:
    issues.append("[CRITICAL] 'COSMOS 2251 DEB' is set as default in app.py but NOT in SATELLITE_CATALOG")
    print("  [FAIL] COSMOS 2251 DEB NOT in catalog")

# Verify progress bar text uses actual satellite names
with open('app.py', 'r', encoding='utf-8') as f:
    app_source = f.read()
if 'Computing SAT-1' in app_source or 'Computing SAT-2' in app_source:
    issues.append("[MINOR] app.py progress bar still uses generic 'SAT-1'/'SAT-2' names instead of actual satellite names")
    print("  [WARN] Progress bar uses generic names")
else:
    print("  [OK] Progress bar uses actual satellite names")

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("ISSUE SUMMARY")
print("=" * 60)

critical = [i for i in issues if i.startswith("[CRITICAL")]
bugs = [i for i in issues if i.startswith("[BUG]")]
errors = [i for i in issues if i.startswith("[ERROR]")]
warnings = [i for i in issues if i.startswith("[WARNING]")]
minor = [i for i in issues if i.startswith("[MINOR]")]
info = [i for i in issues if i.startswith("[INFO]")]

for label, items in [("CRITICAL", critical), ("BUG", bugs), ("ERROR", errors), 
                      ("WARNING", warnings), ("MINOR", minor), ("INFO", info)]:
    if items:
        print(f"\n--- {label} ({len(items)}) ---")
        for i in items:
            print(f"  {i}")

print(f"\nTotal issues found: {len(issues)}")
print(f"  Critical: {len(critical)}, Bugs: {len(bugs)}, Errors: {len(errors)}")
print(f"  Warnings: {len(warnings)}, Minor: {len(minor)}, Info: {len(info)}")
