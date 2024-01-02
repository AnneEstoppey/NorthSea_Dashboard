## Interactive Dashboard, Norwegian North Sea Oil&Gas Production - 1971 to 2023
Direct live link to Dashboard: https://northseadashboard.streamlit.app/

The goal of creating this dashboard is to work with production data directly from the downloaded files (.csv and shapefiles), and visualize the field production through the years.<br>

With the slider, the user can move through the years and select years 1971 to 2023 with increment of 5 years.

Hovering close to the data points or field outlines will show popups with more detailed information.

Production units are mill Sm3 OE (million Standard cubic meters Oil Equivanlent).

We restrained the geographical area to the Norwegian side of the North Sea, so that handling of data was less time consuming during developement for rendering on localhost.

The outlines of the fields are the current outlines (2023).

![01_NPD_dashboard_screenshot](https://github.com/AnneEstoppey/NorthSea_Dashboard/assets/35219455/5c4f8bbd-b8e4-4621-9246-16ecf9131b4a)

![03_NPD_dashboard_screenshot](https://github.com/AnneEstoppey/NorthSea_Dashboard/assets/35219455/70a79803-316c-4adc-855a-d5355780e104)

![02_NPD_dashboard_screenshot](https://github.com/AnneEstoppey/NorthSea_Dashboard/assets/35219455/38a64e14-4319-4b9c-8e64-fadff3ea0c66)

Author: Anne Estoppey.

### Install

We used Python 3.11.5.

Specific libraries (see requirements file on this repo):<br>
- geopandas
- streamlit
- plotly express

We installed all the specific libraries with:<br>
> conda install --channel conda-forge library_name


### References
All data is coming from the public datasets from Norwegian Offshore Directorate: https://www.sodir.no/en/.

**Datasets:**

Source: https://www.sodir.no/en/about-us/open-data/
- Field outlines (zipped shapefile)

Source: https://factpages.npd.no/en/field/TableView/Production/Saleable/Yearly<br>
(the link above might be updated early 2024)
- Field production by year (1971 to 2023)

Inspiration for this dashboard, please check YouTube tutorial from DataProfessor on Streamlit channel here:<br>
https://www.youtube.com/watch?v=asFqpMDSPdM

Also article from Alan Jones in Medium (subscription might be required):<br>
https://medium.com/towards-data-science/how-to-create-a-simple-gis-map-with-plotly-and-streamlit-7732d67b84e2
