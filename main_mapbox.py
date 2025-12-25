import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
import altair as alt
## from app_token import MAPBOX_TOKEN    # <--- use this for dev on localhost

import sys

# Your Mapbox Access Token
## mapbox_access_token = MAPBOX_TOKEN   # <--- use this for dev on localhost

mapbox_access_token = st.secrets["MAPBOX_TOKEN"] # <--- use this for prod on Streamlit server

# Page configuration
st.set_page_config(
    page_title="NPD dashboard",
    page_icon="🛢",
    layout="wide",
    initial_sidebar_state="collapsed")

alt.themes.enable("dark")

# CSS styling
st.markdown("""
    <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 0rem;
                gap: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)


#########################
#### Loading Data... ####
#########################

zip_shapefile_path = './data_from_NPD/fldArea_shape.zip'
csv_prod_file_path = './data_from_NPD/field_production_yearly.csv'
csv_field_prod_file_path = './data_from_NPD/field_production_totalt_NCS_year__DisplayAllRows.csv'


# Function to read the fields shapefile
def read_shapefile(zip_shapefile_path):
    gdf_fields = gpd.read_file(f"zip://{zip_shapefile_path}")
    gdf_fields.crs = "EPSG:23032"   # Set the coordinate reference system (CRS) to UTM zone 32N, ED50
    return gdf_fields


# Function to read and clean the field production data
def read_and_clean_prod_data(csv_file_path):
    df_prod_data = pd.read_csv(csv_file_path, sep=',')
    df_prod_data[df_prod_data._get_numeric_data() < 0] = 0
    return df_prod_data


# Function to read the total yearly production
# for whole Norwegian continental shelf
def read_field_prod_data_yearly(csv_file_path):
    df_field_prod_data_yearly = pd.read_csv(csv_file_path, sep=',')
    # drop all fields, except 'prfYear' and 'prfPrdOeNetMillSm3'
    df_field_prod_data_yearly = df_field_prod_data_yearly[['prfYear', 'prfPrdOeNetMillSm3']]
    # order dataframe descending by 'prfYear', reset index
    df_field_prod_data_yearly = df_field_prod_data_yearly.sort_values(by='prfYear', ascending=False).reset_index(drop=True)
    return df_field_prod_data_yearly


gdf_fields = read_shapefile(zip_shapefile_path)
df_prod_data = read_and_clean_prod_data(csv_prod_file_path)
df_field_prod_data_yearly = read_field_prod_data_yearly(csv_field_prod_file_path)


################################################
#### Fields and production - data wrangling ####
################################################

# Function to prepare production data DataFrame for selected years
def prepare_prod_data(df_prod_data):
    df_production_all_years = df_prod_data.pivot_table(
        index=['prfInformationCarrier', 'prfNpdidInformationCarrier'], 
        columns='prfYear', 
        values='prfPrdOeNetMillSm3', 
        aggfunc='sum').fillna(0)
    df_production_all_years = df_production_all_years.loc[:, '1971':'2025']
    df_production_all_years.columns = df_production_all_years.columns.astype(str)
    df_production_all_years.reset_index(inplace=True)
    df_production_all_years.columns.name = None

    selected_columns = ['prfInformationCarrier', 'prfNpdidInformationCarrier', 
                        '1971', '1976', '1981', '1986', '1991', '1996', 
                        '2001', '2006', '2011', '2016', '2021', '2025']
    return df_production_all_years[selected_columns]


# Function to merge production data with field data
def merge_prod_with_fields(df_prod, gdf_fields):
    merged_data = pd.merge(
        df_prod, gdf_fields,         # ALL fields!
        left_on='prfNpdidInformationCarrier', 
        right_on='idField'
    )
    merged_data = merged_data.sort_values(by='fieldName').reset_index(drop=True)
    return gpd.GeoDataFrame(merged_data, geometry='geometry')


# Function to summarize production data by year for all fields
def sum_prod_yearly_NS(gdf_merge_fields_prod_geo):
    # Drop the 'geometry' column
    df = gdf_merge_fields_prod_geo.drop(columns=['geometry'])
    # select only fields in North Sea from df
    df = df[df['main_area'] == 'North sea'].reset_index(drop=True)
    # Pivot the DataFrame to sum production values by year
    production_years = [col for col in df.columns if col.isnumeric()]
    df_sum_prod_yearly_NS = df[production_years].sum().reset_index()
    df_sum_prod_yearly_NS.columns = ['Year', 'Total Production mill Sm3 OE']

    return df_sum_prod_yearly_NS


# Function to read the total yearly production
# for whole Norwegian continental shelf
def read_prod_data_yearly_total(csv_file_path):
    df_prod_data_yearly_total = pd.read_csv(csv_file_path, sep=',')
    # drop all fields, except 'prfYear' and 'prfPrdOeNetMillSm3'
    df_prod_data_yearly_total = df_prod_data_yearly_total[['prfYear', 'prfPrdOeNetMillSm3']]
    # order dataframe descending by 'prfYear', reset index
    df_prod_data_yearly_total = df_prod_data_yearly_total.sort_values(by='prfYear', ascending=False).reset_index(drop=True)

    return df_prod_data_yearly_total


df_production_5_years = prepare_prod_data(df_prod_data)
gdf_merge_fields_prod_geo = merge_prod_with_fields(df_production_5_years, gdf_fields)
df_sum_prod_yearly_NS = sum_prod_yearly_NS(gdf_merge_fields_prod_geo)


##########################################
#### Functions for dashboard elements ####
##########################################

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
                lon=x, 
                lat=y, 
                mode='lines',
                line=dict(width=0.5, color='#CDC5AF'),
                hoverinfo='text', 
                hovertext=[hover_text] * len(x),
                showlegend=False
            ))
            

    # Add production markers
    fig_prod.add_trace(go.Scattermapbox(
        lon=gdf_merge_fields_prod_geo.geometry.centroid.x,
        lat=gdf_merge_fields_prod_geo.geometry.centroid.y,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=gdf_merge_fields_prod_geo[selected_year_str] * 4,
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
            bearing=0, 
            pitch=0, 
            zoom=3.5,
            center={"lat": 65, "lon": 3}
        ),
        height=850, 
        width=900,
        title='Norwegian Continental Shelf Field Production - Net mill Sm3 OE',
        showlegend=False
    )

    return fig_prod


def create_altair_donut_chart(df_total, df_north_sea, year):
    # Extract production values for the specified year
    total_prod = df_field_prod_data_yearly.loc[df_field_prod_data_yearly['prfYear'] == year, 'prfPrdOeNetMillSm3'].values[0]
    north_sea_prod = df_sum_prod_yearly_NS.loc[df_sum_prod_yearly_NS['Year'] == str(year), 'Total Production mill Sm3 OE'].values[0]

    # Calculate North Sea production as a percentage of total production
    north_sea_percentage = (north_sea_prod / total_prod) * 100 if total_prod != 0 else 0

    # Data for the chart
    data = pd.DataFrame({
        'Category': ['North Sea Production', ''],
        'Value': [north_sea_percentage, 100 - north_sea_percentage],
        'Color': ['#F39C12', '#875A12']  # Bright for North Sea, darker for the rest
    })

    width=150
    height=150

    # Create the donut chart
    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Value", type="quantitative", stack=True),
        color=alt.Color(field="Color", type="nominal", scale=None, legend=None),
        tooltip=['Category', 'Value'],
    ).properties(
        width=width,
        height=height
    )

    # Text in the middle of the donut
    text = alt.Chart(pd.DataFrame({'Value': [f'{north_sea_percentage:.1f} %']})).mark_text(
        size=20, 
        color='#F39C12',
        fontStyle='italic',
    ).encode(
        text='Value:N'
    ).properties(
        # width=width,
        # height=height,
    )

    # Combine the donut chart and the text
    combined_chart = (chart + text).configure_view().configure(background='transparent')

    return combined_chart


###############################
#### Building up dashboard ####
###############################

title_container = st.container()
main_container = st.container()


with title_container:
    st.markdown("<h2 style='text-align: center;'>Norwegian Continental Shelf - Field Production 1971 to 2025</h2>", 
                unsafe_allow_html=True)
    st.markdown("")  # Add extra space below the title


with main_container:
    # Create three columns. The middle column acts as a spacer
    left_column, spacer_column_mid, right_column, spacer_column_end = st.columns([3, 0.1, 1.1, 0.1])

    with left_column:
        # Define the specific years for the slider
        year_options = [1971, 1976, 1981, 1986, 1991, 1996, 2001, 2006, 2011, 2016, 2021, 2025]

        # Slider for selecting the year
        selected_year = st.select_slider(
                            "Select a Year - Browse over fields for more information", 
                            options=year_options, 
                            value=2025,
                            )
        # Plot the map
        fig_prod = plot_map_prod(gdf_merge_fields_prod_geo, mapbox_access_token, selected_year)
        st.plotly_chart(fig_prod, use_container_width=True)

    with right_column:
        # Placeholder for new elements
        st.markdown("Production in North Sea - ""%"" of total offshore production - " + str(selected_year), unsafe_allow_html=True)
        donut_chart = create_altair_donut_chart(df_field_prod_data_yearly, df_sum_prod_yearly_NS, year=selected_year)
        st.altair_chart(donut_chart)

        st.markdown("Highest production fields" + " - " + str(selected_year), unsafe_allow_html=True)
        df_prod_for_table_element = df_production_5_years[['prfInformationCarrier', str(selected_year)]].sort_values(
            by=str(selected_year), ascending=False).reset_index(drop=True)
        
        # extract total prod value for selected year from df_prod_data_yearly_total, to be used as max_value for progress bar
        total_prod = df_field_prod_data_yearly.loc[df_field_prod_data_yearly['prfYear'] == selected_year, 'prfPrdOeNetMillSm3'].values[0]

        st.dataframe(df_prod_for_table_element,
                     column_order=('prfInformationCarrier', str(selected_year)),
                     hide_index=True,
                     width="stretch",
                     column_config={'prfInformationCarrier': st.column_config.TextColumn(
                         'Field Name',
                        ),
                        str(selected_year): st.column_config.ProgressColumn(
                            'Net mill Sm3 OE',
                            format='%.2f',
                            min_value=0,
                            max_value=total_prod,
                        ),
                     }
                )
        # st.markdown("")

        with st.expander('References', expanded=True):
            st.write('''
                Norwegian Offshore Directorate (NOD): [Open data](https://www.sodir.no/en/about-us/open-data/), 
                [NOD FactPages](https://factpages.sodir.no/en/field/TableView/Production/Saleable/TotalNcsYear)
                ''')
            st.write('''Github repo (author): [NorthSea Dashboard](https://github.com/AnneEstoppey/NorthSea_Dashboard)''')