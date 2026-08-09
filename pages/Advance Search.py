import geopandas as gpd
import pandas as pd
import shapely.geometry as geom
import streamlit as st
from streamlit_folium import st_folium
import folium

# Load data...
polygons = gpd.read_file(r'GeoJSON/buildings.geojson', engine="fiona")
lines = gpd.read_file(r'GeoJSON/roads.geojson', engine="fiona")
points = gpd.read_file(r'GeoJSON/poi.geojson', engine="fiona")


st.markdown("## Attribute Search/Query Implementation")

# 2. Extract unique filtering values across all 3 sets
all_regions = list(set(points["Name"].dropna()).union(lines["Road_Name"].dropna()).union(polygons["Building_Name"].dropna()))

# 3. Create a single sidebar or main filter widget
selected_regions = st.multiselect(
    "Select Regions to Filter All Spatial Data:",
    options=all_regions,
    # default=''
)

# 4. Apply the common filter mask to all 3 datasets
if selected_regions:
    filtered_points = points[points["Name"].isin(selected_regions)]
    filtered_lines = lines[lines["Road_Name"].isin(selected_regions)]
    filtered_polygons = polygons[polygons["Building_Name"].isin(selected_regions)]
else:
    # Safe fallback if selection is cleared entirely
    filtered_points = points.iloc[0:0]
    filtered_lines = lines.iloc[0:0]
    filtered_polygons = polygons.iloc[0:0]

# 5. Display tabular views or render on maps
st.subheader("Filtered Points Dataset")
if not filtered_points.empty:
    st.dataframe(pd.DataFrame(filtered_points.drop(columns='geometry'))) # Drop geometry for clean text table
else:
    st.info("No points selected.")

st.subheader("Filtered Line Dataset")
if not filtered_lines.empty:
    st.dataframe(pd.DataFrame(filtered_lines.drop(columns='geometry')))
else:
    st.info("No lines selected.")

st.subheader("Filtered Polygons Dataset")
if not filtered_polygons.empty:
    st.dataframe(pd.DataFrame(filtered_polygons.drop(columns='geometry')))
else:
    st.info("No buildings/polygons selected.")

# ----------------------------------------------------
# ----------------------------------------------------
# Initialize background map
m = folium.Map(location=[8.565, 7.715], zoom_start=13)
folium.TileLayer("Cartodb Positron", name="Street View").add_to(m)

# Add all 3 filtered GeoDataFrames safely to the same map object
# Polygons Layer Safety Check
if filtered_polygons is not None and not filtered_polygons.empty:
    cleaned_polygons = filtered_polygons[filtered_polygons.geometry.notnull()]
    if not cleaned_polygons.empty:
        folium.GeoJson(cleaned_polygons).add_to(m)

# Lines Layer Safety Check
if filtered_lines is not None and not filtered_lines.empty:
    cleaned_lines = filtered_lines[filtered_lines.geometry.notnull()]
    if not cleaned_lines.empty:
        folium.GeoJson(cleaned_lines).add_to(m)

# Points Layer Safety Check
if filtered_points is not None and not filtered_points.empty:
    cleaned_points = filtered_points[filtered_points.geometry.notnull()]
    if not cleaned_points.empty:
        folium.GeoJson(cleaned_points).add_to(m)

# Render map dynamically inside Streamlit
st_folium(m, width=700, height=500)
