import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
## from app_token import MAPBOX_TOKEN

# Your Mapbox Access Token
## mapbox_access_token = MAPBOX_TOKEN

mapbox_access_token = st.secrets["MAPBOX_TOKEN"]

# Page configuration
st.set_page_config(
    page_title="NPD dashboard",
    page_icon="🛢",
    layout="wide",
    initial_sidebar_state="collapsed")

# CSS styling
# st.markdown("""
# <style>

# [data-testid="block-container"] {
#     padding-left: 2rem;
#     padding-right: 2rem;
#     padding-top: 1rem;
#     padding-bottom: -1rem;
#     margin-bottom: -1rem;
# }
            
# [data-testid="stVerticalBlock"] {
#     padding-left: 0rem;
#     padding-right: 0rem;
# }

# </style>
# """, unsafe_allow_html=True)

st.markdown("""
    <style>
            .block-container {
                padding-top: 11rem;
                padding-bottom: 0rem;
                padding-left: 0rem;
                padding-right: 0rem;
                gap: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)


####################################
#### Fields and production data ####
####################################

# Function to read the shapefile for the fields
def read_shapefile(zip_file_path):
    return gpd.read_file(f"zip://{zip_file_path}")

# Function to read and clean the production data
def read_and_clean_prod_data(csv_file_path):
    df_prod_data = pd.read_csv(csv_file_path, sep=';')
    df_prod_data[df_prod_data._get_numeric_data() < 0] = 0
    return df_prod_data

# Function to select fields in the North Sea
def select_north_sea(gdf_fields):
    return gdf_fields[gdf_fields['main_area'] == 'North sea']

# Function to prepare production data DataFrame
def prepare_prod_data(df_prod_data):
    df_production_all_years = df_prod_data.pivot_table(
        index=['prfInformationCarrier', 'prfNpdidInformationCarrier'], 
        columns='prfYear', 
        values='prfPrdOeNetMillSm3', 
        aggfunc='sum').fillna(0)
    df_production_all_years = df_production_all_years.loc[:, '1971':'2023']
    df_production_all_years.columns = df_production_all_years.columns.astype(str)
    df_production_all_years.reset_index(inplace=True)
    df_production_all_years.columns.name = None

    selected_columns = ['prfInformationCarrier', 'prfNpdidInformationCarrier', 
                        '1971', '1976', '1981', '1986', '1991', '1996', 
                        '2001', '2006', '2011', '2016', '2021', '2023']
    return df_production_all_years[selected_columns]

# Function to merge production data with field data
def merge_prod_with_fields(df_prod, gdf_fields):
    merged_data = pd.merge(
        df_prod, gdf_fields, 
        left_on='prfNpdidInformationCarrier', 
        right_on='idField'
    )
    merged_data = merged_data.sort_values(by='fieldName').reset_index(drop=True)
    return gpd.GeoDataFrame(merged_data, geometry='geometry')

# Main script
zip_file_path = './data_from_NPD/fldArea_shape.zip'
gdf_fields = read_shapefile(zip_file_path)

df_prod_data = read_and_clean_prod_data('./data_from_NPD/production-yearly-by-field.csv')
gdf_fields_NS = select_north_sea(gdf_fields)
df_production_5_years = prepare_prod_data(df_prod_data)
gdf_merge_fields_prod_geo = merge_prod_with_fields(df_production_5_years, gdf_fields_NS)


def plot_map_prod(gdf_merge_fields_prod_geo, mapbox_access_token, selected_year):
    # Convert the year to string for column indexing
    selected_year_str = str(selected_year)

    # Create the Plotly figure
    fig_prod = go.Figure()

    # Add field outlines
    for feature, name, operator, dctype in zip(gdf_merge_fields_prod_geo.geometry.__geo_interface__['features'], 
                                               gdf_merge_fields_prod_geo['fieldName'], 
                                               gdf_merge_fields_prod_geo['OpLongName'], 
                                               gdf_merge_fields_prod_geo['Dctype']):
        coords = feature['geometry']['coordinates']
        if feature['geometry']['type'] == 'Polygon':
            coords = [coords]
        for poly in coords:
            x, y = zip(*poly[0])
            hover_text = f"{name}<br>Operator: {operator}<br>HC type: {dctype}"
            fig_prod.add_trace(go.Scattermapbox(
                lon=x, lat=y, mode='lines',
                line=dict(width=0.5, color='#CDC5AF'),
                hoverinfo='text', hovertext=[hover_text] * len(x),
                showlegend=False
            ))
            

    # Add production markers
    fig_prod.add_trace(go.Scattermapbox(
        lon=gdf_merge_fields_prod_geo.geometry.centroid.x,
        lat=gdf_merge_fields_prod_geo.geometry.centroid.y,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=gdf_merge_fields_prod_geo[selected_year_str] * 4,
            # color='red', opacity=0.7color=gdf_merge_fields_prod_geo['1986'],  # Use production values for color
            color=gdf_merge_fields_prod_geo[selected_year_str],  # Use production values for color
            colorscale='Oranges',  # Define the color scale
            opacity=0.7,
            cmin=0,  # Set the min value for the color scale
            cmax=gdf_merge_fields_prod_geo[selected_year_str].max(),  # Set the max value for the color scale
            showscale=True,  # Display the color scale bar
            colorbar=dict(
            title=dict(
                text='Net mill<br>Sm3 OE',  # Color bar title
                side='top'
                )
            )
        ),
        hoverinfo='text',
        hovertext=gdf_merge_fields_prod_geo['fieldName'] + '<br>Production: ' +
                gdf_merge_fields_prod_geo[selected_year_str].astype(str) + ' mill Sm3 OE',
        hoverlabel=dict(bgcolor='orange', font_color='black'),
    ))

    # Set up layout with Mapbox access token
    fig_prod.update_layout(
        mapbox_style="dark",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0, pitch=0, zoom=5.3,
            center={"lat": 59, "lon": 2}
        ),
        autosize=True, height=850, width=900,
        title='Production in Norwegian North Sea',
        showlegend=False
    )

    return fig_prod


# Components
title_container = st.container()
subtitle_container = st.container()
map_container = st.container()
slider_container = st.container()

with title_container:
    st.markdown("<h2 style='text-align: center;'>Norwegian North Sea - Production 1971 to 2023</h2>", unsafe_allow_html=True)

## with subtitle_container:
##    st.markdown("<div style='text-align: center;'>General description here.</div>", unsafe_allow_html=True)

# Define the specific years for the slider
year_options = [1971, 1976, 1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021, 2023]

# Slider for selecting the year
with slider_container:
    selected_year = st.select_slider("Select a Year", options=year_options, value=2023)

# Plot the map
with map_container:
    fig_prod = plot_map_prod(gdf_merge_fields_prod_geo, mapbox_access_token, selected_year)
    st.plotly_chart(fig_prod, use_container_width=True)
