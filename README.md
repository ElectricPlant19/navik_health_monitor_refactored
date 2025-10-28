# NavIC Comprehensive Monitoring System - Modular Architecture

This project has been refactored from a monolithic structure into a clean, modular architecture for better maintainability and readability.

## 📁 Project Structure

```
HEALTH/
├── main_app.py              # Main Streamlit application
├── config.py                # Configuration and constants
├── spacetrack_api.py        # Space-Track API integration
├── drift_analysis.py        # Longitudinal drift calculations
├── maneuver_detection.py    # Orbital maneuver detection
├── health_assessment.py     # Comprehensive health scoring
├── dop_calculations.py      # DOP calculations and satellite positioning
├── visualization.py         # All plotting and visualization functions
└── README.md               # This documentation
```

## 🔧 Module Descriptions

### `config.py`
- **Purpose**: Centralized configuration and constants
- **Contains**: 
  - NavIC satellite NORAD IDs
  - India's geographical points for DOP analysis
  - Service requirements and tolerances
  - Default analysis parameters
  - DOP quality thresholds

### `spacetrack_api.py`
- **Purpose**: Space-Track.org API integration
- **Functions**:
  - `get_spacetrack_session()`: Authentication
  - `fetch_tle_json_cached()`: Cached GP history data
  - `fetch_multiple_tles()`: Latest TLE data
  - `fetch_and_classify_satellite()`: Complete satellite data processing

### `drift_analysis.py`
- **Purpose**: Longitudinal drift calculations and assessment
- **Functions**:
  - `calculate_longitudinal_drift()`: Convert mean motion to drift
  - `assess_drift_health()`: Health assessment based on drift
  - `calculate_drift_trend()`: Analyze drift trends over time
  - `get_drift_direction()`: Determine drift direction with emojis

### `maneuver_detection.py`
- **Purpose**: Statistical detection of orbital maneuvers
- **Functions**:
  - `detect_navik_maneuvers()`: Main maneuver detection algorithm
  - `rolling_median_safe()`: Robust rolling median calculation
  - `mad_zscore()`: Median Absolute Deviation z-score
  - `calculate_maneuver_uniformity()`: Maneuver spacing analysis

### `health_assessment.py`
- **Purpose**: Comprehensive satellite health scoring
- **Functions**:
  - `assess_satellite_health_with_drift()`: Complete health assessment including drift analysis
  - Integrates inclination control, maintenance activity, maneuver uniformity, and drift analysis

### `dop_calculations.py`
- **Purpose**: Dilution of Precision calculations and satellite positioning
- **Functions**:
  - `parse_tle_data()`: Parse TLE text into satellite objects
  - `calculate_satellite_position()`: Calculate satellite positions
  - `calculate_dop_for_location()`: DOP calculations for specific locations
  - `calculate_bounding_boxes()`: Ground track bounding box calculations
  - `get_dop_quality()`: DOP quality assessment

### `visualization.py`
- **Purpose**: All plotting and visualization functions
- **Functions**:
  - `plot_individual_satellites()`: Individual satellite plots
  - `plot_combined_drift()`: Combined drift comparison
  - `plot_bounding_boxes()`: Ground track visualizations
  - `plot_sky_plot()`: Azimuth-elevation sky plots
  - `plot_dop_over_time()`: DOP time series plots
  - `plot_drift_distribution()`: Drift distribution analysis
  - And more specialized plotting functions

### `main_app.py`
- **Purpose**: Main Streamlit application
- **Features**:
  - User interface and sidebar configuration
  - Data fetching and processing orchestration
  - Results display and visualization coordination
  - Session state management

## 🚀 Usage

### Running the Application
```bash
streamlit run main_app.py
```

### Key Features
- **Modular Design**: Each module has a specific responsibility
- **Easy Maintenance**: Changes to one module don't affect others
- **Clear Dependencies**: Well-defined interfaces between modules
- **Reusable Components**: Functions can be imported and used independently
- **Comprehensive Documentation**: Each module is well-documented

## 🔄 Migration from Monolithic Structure

The original `v4.py` file (1612 lines) has been split into:

1. **Configuration** → `config.py` (80 lines)
2. **API Integration** → `spacetrack_api.py` (120 lines)
3. **Drift Analysis** → `drift_analysis.py` (100 lines)
4. **Maneuver Detection** → `maneuver_detection.py` (150 lines)
5. **Health Assessment** → `health_assessment.py` (200 lines)
6. **DOP Calculations** → `dop_calculations.py` (180 lines)
7. **Visualization** → `visualization.py` (400 lines)
8. **Main Application** → `main_app.py` (500 lines)

**Total**: ~1730 lines across 8 focused modules vs. 1612 lines in 1 monolithic file

## 🎯 Benefits of Modular Architecture

1. **Maintainability**: Easier to locate and fix issues
2. **Readability**: Each module has a clear, focused purpose
3. **Testability**: Individual modules can be tested independently
4. **Reusability**: Functions can be imported and used in other projects
5. **Collaboration**: Multiple developers can work on different modules
6. **Documentation**: Each module is self-documenting
7. **Debugging**: Easier to isolate and debug specific functionality

## 📋 Dependencies

All modules maintain the same dependencies as the original:
- `streamlit`
- `numpy`
- `pandas`
- `plotly`
- `requests`
- `skyfield`
- `statistics`

## 🔧 Customization

Each module can be customized independently:
- **Configuration**: Modify `config.py` for different satellites or parameters
- **Analysis**: Adjust algorithms in respective analysis modules
- **Visualization**: Customize plots in `visualization.py`
- **UI**: Modify the main application interface in `main_app.py`

This modular structure makes the NavIC monitoring system much more robust, readable, and maintainable while preserving all original functionality.
