# Daniel Van Hoesen
# St. Louis Neighborhoods
# read in shape file and display

# created 6/23/2020

# 1990 to 2010
# https://www.stlouis-mo.gov/data/tags/tag.cfm?id=1
# http://dynamic.stlouis-mo.gov/census/neigh_comp.cfm


# 1940 pdf

# 1950 pdf

# 1960 pdf 

# 1970
# https://www2.census.gov/library/publications/decennial/1970/phc-1/39204513p18ch09.pdf

# 1980
# https://archive.org/details/1980censusofpo8023131unse/page/386/mode/2up

# 1990 tract numbers
# https://www2.census.gov/geo/maps/trt1990/st29_Missouri/29510_StLouis/

############################
## Imports
############################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
#from matplotlib.colors import to_hex
import csv
import numpy as np


############################
## Functions
############################



############################
## Read and index shapefile data
############################

shape_file = "neighborhood_shape_files/BND_Nhd88_cw.shp"
data = gpd.read_file(shape_file)


data = data[["NHD_NAME","geometry"]]
data.set_index("NHD_NAME", inplace=True)

#  Add color column to data frame
data['bl_pop_color_1990'] = 'r'
data['income_color_1990'] = 'r'

parks_data = data.loc[["Missouri Botanical Garden", "O'Fallon Park", "Forest Park",
					"Belfontaine/Calvary Cemetery", "Fairground Park", "Tower Grove Park",
					"Wilmore Park", "Carondelet Park", "Penrose Park"]]

data = data.drop(["Missouri Botanical Garden", "O'Fallon Park", "Forest Park",
					"Belfontaine/Calvary Cemetery", "Fairground Park", "Tower Grove Park",
					"Wilmore Park", "Carondelet Park", "Penrose Park"])

parks_data['color'] = 'g'

print("\nNumber of Neighborhoods: ", len(data))
print("Number of Parks: ", len(parks_data))


data = data.sort_index()
data = data.to_crs(epsg=4326)
data.to_csv('temp.csv')

