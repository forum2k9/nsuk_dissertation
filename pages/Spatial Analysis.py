import streamlit as st
import pandas as pd
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
import geopandas as gpd
from sqlalchemy import create_engine
import json

st.set_page_config(layout="wide")
st.markdown("### 🗺️ Exploratory Spatial Data Analysis of Campus Facilities")

# 1. Provide a file uploader or fallback to a local file path
uploaded_file = st.sidebar.file_uploader("Upload your GeoJSON file", type=["geojson", "json"])
local_file_path = r'GeoJSON/buildings.geojson'  # Replace with your local file if not uploading

@st.cache_data
def load_geojson_via_geopandas(file_source):
    """Loads GeoJSON using GeoPandas for optimal spatial parsing."""
    return gpd.read_file(file_source).to_wkt()

@st.cache_data
def load_geojson_via_json(file_source):
    """Alternative: Loads GeoJSON as a raw Python dictionary."""
    if hasattr(file_source, "read"):  # If it's an uploaded file object
        return json.load(file_source)
    with open(file_source, "r", encoding="utf-8") as f:
        return json.load(f)

# 2. Determine which data source to read
data_to_map = None
source_name = ""

if uploaded_file is not None:
    # Use GeoPandas to parse the uploaded file object
    data_to_map = load_geojson_via_geopandas(uploaded_file)
    source_name = uploaded_file.name
else:
    # Fallback to local file path if it exists
    try:
        data_to_map = load_geojson_via_geopandas(local_file_path)
        source_name = "FPN Building Layer"
        st.info(f'"On this page, you can upload a GeoJSON spatial data layer to perform exploratory data analysis (EDA) on campus facilities using Kepler.gl."')
    except FileNotFoundError:
        st.warning("Please upload a GeoJSON file via the sidebar to view the map.")

# 3. Render the Kepler.gl Map if data is ready
if data_to_map is not None:
    # Display basic metadata / attribute table below map
    if st.checkbox("Show Attribute Table of Campus Buildings"):
        st.write(data_to_map)

    # Initialize Kepler.gl map object
    map_config = KeplerGl(height=1000)
    
    # Add GeoJSON layer (Kepler automatically handles Point, LineString, Polygon, MultiPolygon)
    map_config.add_data(data=data_to_map, name=source_name)
    
    # Render static component in Streamlit
    keplergl_static(map_config, center_map=True)

