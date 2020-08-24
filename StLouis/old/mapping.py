# Daniel Van Hoesen
# St. Louis Neighborhoods
# read in shape file and display

# created 6/23/2020

# 1990 to 2010
# https://www.stlouis-mo.gov/data/tags/tag.cfm?id=1

############################
## Imports
############################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import csv
import numpy as np


############################
## Read and index shapefile data
############################

shape_file = "neighborhood_shape_files/BND_Nhd88_cw.shp"
data = gpd.read_file(shape_file)


data = data[["NHD_NAME","geometry"]]
data.set_index("NHD_NAME", inplace=True)

#  Add color column to data frame
data['color_2010'] = 'b'
data['color_2000'] = 'b'

parks_data = data.loc[["Missouri Botanical Garden", "O'Fallon Park", "Forest Park",
					"Belfontaine/Calvary Cemetery", "Fairground Park", "Tower Grove Park",
					"Wilmore Park", "Carondelet Park", "Penrose Park"]]

data = data.drop(["Missouri Botanical Garden", "O'Fallon Park", "Forest Park",
					"Belfontaine/Calvary Cemetery", "Fairground Park", "Tower Grove Park",
					"Wilmore Park", "Carondelet Park", "Penrose Park"])

parks_data['color'] = 'g'

print("\nNumber of Neighborhoods: ", len(data))
print("Number of Parks: ", len(parks_data))


#c = "The Ville"
#data.loc[c]['color'] = 'r'


############################
## Read in neighborhood data
############################

filename = 'neighborhoods_data.csv'
raw_data = pd.read_csv(filename, header=0)


"""
# alphabetically sort names without messing with geopandas dataframe
names = []
for name in data.index:
	names.append(name)

names.sort()

# create csv of all neighborhoods
with open(filename, 'w') as file:
	writer = csv.writer(file)
	writer.writerow(['neighborhoods'])
	for name in names:
		writer.writerow([name])
"""

############################
## Interpolate data and change color
############################

# may help to distinguish colors if logarithm of data
#raw_data['2010 population'] = np.log(raw_data['2010 population'])
#raw_data['2000 population'] = np.log(raw_data['2000 population'])

max_pop_2010 = raw_data['2010 population'].max()
max_pop_2000 = raw_data['2000 population'].max()

print('max population 2010: ', max_pop_2010)
print('max population 2000: ', max_pop_2000)

if max_pop_2000 > max_pop_2010:
	raw_data['color_2010'] = raw_data['2010 population'].values / max_pop_2000
	raw_data['color_2000'] = raw_data['2000 population'].values / max_pop_2000
else:
	raw_data['color_2010'] = raw_data['2010 population'].values / max_pop_2010
	raw_data['color_2000'] = raw_data['2000 population'].values / max_pop_2010


for name in data.index:

	# 2010 colors
	color_val = plt.cm.Greys(raw_data[raw_data.neighborhoods==name].color_2010)
	color_val = to_hex(color_val[:,0:3][0], keep_alpha=True).upper()
	data.color_2010[data.index==name] = color_val

	# 2000 colors
	color_val = plt.cm.Greys(raw_data[raw_data.neighborhoods==name].color_2000)
	color_val = to_hex(color_val[:,0:3][0], keep_alpha=True).upper()
	data.color_2000[data.index==name] = color_val

############################
## Plotting
############################

fig1, ax1 = plt.subplots(figsize=(10,8),ncols=2)

#2010 data
data.plot(color=data.color_2010, edgecolor='black', ax=ax1[0])
parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[0])
ax1[0].set_axis_off()

#2000 data
data.plot(color=data.color_2000, edgecolor='black', ax=ax1[1])
parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[1])
ax1[1].set_axis_off()


"""
# add names of neighborhoods
for name in data.index:
	ct = data.loc[name].geometry.centroid
	ax1.annotate(name, xy=(ct.x, ct.y))

# add names of parks
for name in parks_data.index:
	ct = parks_data.loc[name].geometry.centroid
	ax1.annotate(name, xy=(ct.x, ct.y))
"""

plt.show()

