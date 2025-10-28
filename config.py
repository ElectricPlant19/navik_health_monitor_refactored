"""
Configuration file for NavIC Comprehensive Monitoring System
Contains all constants, satellite data, and configuration parameters
"""

# Constants
MU = 398600.4418  # km^3/s^2
R_EARTH = 6371.0  # km
GEOSYNC_MEAN_MOTION = 1.002737909  # revolutions/day for perfect geostationary orbit

# NavIC Satellite NORAD IDs
NAVIK_SATS = {
    "IRNSS-1B": 39635,
    "IRNSS-1C": 40269,
    "IRNSS-1D": 40547,
    "IRNSS-1E": 41241,
    "IRNSS-1F": 41384,
    "IRNSS-1I": 43286,
    "NVS-01": 56759
}

# India's extreme geographical points for DOP analysis
INDIA_EXTREME_POINTS = {
    "Northernmost (Siachen Glacier)": (35.5, 77.0),
    "Southernmost (Indira Point)": (6.75, 93.85),
    "Easternmost (Kibithu)": (28.0, 97.0),
    "Westernmost (Guhar Moti)": (23.7, 68.1),
    "Capital (Delhi)": (28.7, 77.1)
}

# NavIC service requirements (target longitudes and inclinations)
NAVIK_SERVICE_REQUIREMENTS = {
    "IRNSS-1B": {"longitude": 55.0, "inclination": 29.0},
    "IRNSS-1C": {"longitude": 83.0, "inclination": 5.0},
    "IRNSS-1D": {"longitude": 111.75, "inclination": 30.0},
    "IRNSS-1E": {"longitude": 111.75, "inclination": 29.0},
    "IRNSS-1F": {"longitude": 32.5, "inclination": 5.0},
    "IRNSS-1I": {"longitude": 55.0, "inclination": 29.0},
    "NVS-01": {"longitude": 129.5, "inclination": 5.0}
}

# Space-Track API configuration
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"

# Inactive satellites (for DOP calculations)
INACTIVE_SATELLITES = ["IRNSS-1B", "IRNSS-1C", "IRNSS-1D"]

# Default analysis parameters
DEFAULT_PARAMS = {
    "z_threshold": 3.5,
    "sma_threshold": 0.5,
    "inc_threshold": 0.01,
    "persist_window": 2,
    "inclination_tolerance": 1.0,
    "drift_tolerance_gso": 0.05,
    "min_maneuvers_per_month": 1,
    "max_maneuvers_per_month": 8,
    "maneuver_uniformity_threshold": 0.8,
    "elevation_mask_deg": 5,
    "timestep_minutes": 15,
    "prop_duration_days": 1.5
}

# DOP quality thresholds
DOP_QUALITY_THRESHOLDS = {
    "Excellent": 2,
    "Good": 4,
    "Moderate": 6,
    "Fair": 8,
    "Poor": float('inf')
}
