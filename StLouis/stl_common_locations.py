# Daniel Van Hoesen
# St. Louis Neighborhoods
# read in shape file and display

# created 6/23/2020


############################
## Imports
############################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPolygon
import csv
import numpy as np
import math


############################
## Functions
############################



############################
## Read and index shapefile data
############################

# read in parks data file
data_file = 'stl_boundary.csv'

data_csv = pd.read_csv(data_file)
data = gpd.GeoDataFrame(data_csv)

# set the names as the index
data.set_index("Name", inplace=True)

# set the geometry column to the geometry
data['geometry'] = data['geometry'].apply(wkt.loads)
data.set_geometry('geometry')

poly = data.loc['STL_boundary'].geometry
#print(poly.bounds)

lon1, lat1, lon2, lat2 = poly.bounds

lat_diff = np.abs(lat1-lat2)
lon_diff = np.abs(lon1-lon2)

# number of points in latitude direction
n_lat = 201

# latitude distance (in degrees)
lat_dist = lat_diff / n_lat
print('latitude distance: ', lat_dist)
print('latitude points: ', n_lat)

# number of points in the longitude direction keeping the distance equal to the latitude distance spacing
n_lon = int(n_lat * lon_diff / lat_diff)
lon_dist = lon_diff/n_lon
print('longitude distance: ', lon_dist)
print('longitude points', n_lon)

lats = np.linspace(lat1, lat2, num=n_lat, endpoint=True)
lons = np.linspace(lon1, lon2, num=n_lon, endpoint=True)

boundaries = []

for i in range(len(lons)-1):
	for j in range(len(lats)-1):
		p1 = Point(lons[i],lats[j])
		p2 = Point(lons[i+1],lats[j])
		p3 = Point(lons[i+1],lats[j+1])
		p4 = Point(lons[i],lats[j+1])

		poly_new = Polygon([[p1.x,p1.y],[p2.x,p2.y],[p3.x,p3.y],[p4.x,p4.y]])
		intersection = poly_new.intersection(poly)

		# some will be multipolygons, covert to polygons
		if type(intersection)!=Polygon:
			intersection = Polygon(list(intersection))

		if intersection.is_empty:
			do_nothing = 0
		else:
			boundaries.append(intersection)


poly_df = pd.DataFrame(boundaries, columns=['geometry'])
poly_data = gpd.GeoDataFrame(poly_df, geometry='geometry')

ax = data.plot(color='white', edgecolor='black')
poly_data.plot(color='blue', edgecolor='red', ax=ax)

plt.show()

poly_data.to_csv('temp.csv')