import folium
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import Search

# -------- Layout configuration --------
st.set_page_config(page_title="Smart Web-Based Campus Platform...", layout="wide")
st.markdown("### Smart Web-Based Campus Platform for FPN")
st.html("<style>.stMainBlockContainer { padding-top: 3rem; }</style>")

st.logo("img/logo.png")

# -------- Sidebar: Camera Feeds or Filters --------
with st.sidebar:
    st.header("Campus Points of Interest")
    # -------- Add placeholder for feed images
    # st.image("img/01.jpg", caption="Gate Security Feed")
    # st.image("img/02.jpg", caption="Gate Security Feed")
    # st.image("img/03.jpg", caption="Gate Security Feed")

    search_text = st.text_input(label="Seach the map...", value="")

# -------- Main Map Area --------
col1, col2 = st.columns([3, 1])
with col1:
    # bounds = [[8.55, 7.70], [8.58, 7.73]]
    bounds = [[8.61, 7.67], [8.56, 7.75]]

    m = folium.Map(
        location=[8.565, 7.715], 
        zoom_start=13, 
        control_scale=True,
        min_zoom=12,
        max_zoom=20,
        zoom_control=True,
        max_bounds=True,
        min_lat=8.61,
        min_lon=7.67,
        max_lat=8.56,
        max_lon=7.75,
        tiles=None
    )

    # Add preferred default basemap LAST (visible on startup)
    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri", name="Satellite View").add_to(m)
    folium.TileLayer(tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", attr="OpenTopoMap", name="Topographic View").add_to(m)
    folium.TileLayer("Cartodb Positron", name="Street View").add_to(m)

    # Add GeoJSON layers here
    boundary = gpd.read_file(r'GeoJSON/boundary.geojson', engine="fiona").to_wkt()
    building = gpd.read_file(r'GeoJSON/buildings.geojson', engine="fiona").to_wkt()
    road = gpd.read_file(r'GeoJSON/roads.geojson', engine="fiona").to_wkt()

    folium.GeoJson(r'GeoJSON/boundary.geojson', name="Campus Boundary", color="red", weight=4, fill=False).add_to(m)
    folium.GeoJson(r'GeoJSON/buildings.geojson', name="Campus Buildings", color="black", weight=1, fill=True).add_to(m)
    folium.GeoJson(r'GeoJSON/roads.geojson', name="Campus Roads", color="black", weight=1.2).add_to(m)
    
    poi = folium.GeoJson(
        r'GeoJSON/poi.geojson',
        name="Campus Points of Interest",
        marker=folium.Marker( icon=folium.Icon(color="blue", icon="info-sign") ),
        tooltip=folium.GeoJsonTooltip(fields=["Name"], aliases=[""]),
        popup=folium.GeoJsonPopup(fields=["image"], aliases=[""])
    ).add_to(m)

    # Bind Search to the layer
    Search(
        layer=poi,
        geom_type="Point",
        placeholder="Search Places on Campus...",
        search_label="Name", # Feature property to index
        position="topright"
    ).add_to(m)

    # Helper function to determine color based on the attribute value
    def get_color(predicted):
        if predicted == 1:
            return "#1eb45f" # Vegetation
        elif predicted == 2:
            return "#da9426" # Bear grond
        else:
            return "#3d80ea"  # water

    # Create the style function
    # The function accepts a single GeoJSON feature and extracts its properties
    def style_function(feature):
        predicted = feature["properties"]["predicted"]
        return {
            "fillColor": get_color(predicted),
            "color": "black",       # Border color
            "weight": 0.2,          # Border thickness
            "fillOpacity": 0.6      # Opacity of the polygon fill
        }

    folium.GeoJson('GeoJSON/landcover.geojson', style_function=style_function, name="Campus LULC", show=False, color="green", weight=2, fill=True).add_to(m)

    # Add the Layer Control
    folium.LayerControl().add_to(m)

    # Render in Streamlit
    st_folium(m, width=600, height=500)

# -------- Metrics Row --------
with col2:
    st.metric(label="Total Area", value="2146.158 Ha")
    st.metric(label="Total Buildings", value="311")
    st.metric(label="Roads Network", value="85 ", delta="38.776 km of road network")
    st.metric(label="Point of Interest", value="22")

# -------- Bottom Panel: Data Table --------
st.subheader("Attribute Table Details")
with st.expander("Building Attribute", icon="🏠"):
    st.write("This are the attributes of the buildings...:")
    st.dataframe(building)
with st.expander("Roads Attribute", icon="🛣️"):
    st.write("This are the attributes of the roads...:")
    st.dataframe(road)
