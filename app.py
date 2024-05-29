import zipfile
import requests
import io
import os
# import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
# from streamlit_folium import st_folium

# # This section will need to be rewritten if we even want to keep it. Streamlit throws an error with it.
# # I think it's because Streamlit uses linux and MacOS is a little different, idk we'll see.

# if not os.path.exists("/usa/usa.shp"):
#   r = requests.get("https://static-data-screeningtool.geoplatform.gov/data-versions/1.0/data/score/downloadable/1.0-shapefile-codebook.zip",stream=True)
#   with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
#       zip_ref.extract("1.0-codebook.csv")
#       with zip_ref.open("usa.zip") as nested_zip:
#         nested_zip_filedata = io.BytesIO(nested_zip.read())
#         with zipfile.ZipFile(nested_zip_filedata) as unzipped_nested_zip:
#           unzipped_nested_zip.extractall("/usa/")

# r2 = requests.get("https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip")
# with zipfile.ZipFile(io.BytesIO(r2.content)) as zip_ref:
#   zip_ref.extractall("/ztca")
          


geo_data = gpd.read_file("usa/usa.shp",engine="pyogrio",use_arrow=True)
df_cols = pd.read_csv("usa/columns.csv")
# zcta = gpd.read_file("/content/ztca/tl_2023_us_zcta520.shp",engine="pyogrio",use_arrow=True).to_crs(geo_data.crs)
zips_to_tracts = pd.read_excel("ZIP_TRACT_032024.xlsx")
demograph_data = pd.read_csv("RegionMapPopulated.csv")

geo_data = geo_data[~geo_data.geometry.isna()]


geo_data.GEOID10 = geo_data.GEOID10.astype("int64")
geo_data_with_zips = geo_data.merge(zips_to_tracts,how="left",left_on="GEOID10",right_on="TRACT")
full_data = geo_data_with_zips.merge(demograph_data, how="left",left_on="ZIP",right_on="Zip Code")

cols = full_data.columns.tolist()
col_choices = st.multiselect(
  "What columns would you like to view?",
  cols,
  ["geometry","GEOID10","SF","TPF","ZIP"]
)
full_data = full_data.loc[:,col_choices]


states = full_data.SF.unique().tolist()
continental = states.copy()
non_continental = ['Hawaii','Alaska','Puerto Rico','American Samoa', 'Guam', 'Northern Mariana Islands','Virgin Islands']
us49 = full_data.copy()
for n in non_continental:
  continental.remove(n)
  us49 = us49[us49.SF != n]


states.reverse()
states.append("Continental U.S.")
states.append("Entire U.S.")
states.reverse()
mapping_var = "TPF"

state_choice = st.multiselect(
  "What area of the country would you like to look at?",
  states,
  ["Vermont","New Hampshire"]
)


if state_choice == "Entire U.S.":
  plot_data = full_data.copy()
elif state_choice == "Continental U.S.":
  plot_data = us49.copy()
else:
  plot_data = full_data[full_data.SF.isin(state_choice)]




# col_name = df_cols[df_cols.shapefile_column==mapping_var].iat[0,1]

fig,ax = plt.subplots(1,1)

m = plot_data.explore(column=mapping_var) #,legend=True,legend_kwds={"label":col_name,"orientation":"horizontal"})
st_data = st_folium(m)
