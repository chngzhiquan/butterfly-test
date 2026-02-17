import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
import os
import json
from datetime import time
from dotenv import load_dotenv
from arcgis.gis import GIS
from arcgis.features import FeatureLayer

# 1. APP CONFIGURATION
st.set_page_config(
    page_title="Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DATA LOADING & PROCESSING
@st.cache_data(ttl=3600)
def load_data():
    """
    Connects to ArcGIS Online, fetches the layer, and cleans the data.
    """
    # A. Load Credentials (Local .env or Cloud Secrets)
    load_dotenv()
    user = os.getenv("ARCGIS_USER") or st.secrets.get("ARCGIS_USER")
    pwd = os.getenv("ARCGIS_PASS") or st.secrets.get("ARCGIS_PASS")
    url = os.getenv("ARCGIS_LAYER_URL") or st.secrets.get("ARCGIS_LAYER_URL")

    if not url:
        st.error("❌ API URL missing. Please set ARCGIS_LAYER_URL in .env or secrets.")
        st.stop()

    try:
        # B. Connect to ArcGIS (Login if credentials exist, else try anonymous)
        if user and pwd:
            gis = GIS("https://www.arcgis.com", user, pwd)
        else:
            gis = GIS() # Anonymous access if layer is public

        layer = FeatureLayer(url)
        
        # C. Query Data (Fetch all rows)
        query_result = layer.query(where="1=1", out_fields="*", return_geometry=True)
        sdf = query_result.sdf  # Convert to Spatially Enabled DataFrame
        
        # --- DATA CLEANING ---
        
        # 1. Extract Lat/Lon from ArcGIS 'SHAPE' object
        if 'SHAPE' in sdf.columns:
            sdf['latitude'] = sdf['SHAPE'].apply(lambda x: x.y)
            sdf['longitude'] = sdf['SHAPE'].apply(lambda x: x.x)
        
        # 2. Clean 'Count_' (Fill NaNs with 1 for single sightings)
        if 'Count_' in sdf.columns:
            sdf['Count_'] = sdf['Count_'].fillna(1).astype(int)
        else:
            sdf['Count_'] = 1 # Fallback if column is missing

        # 3. Clean 'Start_Time' (Extract Hour for slider)
        # Handles various ArcGIS time formats
        if 'Start_Time' in sdf.columns:
            # Try converting to datetime; errors='coerce' turns bad data into NaT
            sdf['dt_temp'] = pd.to_datetime(sdf['Start_Time'], errors='coerce')
            sdf['hour'] = sdf['dt_temp'].dt.hour.fillna(12).astype(int) # Default to noon if null
        else:
            sdf['hour'] = 12

        # 4. Handle Missing Species/Parks
        sdf['Species'] = sdf['Species'].fillna('Unknown')
        sdf['Park'] = sdf['Park'].fillna('Unknown')

        return sdf

    except Exception as e:
        st.error(f"⚠️ Error connecting to ArcGIS: {e}")
        st.stop()

# Load the data
with st.spinner('🔄 Fetching live data from ArcGIS Cloud...'):
    df = load_data()


# 3. SIDEBAR FILTERS
st.sidebar.header("🔍 Filter Controls")

# A. Year Filter
all_years = sorted(df['Year'].dropna().unique())
selected_years = st.sidebar.multiselect("Select Year", all_years, default=all_years)

# B. Month Filter
all_months = sorted(df['Month'].dropna().unique())
selected_months = st.sidebar.multiselect("Select Month", all_months, default=all_months)

# C. Species Filter
all_species = sorted(df['Species'].unique())
selected_species = st.sidebar.multiselect("Select Species", all_species, default=all_species[:5])

# D. Time of Day Filter
min_h, max_h = int(df['hour'].min()), int(df['hour'].max())
if min_h == max_h: max_h += 1 # Prevent slider error if only 1 hour exists
time_range = st.sidebar.slider("Time of Day (24h)", min_h, max_h, (min_h, max_h))

# E. Map Style ( moved to sidebar for cleanliness)
st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Map Settings")
map_style = st.sidebar.radio("Layer Type", ["Scatter (Points)", "Heatmap (Density)"])

# --- APPLY FILTERS ---
mask = (
    (df['Year'].isin(selected_years)) &
    (df['Month'].isin(selected_months)) &
    (df['Species'].isin(selected_species)) &
    (df['hour'] >= time_range[0]) &
    (df['hour'] <= time_range[1])
)
filtered_df = df[mask]


# 4. MAIN DASHBOARD UI
st.title("🌿 Biodiversity Explorer")
st.markdown(f"**Live Analysis of {len(filtered_df)} Sightings**")

# --- ROW 1: METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sightings", f"{len(filtered_df):,}")
col2.metric("Total Individuals", f"{filtered_df['Count_'].sum():,}")
# Logic to find top species/park safely
top_s = filtered_df['Species'].mode()[0] if not filtered_df.empty else "N/A"
top_p = filtered_df['Park'].mode()[0] if not filtered_df.empty else "N/A"
col3.metric("Most Common Species", top_s)
col4.metric("Top Hotspot", top_p)

st.divider()

# --- ROW 2: THE INTERACTIVE MAP ---
c1, c2 = st.columns([3, 1]) # Map takes 75% width

with c1:
    st.subheader("📍 Spatial Distribution")
    
    # Define View State (Singapore)
    view_state = pdk.ViewState(
        latitude=1.3521, 
        longitude=103.8198, 
        zoom=10.5, 
        pitch=50 if map_style == "Heatmap (Density)" else 0
    )

    layers = []

    # Add Park Boundaries (To include file)
    if os.path.exists("parks.geojson"):
        with open("parks.geojson") as f:
            geojson_data = json.load(f)
        
        park_layer = pdk.Layer(
            "GeoJsonLayer",
            geojson_data,
            opacity=0.3,
            stroked=True,
            filled=True,
            wireframe=True,
            get_fill_color=[0, 255, 0, 50],
            get_line_color=[0, 100, 0],
            get_line_width=20
        )
        layers.append(park_layer)

    # DATA LAYERS
    if map_style == "Scatter (Points)":
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]', # Reddish dots
            get_radius=30,
            pickable=True
        )
        layers.append(layer)
        tooltip = {"html": "<b>{Species}</b><br/>Count: {Count_}<br/>Park: {Park}"}

    else: # Heatmap
        layer = pdk.Layer(
            "HeatmapLayer",
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_weight="Count_", # Critical: Weights by number of birds seen
            radiusPixels=40,
            intensity=1,
            threshold=0.05
        )
        layers.append(layer)
        tooltip = None

    # Render Map
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=layers,
        tooltip=tooltip
    ))

