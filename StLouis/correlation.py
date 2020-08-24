# Daniel Van Hoesen
# St. Louis Neighborhoods and tracts
# display neighborhoods and tracts with overlay color for income or demographic

# created 6/23/2020

# 1940 pdf

# 1950 pdf

# 1960 pdf 

# 1970 pdf

# 1980
# https://archive.org/details/1980censusofpo8023131unse/page/386/mode/2up

# 1990 tract numbers
# https://www2.census.gov/geo/maps/trt1990/st29_Missouri/29510_StLouis/

# 1990 to 2010
# https://www.stlouis-mo.gov/data/tags/tag.cfm?id=1
# http://dynamic.stlouis-mo.gov/census/neigh_comp.cfm

############################
## Imports
############################

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shapely import wkt
import csv
import numpy as np


############################
## Functions
############################


############################
## Main
############################

# read in parks data file
parks_data_file = 'parks_data.csv'

parks_data_csv = pd.read_csv(parks_data_file)
parks_data = gpd.GeoDataFrame(parks_data_csv)

# set the names as the index
parks_data.set_index("name", inplace=True)

# set the geometry column to the geometry
parks_data['geometry'] = parks_data['geometry'].apply(wkt.loads)
parks_data.set_geometry('geometry')

# change the extra data colors
parks_data['color'] = 'green'
parks_data.loc['river'].color = 'blue'

# create the income and demographic color bar mapping
c_cor = plt.cm.ScalarMappable(cmap='Greys')

# initialize time variant figure
fig1, ax1 = plt.subplots(figsize=(7,12),ncols=1)

# axes parameters and color bar
ax1.set_axis_off()
cor_bar = fig1.colorbar(c_cor, ax=ax1, shrink=0.5, ticks=[0.03,0.97])
cor_bar.ax.set_yticklabels(['Low Correlation','High Correlation'])

# set the color bar labels
#plt.gcf().text(0.21,0.8, '% People of Color', fontsize=12)


years = ['1940','1950','1960','1970','1980','2010','2011','2012','2013','2014','2015','2016','2017','2018']
for year in years:

	# read in the data file
	data_file = year + '_data.csv'

	# data 2010 to 2018 are ACS (American Community Survey) estimates 
	if int(year) > 2009:
		data_file = year + '_data_ACS_estimates.csv'

	data_csv = pd.read_csv(data_file)
	data = gpd.GeoDataFrame(data_csv)

	# set the tracts as the index
	data.set_index("tract", inplace=True)

	# set the geometry column to the geometry
	data['geometry'] = data['geometry'].apply(wkt.loads)
	data = data.set_geometry('geometry')

	# demographic variables
	dem_color = 'dem_color'
	name_poc = 'people of color'
	name_pop = 'population'

	# median income variables
	inc_color = 'inc_color'
	name_inc = 'median income per household'

	# correlation variables
	cor_color = 'cor_color'

	# initialize demogaphric colors by normalizing by population
	data[dem_color] = data[name_poc].values / data[name_pop].values

	# determine income colors and finding missing data
	max_inc = data[name_inc].max()
	min_inc = data[name_inc].min()

	# normalize income data
	data[inc_color] = (data[name_inc].values - min_inc) / (max_inc - min_inc)

	# check for missing data or zeros
	inc_names = []

	for name in data.index:
		color_val = data.loc[name][inc_color].item()
		if color_val!=color_val: # nan does not equal itself
			print(year, name, color_val)
			color_val = 0
			inc_names.append(name)
		data.at[name, inc_color] = color_val

	# demographic color and income color is normalized between 0 and 1
	# dem_color: 1 is 100% of people of color
	# inc_color: 1 is high income

	data[cor_color] = np.abs(data[dem_color]-data[inc_color])

	# make list of names with no data into numpy arrays for easier use
	inc_names = np.array(inc_names)

	# copy shape dataframe of neighborhoods with no data
	if len(inc_names) != 0:
		inc_no_data = gpd.GeoDataFrame(data, index=inc_names)


	## plot correlation data
	data.plot(column=cor_color,cmap='Greys', edgecolor='black', ax=ax1, legend=False)

	# add no data red plot
	if len(inc_names) != 0:
		inc_no_data.plot(color='r', edgecolor='black', ax=ax1)

	
	# add parks data
	parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1, linewidth=1)

	# add Forest Park label
	ct = parks_data.loc['Forest Park'].geometry.centroid
	ax1.annotate('Forest Park', xy=(ct.x, ct.y), rotation=-6, size=9, va='center', ha='center')

	# add annotation as a legend for data source
	data_source = 'Data Source: U.S. Census'
	if int(year) > 2009:
		data_source = 'Data Source: American Community Survey'

	fake_line = Line2D([0], [0], color='white', lw=1)
	ax1.legend([fake_line], [data_source], loc=3, bbox_to_anchor=(0.70,-0.05), frameon=False)


	# add custom legend for parks and no data or zero population
	custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10), Line2D([0], [0], color='r', lw=10)]
	ax1.legend(custom_lines, ['Parks', 'Mississippi River', 'No data'], loc=4, frameon=False)

	# year as figure title
	fig1.suptitle(year, x=0.5, y=0.9, fontsize=18)
	
	# pause for viewing
	plt.show(block=False)
	plt.pause(1)

#plt.show()
plt.pause(3)
plt.close()

