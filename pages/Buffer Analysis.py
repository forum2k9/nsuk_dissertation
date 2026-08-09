import folium
import geopandas as gpd
import streamlit as st
from shapely.geometry import Point
from streamlit_folium import st_folium

st.set_page_config(page_title="Dynamic Buffer App", layout="wide")
st.title("🗺️ Custom Dynamic Buffer Generator")

# 1. User Input Controls in the Sidebar
st.sidebar.header("1. Coordinates")
lat = st.sidebar.number_input("Latitude:", min_value=-90.0, max_value=90.0, value=8.565, step=0.01)
lon = st.sidebar.number_input("Longitude:", min_value=-180.0, max_value=180.0, value=7.715, step=0.01)

st.sidebar.header("2. Projection Settings")
# EPSG:32631 is UTM Zone 31N (West Africa/Europe), EPSG:3857 is Web Mercator (Global, less accurate for distance)
epsg_choice = st.sidebar.selectbox(
    "Select Local Metric Projection (EPSG):",
    options=["EPSG:26332", "EPSG:3857"],
    index=0,
    help="Use a local UTM zone for high metric accuracy, or 3857 for a general global estimate."
)

st.sidebar.header("3. Buffer Settings")
buffer_distance = st.sidebar.slider("Buffer Distance (meters):", min_value=500, max_value=5000, value=3000, step=500)
buffer_color = st.sidebar.color_picker("Pick a Buffer Color:", "#b4301f")

# 2. Geospatial Processing Pipeline
@st.cache_data
def generate_dynamic_buffer(latitude, longitude, target_epsg, distance):
    # Create point from user coordinates
    point = Point(longitude, latitude)
    gdf = gpd.GeoDataFrame({'geometry': [point]}, crs="EPSG:4326")
    
    # Project, buffer, and convert back to WGS84
    gdf_projected = gdf.to_crs(target_epsg)
    buffer_projected = gdf_projected.buffer(distance)
    return buffer_projected.to_crs("EPSG:4326")

# Execute data creation based on inputs
try:
    buffer_wgs84 = generate_dynamic_buffer(lat, lon, epsg_choice, buffer_distance)

    # 3. Build and Render the Folium Map
    m = folium.Map(location=[lat, lon], zoom_start=12, tiles="cartodbpositron")

    # Add the center point marker
    folium.Marker(
        [lat, lon], 
        popup=f"Center: {lat}, {lon}",
        tooltip="Center Point"
    ).add_to(m)

    # Add the dynamic buffer polygon
    folium.GeoJson(
        buffer_wgs84,
        style_kwds={
            'fillColor': buffer_color, 
            'color': buffer_color, 
            'fillOpacity': 0.3,
            'weight': 2
        }
    ).add_to(m)

    # Render in layout
    st_folium(m, width="100%", height=600, returned_objects=[])

except Exception as e:
    st.error(f"An error occurred during geometric projection: {e}")
    st.info("Tip: Ensure your selected EPSG code supports your coordinate region.")
