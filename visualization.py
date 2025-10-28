"""
Visualization Module
Handles all plotting and visualization functions for the NavIC monitoring system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from config import INDIA_EXTREME_POINTS, INACTIVE_SATELLITES
from dop_calculations import calculate_dop_for_location, calculate_bounding_boxes


def plot_individual_satellites(df_all):
    """Plot individual satellite data (inclination, altitude, drift)."""
    st.subheader("Individual Satellite Plots")
    
    for sat_name in sorted(df_all['satellite'].unique()):
        sat_df = df_all[df_all['satellite'] == sat_name].copy()
        
        st.markdown(f"### {sat_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_incl = px.line(
                sat_df,
                x='EPOCH',
                y='INCLINATION',
                markers=True,
                title=f"{sat_name} - Inclination Over Time",
                labels={'EPOCH': 'Epoch', 'INCLINATION': 'Inclination (°)'},
                hover_data=['INCLINATION', 'type']
            )
            fig_incl.update_traces(line_color='#636EFA')
            fig_incl.update_layout(hovermode='x unified', showlegend=False)
            st.plotly_chart(fig_incl, use_container_width=True)
        
        with col2:
            if 'altitude_km' in sat_df.columns and not sat_df['altitude_km'].isna().all():
                fig_alt = px.line(
                    sat_df,
                    x='EPOCH',
                    y='altitude_km',
                    markers=True,
                    title=f"{sat_name} - Altitude Above Surface",
                    labels={'EPOCH': 'Epoch', 'altitude_km': 'Altitude (km)'}
                )
                fig_alt.update_traces(line_color='#EF553B')
                fig_alt.update_layout(hovermode='x unified', showlegend=False)
                st.plotly_chart(fig_alt, use_container_width=True)
            else:
                st.info(f"No altitude data available for {sat_name}")
        
        # Drift plot
        if 'LonDrift_deg_per_day' in sat_df.columns and not sat_df['LonDrift_deg_per_day'].isna().all():
            fig_drift = px.line(
                sat_df,
                x='EPOCH',
                y='LonDrift_deg_per_day',
                markers=True,
                title=f"{sat_name} - Longitudinal Drift Over Time",
                labels={'EPOCH': 'Epoch', 'LonDrift_deg_per_day': 'Drift (°/day)'}
            )
            fig_drift.update_traces(line_color='#00CC96')
            fig_drift.update_layout(hovermode='x unified', showlegend=False)
            
            # Add zero line for reference
            fig_drift.add_hline(y=0, line_dash="dash", line_color="gray", 
                               annotation_text="Zero Drift", annotation_position="right")
            
            st.plotly_chart(fig_drift, use_container_width=True)
        
        st.markdown("---")


def plot_combined_drift(df_all):
    """Plot combined drift comparison for all satellites."""
    if 'LonDrift_deg_per_day' in df_all.columns:
        st.subheader("All Satellites - Drift Comparison")
        fig_all_drift = px.line(
            df_all[df_all['LonDrift_deg_per_day'].notna()],
            x='EPOCH',
            y='LonDrift_deg_per_day',
            color='satellite',
            markers=False,
            title="All NavIC Satellites - Longitudinal Drift Over Time",
            labels={'EPOCH': 'Epoch', 'LonDrift_deg_per_day': 'Drift (°/day)', 'satellite': 'Satellite'}
        )
        fig_all_drift.add_hline(y=0, line_dash="dash", line_color="white", 
                               annotation_text="Zero Drift", annotation_position="right")
        fig_all_drift.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_all_drift, use_container_width=True)


def plot_bounding_boxes(satellites, reference_time, timestep_minutes=15, prop_duration_days=1.5):
    """Plot satellite ground track bounding boxes."""
    st.subheader("🗺️ Satellite Ground Track Bounding Boxes")
    st.caption("Shows the geographic coverage area for each satellite over the next 1.5 days")
    
    with st.spinner("Calculating satellite ground tracks..."):
        bounding_boxes = calculate_bounding_boxes(
            satellites, 
            reference_time, 
            timestep_minutes=timestep_minutes, 
            prop_duration_days=prop_duration_days
        )
        
        if bounding_boxes:
            for sat_name, box_data in bounding_boxes.items():
                st.markdown(f"#### {sat_name} Ground Track")
                
                fig = go.Figure()
                
                fig.add_trace(go.Scattergeo(
                    lon=box_data['longitudes'],
                    lat=box_data['latitudes'],
                    mode='lines+markers',
                    name=sat_name,
                    marker=dict(size=3),
                    line=dict(width=2)
                ))
                
                box_lons = [
                    box_data['min_lon'], box_data['max_lon'], 
                    box_data['max_lon'], box_data['min_lon'], 
                    box_data['min_lon']
                ]
                box_lats = [
                    box_data['min_lat'], box_data['min_lat'], 
                    box_data['max_lat'], box_data['max_lat'], 
                    box_data['min_lat']
                ]
                
                fig.add_trace(go.Scattergeo(
                    lon=box_lons,
                    lat=box_lats,
                    mode='lines',
                    name='Bounding Box',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.add_trace(go.Scattergeo(
                    lon=[box_data['mean_lon']],
                    lat=[box_data['mean_lat']],
                    mode='markers',
                    name='Center',
                    marker=dict(size=10, color='red', symbol='x')
                ))
                
                fig.update_geos(
                    projection_type="natural earth",
                    showland=True,
                    landcolor="lightgray",
                    showocean=True,
                    oceancolor="lightblue",
                    showcountries=True,
                    countrycolor="white",
                    showlakes=True,
                    lakecolor="lightblue",
                    center=dict(lon=box_data['mean_lon'], lat=box_data['mean_lat']),
                    projection_scale=3
                )
                
                fig.update_layout(
                    title=f"{sat_name} - Geographic Coverage (1.5 days)",
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Longitude Range", 
                             f"{box_data['min_lon']:.2f}° to {box_data['max_lon']:.2f}°")
                with col2:
                    st.metric("Latitude Range", 
                             f"{box_data['min_lat']:.2f}° to {box_data['max_lat']:.2f}°")
                with col3:
                    st.metric("Center Position", 
                             f"({box_data['mean_lat']:.2f}°, {box_data['mean_lon']:.2f}°)")
                
                st.markdown("---")
            
            plot_combined_ground_tracks(bounding_boxes)
        else:
            st.warning("No bounding box data available for plotting.")


def plot_combined_ground_tracks(bounding_boxes):
    """Plot combined ground tracks for all satellites."""
    st.markdown("#### All Satellites - Combined Ground Tracks")
    
    fig_combined = go.Figure()
    
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
    
    for idx, (sat_name, box_data) in enumerate(bounding_boxes.items()):
        color = colors[idx % len(colors)]
        
        fig_combined.add_trace(go.Scattergeo(
            lon=box_data['longitudes'],
            lat=box_data['latitudes'],
            mode='lines',
            name=sat_name,
            line=dict(width=2, color=color),
            showlegend=True
        ))
    
    fig_combined.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue",
        showcountries=True,
        countrycolor="white",
        showlakes=True,
        lakecolor="lightblue",
        center=dict(lon=80, lat=20),
        projection_scale=2
    )
    
    fig_combined.update_layout(
        title="All NavIC Satellites - Combined Ground Tracks",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)


def plot_sky_plot(satellites, sat_positions, location_meta, elevation_mask_deg):
    """Plot azimuth-elevation sky plot."""
    st.subheader("🧭 Azimuth–Elevation Sky Plot")
    
    # Prepare polar coordinates: r = 90 - elevation (so zenith at center), theta = azimuth
    az_list = []
    r_list = []
    names = []
    for name, pos in zip([s for s in satellites.keys()], sat_positions):
        if pos is None:
            continue
        if pos['elevation'] > elevation_mask_deg:
            az_list.append(pos['azimuth'])
            r_list.append(max(0, 90 - pos['elevation']))
            names.append(name)
    
    if len(az_list) > 0:
        fig_sky = go.Figure()
        fig_sky.add_trace(go.Scatterpolar(
            r=r_list,
            theta=az_list,
            mode='markers+text',
            text=names,
            textposition='top center',
            marker=dict(size=10)
        ))
        fig_sky.update_layout(
            title=f"Sky Plot at {location_meta['name']} (mask {elevation_mask_deg}°)",
            polar=dict(
                radialaxis=dict(range=[0, 90], tickvals=[0, 30, 60, 90], ticktext=['Zenith', '60°', '30°', 'Horizon']),
                angularaxis=dict(direction='clockwise', rotation=90)
            ),
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_sky, use_container_width=True)
    else:
        st.info("No satellites above the elevation mask for sky plot at this time.")


def plot_dop_over_time(satellites, use_custom_location, custom_lat, custom_lon, 
                      elevation_mask_deg, selected_location=None):
    """Plot DOP values over time."""
    st.subheader("📡 DOP Over Time (30 Days)")
    
    if use_custom_location:
        lat, lon = float(custom_lat), float(custom_lon)
        timeseries_location_name = f"Custom ({lat:.3f}, {lon:.3f})"
    else:
        if selected_location:
            lat, lon = INDIA_EXTREME_POINTS[selected_location]
            timeseries_location_name = selected_location
        else:
            st.warning("Please select a location for DOP time series")
            return
    
    with st.spinner(f"Calculating DOP over time for {timeseries_location_name}..."):
        current_time = datetime.utcnow()
        time_points = []
        gdop_values = []
        pdop_values = []
        hdop_values = []
        vdop_values = []
        visible_sat_counts = []
        
        for hours in range(0, 30*24, 6):
            calc_time = current_time + timedelta(hours=hours)
            dop, visible_sats, _ = calculate_dop_for_location(
                satellites, lat, lon, calc_time, elevation_mask_deg=elevation_mask_deg
            )
            
            time_points.append(calc_time)
            visible_sat_counts.append(len(visible_sats))
            
            if dop:
                gdop_values.append(dop['GDOP'])
                pdop_values.append(dop['PDOP'])
                hdop_values.append(dop['HDOP'])
                vdop_values.append(dop['VDOP'])
            else:
                gdop_values.append(None)
                pdop_values.append(None)
                hdop_values.append(None)
                vdop_values.append(None)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f'DOP Values Over Time - {timeseries_location_name}', 
                          'Visible Satellites Count'),
            vertical_spacing=0.15
        )
        
        fig.add_trace(
            go.Scatter(x=time_points, y=gdop_values, name='GDOP', 
                     line=dict(color='#636EFA')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=pdop_values, name='PDOP', 
                     line=dict(color='#EF553B')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=hdop_values, name='HDOP', 
                     line=dict(color='#00CC96')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=vdop_values, name='VDOP', 
                     line=dict(color='#AB63FA')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=time_points, y=visible_sat_counts, name='Visible Satellites',
                     line=dict(color='#FFA15A'), fill='tozeroy'),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="DOP Value", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        
        fig.update_layout(height=800, showlegend=True, hovermode='x unified')
        
        st.plotly_chart(fig, use_container_width=True)


def plot_combined_inclination(df_all):
    """Plot combined inclination comparison for all satellites."""
    st.subheader("📈 All Satellites - Inclination Comparison")
    fig_all_incl = px.line(
        df_all,
        x='EPOCH',
        y='INCLINATION',
        color='satellite',
        markers=False,
        title="All NavIC Satellites - Inclination Over Time",
        labels={'EPOCH': 'Epoch', 'INCLINATION': 'Inclination (°)', 'satellite': 'Satellite'}
    )
    fig_all_incl.update_layout(hovermode='x unified', height=500)
    st.plotly_chart(fig_all_incl, use_container_width=True)


def plot_combined_altitude(df_all):
    """Plot combined altitude comparison for all satellites."""
    if 'altitude_km' in df_all.columns and not df_all['altitude_km'].isna().all():
        st.subheader("🛰️ All Satellites - Altitude Comparison")
        fig_all_alt = px.line(
            df_all[df_all['altitude_km'].notna()],
            x='EPOCH',
            y='altitude_km',
            color='satellite',
            markers=False,
            title="All NavIC Satellites - Altitude Over Time",
            labels={'EPOCH': 'Epoch', 'altitude_km': 'Altitude (km)', 'satellite': 'Satellite'}
        )
        fig_all_alt.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_all_alt, use_container_width=True)


def plot_drift_distribution(df_all):
    """Plot drift distribution analysis."""
    if 'LonDrift_deg_per_day' in df_all.columns:
        st.subheader("📊 Drift Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram of drift values
            fig_hist = px.histogram(
                df_all[df_all['LonDrift_deg_per_day'].notna()],
                x='LonDrift_deg_per_day',
                color='satellite',
                title="Drift Distribution by Satellite",
                labels={'LonDrift_deg_per_day': 'Drift (°/day)', 'count': 'Frequency'},
                nbins=50,
                marginal="box"
            )
            fig_hist.update_layout(height=500)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot of drift by satellite type
            df_all_with_type = df_all.copy()
            df_all_with_type['sat_type'] = df_all_with_type['INCLINATION'].apply(
                lambda x: 'GSO' if (0.0 < x < 10.0) else ('IGSO' if x >= 10.0 else 'Unclassified')
            )
            
            fig_box = px.box(
                df_all_with_type[df_all_with_type['LonDrift_deg_per_day'].notna()],
                x='sat_type',
                y='LonDrift_deg_per_day',
                color='sat_type',
                title="Drift Distribution by Satellite Type",
                labels={'LonDrift_deg_per_day': 'Drift (°/day)', 'sat_type': 'Satellite Type'}
            )
            fig_box.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_box.update_layout(height=500)
            st.plotly_chart(fig_box, use_container_width=True)


def plot_drift_vs_altitude(df_all):
    """Plot drift vs altitude correlation."""
    if 'LonDrift_deg_per_day' in df_all.columns and 'altitude_km' in df_all.columns:
        st.subheader("🔬 Drift vs Altitude Correlation")
        
        fig_scatter = px.scatter(
            df_all[(df_all['LonDrift_deg_per_day'].notna()) & (df_all['altitude_km'].notna())],
            x='altitude_km',
            y='LonDrift_deg_per_day',
            color='satellite',
            title="Longitudinal Drift vs Altitude",
            labels={'altitude_km': 'Altitude (km)', 'LonDrift_deg_per_day': 'Drift (°/day)'},
            hover_data=['EPOCH', 'INCLINATION']
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray", 
                             annotation_text="Zero Drift", annotation_position="right")
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