"""

#c = "The Ville"
#data.loc[c]['color'] = 'r'


############################
## Read in neighborhood data
############################

filename = 'neighborhoods_data.csv'
raw_data = pd.read_csv(filename, header=0)

# map color of population is percentage black people
raw_data['bl_pop_color_1990'] = raw_data['1990 black'].values / raw_data['1990 population'].values
"""
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
"""
############################
## Interpolate data and change color
############################

max_income_1990 = raw_data['1990 income per capita'].max()
min_income_1990 = raw_data['1990 income per capita'].min()
mid_income_1990 = round((max_income_1990 + min_income_1990) / 2.0)

# normalize income data
raw_data['income_color_1990'] = (raw_data['1990 income per capita'].values - min_income_1990) / (max_income_1990 - min_income_1990)

# list of no data from income and demographic data
inc_names = []
dem_names = []


for name in data.index:

	# 1990 income mapping colors
	color_val = raw_data[raw_data.neighborhoods==name].income_color_1990.item()
	if color_val!=color_val: # nan does not equal itself
		print(name, color_val)
		color_val = 0
		inc_names.append(name)
	data.income_color_1990[data.index==name] = color_val

	# 1990 demographic mapping colors
	color_val = raw_data[raw_data.neighborhoods==name].bl_pop_color_1990.item()
	if color_val!=color_val: # nan does not equal itself
		print(name, color_val)
		color_val = 0
		dem_names.append(name)
	data.bl_pop_color_1990[data.index==name] = color_val

# make list of names with no data into numpy arrays for easier use
inc_names = np.array(inc_names)
dem_names = np.array(dem_names)

# copy shape dataframe of neighborhoods with no data
if len(inc_names) != 0:
	inc_no_data = gpd.GeoDataFrame(data, index=inc_names)
if len(dem_names) != 0:
	dem_no_data = gpd.GeoDataFrame(data, index=dem_names)

############################
## Plotting
############################

# create the income and demographic color maps
c_inc = plt.cm.ScalarMappable(cmap='Blues')
c_dem = plt.cm.ScalarMappable(cmap='Greys')

# create the subplot figure and axes
fig1, ax1 = plt.subplots(figsize=(14,12),ncols=2)

## 1990 demographic mapping
data.plot(column='bl_pop_color_1990',cmap='Greys', edgecolor='black', ax=ax1[0], legend=False)
parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[0])

# add no data red plot
if len(dem_names) != 0:
	dem_no_data.plot(color='r', edgecolor='black', ax=ax1[0])

# axes parameters and titles
ax1[0].set_axis_off()
ax1[0].title.set_text('% Black Population (1990)')
dem_bar = fig1.colorbar(c_dem, ax=ax1[0], shrink=0.5, ticks=[0.01,0.5,0.99])
dem_bar.ax.set_yticklabels(['0','50','100'])

# add Forest Park label
ct = parks_data.loc['Forest Park'].geometry.centroid
ax1[0].annotate('Forest Park', xy=(ct.x-4500, ct.y-700), rotation=-6)


## 1990 income mapping
data.plot(column='income_color_1990', cmap='Blues', edgecolor='black', ax=ax1[1], legend=False)
parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[1])

# add no data red plot
if len(inc_names) != 0:
	inc_no_data.plot(color='r', edgecolor='black', ax=ax1[1])

# axes parameters and titles
ax1[1].set_axis_off()
ax1[1].title.set_text('Income per Capita (1990)')
#inc_bar = fig1.colorbar(c_inc, ax=ax1[1], shrink=0.6, ticks=[0,0.5,1])
#inc_bar.ax.set_yticklabels(['$'+str(int(min_income_1990)),'$'+str(int(mid_income_1990)),'$'+str(int(max_income_1990))])
inc_bar = fig1.colorbar(c_inc, ax=ax1[1], shrink=0.5, ticks=[0.03,0.97])
inc_bar.ax.set_yticklabels(['Lower Income','Higher Income'])
inc_bar.ax.tick_params(size=0)


# add Forest Park label
ct = parks_data.loc['Forest Park'].geometry.centroid
ax1[1].annotate('Forest Park', xy=(ct.x-4500, ct.y-700), rotation=-6)

# add custom legend for parks and no data or zero population
custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='r', lw=10)]
ax1[1].legend(custom_lines, ['Parks', 'No data'], loc=4, frameon=False)

"""
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
"""
plt.show(block=False)
plt.pause(2)
plt.close()

# initialize time variant figure
fig2, ax2 = plt.subplots(figsize=(6,9))

# add parks data
parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax2)

# add Forest Park label
ct = parks_data.loc['Forest Park'].geometry.centroid
ax2.annotate('Forest Park', xy=(ct.x-4500, ct.y-700), rotation=-6)

# axes parameters and color bar
ax2.set_axis_off()
dem_bar = fig2.colorbar(c_dem, ax=ax2, shrink=0.5, ticks=[0.01,0.5,0.99])
dem_bar.ax.set_yticklabels(['0','50','100'])


years = ['1990','2000','2010']
for year in years:

	# build name with year
	name_color = 'bl_pop_color_' + year
	name_bl = year + ' black'
	name_pop = year + ' population'
	name_axis_title = '% Black Population (' + year + ')'


	# initialize colors for data and raw data
	data[name_color] = 'r'
	raw_data[name_color] = raw_data[name_bl].values / raw_data[name_pop].values

	dem_names = []

	for name in data.index:

		# demographic mapping colors
		color_val = raw_data[raw_data.neighborhoods==name][name_color].item()
		if color_val!=color_val: # nan does not equal itself
			print(name, color_val)
			color_val = 0
			dem_names.append(name)
		data[name_color][data.index==name] = color_val


	# make list of names with no data into numpy arrays for easier use
	dem_names = np.array(dem_names)

	# copy shape dataframe of neighborhoods with no data
	if len(dem_names) != 0:
		dem_no_data = gpd.GeoDataFrame(data, index=dem_names)


	## plot demographic data
	data.plot(column=name_color,cmap='Greys', edgecolor='black', ax=ax2, legend=False)

	# add no data red plot
	if len(dem_names) != 0:
		dem_no_data.plot(color='r', edgecolor='black', ax=ax2)

	# axis title
	ax2.title.set_text(name_axis_title)
	
	plt.show(block=False)
	plt.pause(1)

	# remove no data names list
	del dem_names


plt.pause(2)

plt.close()
"""