with c2:
    st.subheader("📊 Top 5 Species")
    # Bar Chart: Sum of 'Count_' by Species
    if not filtered_df.empty:
        chart_data = filtered_df.groupby('Species')['Count_'].sum().nlargest(5).reset_index()
        
        chart = alt.Chart(chart_data).mark_bar(color='#2E8B57').encode(
            x=alt.X('Count_', title='Individuals'),
            y=alt.Y('Species', sort='-x', title=None),
            tooltip=['Species', 'Count_']
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No data.")

# --- ROW 3: PARK AGGREGATION ---
st.divider()
st.subheader("🌳 Park Analysis")

if not filtered_df.empty:
    # Aggregation: Total count per park
    park_data = filtered_df.groupby('Park')['Count_'].sum().nlargest(10).reset_index()
    
    park_chart = alt.Chart(park_data).mark_bar().encode(
        x=alt.X('Park', sort='-y', title=None),
        y=alt.Y('Count_', title='Total Count'),
        color=alt.Color('Park', legend=None),
        tooltip=['Park', 'Count_']
    ).properties(height=300)
    
    st.altair_chart(park_chart, use_container_width=True)

# --- EXPANDER FOR RAW DATA ---
with st.expander("📂 View Raw Data Table"):
    st.dataframe(filtered_df[['Species', 'Count_', 'Park', 'Year', 'Month', 'Start_Time', 'latitude', 'longitude']])