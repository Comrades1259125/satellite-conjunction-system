"""
TLE Fetcher Module
Fetches Two-Line Element (TLE) data for satellites from CelesTrak.
"""

import requests
from skyfield.api import EarthSatellite, load

# Pre-defined satellite catalog with NORAD IDs and TLE names
SATELLITE_CATALOG = {
    "ISS (ZARYA)": 25544,
    "FENGYUN 1C DEB": 29479,
    "COSMOS 2251 DEB": 34454,
    "IRIDIUM 33 DEB": 33776,
    "STARLINK-1008": 44714,
    "NOAA 19": 33591,
    "TERRA": 25994,
    "AQUA": 27424,
    "HUBBLE SPACE TELESCOPE": 20580,
    "TIANGONG": 48274,
    "CZ-6A DEB": 54236,
}

# Fallback TLE data for common satellites (in case API is unavailable)
FALLBACK_TLE = {
    "ISS (ZARYA)": (
        "1 25544U 98067A   26097.81163521  .00007114  00000+0  13797-3 0  9993",
        "2 25544  51.6331 288.3735 0006339 285.1531  74.8756 15.48821670560845"
    ),
    "FENGYUN 1C DEB": (
        "1 29479U 06041A   26097.46200666  .00000740  00000+0  13580-3 0  9996",
        "2 29479  98.0601 114.6479 0018263 148.6460 211.5838 14.68523991 44495"
    ),
    "COSMOS 2251 DEB": (
        "1 34454U 93036PG  26097.52714437  .00000714  00000+0  21573-3 0  9992",
        "2 34454  74.0206 281.0443 0040012 150.2271 210.1239 14.35813247607381"
    ),
    "IRIDIUM 33 DEB": (
        "1 33776U 97051P   26097.77619603  .00000913  00000+0  29236-3 0  9998",
        "2 33776  86.4072  32.0118 0014456 168.0895 255.7112 14.38459921897505"
    ),
    "STARLINK-1008": (
        "1 44714U 19074B   26097.14472000  .00093530  00000+0  27708-2 0  9998",
        "2 44714  53.1559  46.1506 0003232 126.1394 233.9908 15.34101796353235"
    ),
    "NOAA 19": (
        "1 33591U 09005A   26097.89988056  .00000041  00000+0  45897-4 0  9993",
        "2 33591  98.9556 168.7125 0013044 225.8437 134.1663 14.13462778884555"
    ),
    "TERRA": (
        "1 25994U 99068A   26097.91170093  .00000433  00000+0  97225-4 0  9993",
        "2 25994  97.9533 150.2211 0003661  91.9079  82.3618 14.61047862399345"
    ),
    "AQUA": (
        "1 27424U 02022A   26097.90746961  .00001013  00000+0  21172-3 0  9991",
        "2 27424  98.4223  65.8158 0001533 113.3237 304.1730 14.62048321273005"
    ),
    "HUBBLE SPACE TELESCOPE": (
        "1 20580U 90037B   26097.64834574  .00007506  00000+0  24354-3 0  9997",
        "2 20580  28.4726 202.3847 0002355  89.2178 270.8688 15.29974059777755"
    ),
    "TIANGONG": (
        "1 48274U 21035A   26097.94592976  .00023763  00000+0  26651-3 0  9994",
        "2 48274  41.4681  29.9517 0004108 155.7123 204.3911 15.62089242282181"
    ),
    "CZ-6A DEB": (
        "1 54236U 22151B   26097.90960432  .00000006  00000+0  28245-4 0  9998",
        "2 54236  98.8521 100.1393 0045327 179.9905 180.1274 14.09292143174744"
    )
}


def fetch_tle_from_celestrak(norad_id: int) -> tuple:
    """
    Fetch TLE from CelesTrak API by NORAD ID.
    Returns (name, line1, line2) or None if failed.
    """
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            if len(lines) >= 3:
                name = lines[0].strip()
                line1 = lines[1].strip()
                line2 = lines[2].strip()
                return (name, line1, line2)
    except Exception:
        pass
    return None


def get_satellite(name: str, ts=None) -> EarthSatellite:
    """
    Get an EarthSatellite object by satellite name.
    Tries CelesTrak first, falls back to built-in data.
    """
    if ts is None:
        ts = load.timescale()

    # Try fetching from CelesTrak
    if name in SATELLITE_CATALOG:
        norad_id = SATELLITE_CATALOG[name]
        result = fetch_tle_from_celestrak(norad_id)
        if result:
            _, line1, line2 = result
            return EarthSatellite(line1, line2, name, ts)

    # Fallback to built-in TLE
    if name in FALLBACK_TLE:
        line1, line2 = FALLBACK_TLE[name]
        return EarthSatellite(line1, line2, name, ts)

    raise ValueError(f"Satellite '{name}' not found in catalog or fallback TLE data.")


def get_satellite_from_tle(name: str, line1: str, line2: str, ts=None) -> EarthSatellite:
    """
    Create an EarthSatellite from user-provided TLE lines.
    """
    if ts is None:
        ts = load.timescale()
    return EarthSatellite(line1.strip(), line2.strip(), name.strip(), ts)


def get_available_satellites() -> list:
    """Return list of available satellite names."""
    return list(SATELLITE_CATALOG.keys())
