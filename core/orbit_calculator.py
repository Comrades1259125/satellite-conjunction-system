"""
Orbit Calculator Module
Computes satellite positions (ITRF x, y, z) over a time span.
"""

import numpy as np
from skyfield.api import load
from datetime import datetime, timedelta, timezone


def compute_positions(satellite, ts, time_array):
    """
    Compute ITRF (x, y, z) positions for a satellite over a time array.

    Args:
        satellite: EarthSatellite object
        ts: Skyfield timescale
        time_array: Skyfield Time array

    Returns:
        positions: numpy array of shape (N, 3) in km
    """
    geocentric = satellite.at(time_array)
    # Get ITRF position in km
    pos = geocentric.position.km  # shape (3, N)
    return pos.T  # shape (N, 3)


def compute_velocities(satellite, ts, time_array):
    """
    Compute ITRF velocities for a satellite over a time array.

    Args:
        satellite: EarthSatellite object
        ts: Skyfield timescale
        time_array: Skyfield Time array

    Returns:
        velocities: numpy array of shape (N, 3) in km/s
    """
    geocentric = satellite.at(time_array)
    vel = geocentric.velocity.km_per_s  # shape (3, N)
    return vel.T  # shape (N, 3)


def generate_time_array(ts, duration_hours=24, step_minutes=1):
    """
    Generate a time array from now for the specified duration.

    Args:
        ts: Skyfield timescale
        duration_hours: Duration in hours (default 24)
        step_minutes: Time step in minutes (default 1)

    Returns:
        time_array: Skyfield Time array
        datetimes: List of Python datetime objects (UTC)
    """
    now = datetime.now(timezone.utc)
    total_minutes = int(duration_hours * 60)
    num_steps = total_minutes // step_minutes + 1

    datetimes = [now + timedelta(minutes=i * step_minutes) for i in range(num_steps)]

    # Convert to Skyfield time
    years = [dt.year for dt in datetimes]
    months = [dt.month for dt in datetimes]
    days = [dt.day for dt in datetimes]
    hours = [dt.hour for dt in datetimes]
    minutes = [dt.minute for dt in datetimes]
    seconds = [dt.second + dt.microsecond / 1e6 for dt in datetimes]

    time_array = ts.utc(years, months, days, hours, minutes, seconds)
    return time_array, datetimes


def compute_orbital_elements(satellite, ts, time_array):
    """
    Compute basic orbital parameters at each time step.
    Returns altitude (km above Earth surface) for each step.
    """
    geocentric = satellite.at(time_array)
    pos = geocentric.position.km  # shape (3, N)
    earth_radius = 6371.0  # km

    # Distance from Earth center
    distances = np.sqrt(pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2)
    altitudes = distances - earth_radius

    return altitudes
