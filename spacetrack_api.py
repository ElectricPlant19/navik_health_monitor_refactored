"""
Space-Track API module for fetching satellite data
Handles authentication and data retrieval from space-track.org
"""

import requests
import streamlit as st
from config import LOGIN_URL


@st.cache_resource
def get_spacetrack_session(username: str, password: str):
    """Returns a logged-in requests.Session cached as a resource."""
    s = requests.Session()
    resp = s.post(LOGIN_URL, data={'identity': username, 'password': password})
    if resp.status_code != 200:
        raise Exception(f"Space-Track login failed: HTTP {resp.status_code}")
    return s


@st.cache_data(ttl=3600)
def fetch_tle_json_cached(norad_id: int, start_date: str, end_date: str, username: str, password: str):
    """Cached fetch of the GP history JSON."""
    session = get_spacetrack_session(username, password)
    gp_url = (
        f"https://www.space-track.org/basicspacedata/query/class/gp_history/"
        f"EPOCH/{start_date}--{end_date}/NORAD_CAT_ID/{norad_id}/orderby/EPOCH asc/format/json"
    )
    resp = session.get(gp_url)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch GP data for {norad_id}: HTTP {resp.status_code}")
    return resp.json()


@st.cache_data(ttl=3600)
def fetch_multiple_tles(norad_ids, username: str, password: str):
    """Fetch latest TLE data for multiple satellites."""
    session = get_spacetrack_session(username, password)
    ids_str = ','.join(map(str, norad_ids))
    query_url = (
        f"https://www.space-track.org/basicspacedata/query/class/tle_latest/"
        f"NORAD_CAT_ID/{ids_str}/orderby/NORAD_CAT_ID,ORDINAL/format/3le"
    )
    resp = session.get(query_url)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch TLE data: HTTP {resp.status_code}")
    return resp.text


def fetch_and_classify_satellite(norad_id: int, start_date: str, end_date: str,
                                 username: str, password: str, igso_min=10, deviation_tol=0.3):
    """Fetches and classifies satellite data."""
    import pandas as pd
    import numpy as np
    from config import R_EARTH
    
    data = fetch_tle_json_cached(int(norad_id), start_date, end_date, username, password)

    if not data:
        raise ValueError(f"No GP data found for NORAD ID {norad_id} in given range")

    df = pd.DataFrame(data)

    # Standardize column names
    if 'EPOCH' not in df.columns and 'epoch' in df.columns:
        df.rename(columns={'epoch': 'EPOCH'}, inplace=True)
    if 'INCLINATION' not in df.columns and 'inclination' in df.columns:
        df.rename(columns={'inclination': 'INCLINATION'}, inplace=True)
    if 'SEMIMAJOR_AXIS' not in df.columns and 'semimajor_axis' in df.columns:
        df.rename(columns={'semimajor_axis': 'SEMIMAJOR_AXIS'}, inplace=True)
    if 'MEAN_MOTION' not in df.columns and 'mean_motion' in df.columns:
        df.rename(columns={'mean_motion': 'MEAN_MOTION'}, inplace=True)

    if 'EPOCH' not in df.columns or 'INCLINATION' not in df.columns:
        raise ValueError("GP JSON missing required fields 'EPOCH' or 'INCLINATION'")

    required_cols = ['EPOCH', 'INCLINATION']
    if 'SEMIMAJOR_AXIS' in df.columns:
        required_cols.append('SEMIMAJOR_AXIS')
    if 'MEAN_MOTION' in df.columns:
        required_cols.append('MEAN_MOTION')
    
    df = df[required_cols].copy()
    df['EPOCH'] = pd.to_datetime(df['EPOCH'])
    df['INCLINATION'] = df['INCLINATION'].astype(float)
    
    # Calculate longitudinal drift
    if 'MEAN_MOTION' in df.columns:
        df['MEAN_MOTION'] = df['MEAN_MOTION'].astype(float)
        from drift_analysis import calculate_longitudinal_drift
        df['LonDrift_deg_per_day'] = calculate_longitudinal_drift(df['MEAN_MOTION'])

    # Classify satellite type
    df['type'] = df['INCLINATION'].apply(
        lambda x: 'GSO' if (x > 0.0 and x < 10.0) else ('IGSO' if x >= igso_min else 'Unclassified')
    )

    mean_incl = df['INCLINATION'].mean()
    df['mean_inclination'] = mean_incl
    df['maintained'] = df['INCLINATION'].apply(lambda x: abs(x - mean_incl) <= deviation_tol)

    df = df.sort_values('EPOCH').reset_index(drop=True)

    # Calculate altitude
    if 'SEMIMAJOR_AXIS' in df.columns:
        df['SEMIMAJOR_AXIS'] = df['SEMIMAJOR_AXIS'].astype(float)
        df['altitude_km'] = df['SEMIMAJOR_AXIS'] - R_EARTH
    else:
        df['SEMIMAJOR_AXIS'] = np.nan
        df['altitude_km'] = np.nan

    return df
