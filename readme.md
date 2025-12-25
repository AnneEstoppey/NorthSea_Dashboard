## Interactive Dashboard, Norwegian Continental Shelf Oil&Gas Production - 1971 to 2025

Link to dashboard here: https://northseadashboard.streamlit.app
</br>(Dashboard can take a couple of minutes to launch)

The goal of creating this dashboard was to work with production data directly from the downloaded files (.csv and shapefiles), and visualize the field production through the years.<br>

We also wished to experiment with additional elements like a donut graph, and some more advanced table visualization.<br>

With the slider, the user can move through the years and select years 1971 to 2025 with increment of 5 years.

Hovering close to the data points or field outlines will show popups with more detailed information.

Production units are mill Sm3 OE (million Standard cubic meters Oil Equivalent).

The outlines of the fields are from December 2025.

<img width="3346" height="1800" alt="image" src="https://github.com/user-attachments/assets/a90e8531-7d26-4944-b07a-4287a2216a0f" />

<img width="3334" height="1794" alt="image" src="https://github.com/user-attachments/assets/e8cf1467-c628-43fd-9e0a-7b2f363a996e" />

(tested on MS Edge and Chrome in Windows 11, Safari on MacOS, and with iOS on iPhone)<br>

Author: Anne Estoppey, 2025.

### Install

We used Python 3.11.5.

Specific libraries (see requirements file on this repo):<br>
- geopandas
- streamlit
- plotly express
- altair

We installed all the specific libraries with:<br>
> conda install --channel conda-forge library_name

Note that as background we used MapBox Dark Theme, api token is free to use, please check on their website.


### References
All data is coming from the public datasets from Norwegian Offshore Directorate: https://www.sodir.no/en/.<br>
(previously: Norwegian Petroleum Directorate or NPD)

**Datasets:**

Source: https://www.sodir.no/en/facts/data-and-analyses/open-data
- Field outlines (zipped shapefile)

Source: https://factpages.sodir.no/en/field/TableView/Production/Saleable/Yearly<br>
- Field production by year (1971 to 2025)

Source: https://factpages.sodir.no/en/field/TableView/Production/Saleable/TotalNcsYear
- Total offshore production by year (1971 to 2025)

<br>
<br>
Inspiration for this dashboard, please check YouTube tutorial from DataProfessor on Streamlit channel here:<br>
https://www.youtube.com/watch?v=asFqpMDSPdM

Also article from Alan Jones in Medium (subscription might be required):<br>
https://medium.com/towards-data-science/how-to-create-a-simple-gis-map-with-plotly-and-streamlit-7732d67b84e2







