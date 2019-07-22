
# coding: utf-8

# <b>Scrapping data from wikipedia</b>
# 

# Importing Libraries

# In[8]:


import pandas as pd
from bs4 import BeautifulSoup
import requests

from geopy.geocoders import Nominatim

import matplotlib.cm as cm
import matplotlib.colors as colors

from sklearn.cluster import KMeans

import folium 


# Parse wikipedia page

# In[9]:


source = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup = BeautifulSoup(source,'lxml')


# Find first table from page

# In[11]:


table_can_zipinfo = soup.find('table')
colvals = table_can_zipinfo.find_all('td')

elem_cnt = len(colvals)

postcode = []
borough = []
neighborhood = []

for i in range(0, elem_cnt, 3):
    postcode.append(colvals[i].text.strip())
    borough.append(colvals[i+1].text.strip())
    neighborhood.append(colvals[i+2].text.strip())


# Convert DataFrame from List of values

# In[14]:


df_can_postcode = pd.DataFrame(data=[postcode, borough, neighborhood]).transpose()
df_can_postcode.columns = ['Postcode', 'Borough', 'Neighborhood']


# In[15]:


df_can_postcode


# clean data and transform

# In[16]:


df_can_postcode.drop(df_can_postcode[df_can_postcode['Borough'] == 'Not assigned'].index, inplace=True)
df_can_postcode.loc[df_can_postcode.Neighborhood == 'Not assigned', "Neighborhood"] = df_can_postcode.Borough


# In[22]:


df_grp_can = df_can_postcode.groupby(['Postcode', 'Borough'])['Neighborhood'].apply(', '.join).reset_index()
df_grp_can.columns = ['Postcode', 'Borough', 'Neighborhood']


# Read Geospatial csv file and inner join it with df_grp_can

# In[23]:


df_latlng = pd.read_csv('http://cocl.us/Geospatial_data')
df_latlng.columns = ['Postcode', 'Latitude', 'Longitude']

df_join = pd.merge(df_grp_can, df_latlng, on=['Postcode'], how='inner')


# In[24]:


df_join


# <b>
# Explore and cluster the neighborhoods in Toronto.
# </b>

# In[25]:




neighborhoods = df_join[['Borough', 'Neighborhood', 'Latitude', 'Longitude']].copy()
neighborhoods.head(5)


# In[26]:


print('The dataframe has {} boroughs and {} neighborhoods.'.format(
        len(neighborhoods['Borough'].unique()),
        neighborhoods.shape[0]
    )
)


# In[27]:


address = 'Toronto, Canada'

geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[29]:




# create map of Toronto using latitude and longitude values
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'], neighborhoods['Borough'], neighborhoods['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
map_toronto

