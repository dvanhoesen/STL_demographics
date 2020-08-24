# Daniel Van Hoesen
# St. Louis Neighborhoods and tracts
# created 6/23/2020
# display neighborhoods and tracts with overlay color for income or demographic


# data

# pdf: 1940, 1950, 1960, 1970

# 1980
# https://archive.org/details/1980censusofpo8023131unse/page/386/mode/2up

# 1990 and 2000 
# https://www2.census.gov/geo/maps/trt1990/st29_Missouri/29510_StLouis/
# http://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.dp3_2kt.sas&state=29&county=510&tract=1011.00

# 2000 to 2018
# data.census.gov
# geography > tracts > Missouri > St. Louis City

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
parks_data.loc['Delmar'].color = 'red'

# take out Delmar and place in at end
delmar_df = parks_data.loc[['Delmar'],:].copy()
parks_data = parks_data.drop('Delmar')

# create the income and demographic color bar mapping
c_dem = plt.cm.ScalarMappable(cmap='gray')
c_inc = plt.cm.ScalarMappable(cmap='gray')

# initialize time variant figure
fig1, ax1 = plt.subplots(figsize=(14,12),ncols=2)

# demographic axes parameters and color bar
ax1[0].set_axis_off()
dem_bar = fig1.colorbar(c_dem, ax=ax1[0], shrink=0.5, ticks=[0.01,0.5,0.99])
dem_bar.ax.set_yticklabels(['0','50','100'])

# income axes parameters and color bar
ax1[1].set_axis_off()
inc_bar = fig1.colorbar(c_inc, ax=ax1[1], shrink=0.5, ticks=[0.03,0.97])
inc_bar.ax.set_yticklabels(['Lower Income','Higher Income'])

# set the color bar labels
plt.gcf().text(0.20,0.8, '% Population White', fontsize=12)
plt.gcf().text(0.6,0.8, 'Income per Household', fontsize=12)

# add Forest Park label
ct = parks_data.loc['Forest Park'].geometry.centroid
ax1[0].annotate('Forest Park', xy=(ct.x, ct.y), rotation=-6, size=9, va='center', ha='center')
ax1[1].annotate('Forest Park', xy=(ct.x, ct.y), rotation=-6, size=9, va='center', ha='center')

# years to show for mapping (2018 twice b/c last and want to show Delmar divide)
years = ['1900','1930','1940','1950','1960','1970','1980', '1990','2000',
		'2010','2011','2012','2013','2014','2015','2016','2017','2018','2018']

count = 0
vid_count = 0
for year in years:

	# demographic variables
	dem_color = 'dem_color'
	name_dem = 'white'
	name_pop = 'population'

	# median income variables
	inc_color = 'inc_color'
	name_inc = 'median income per household'

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

	# initialize demogaphric colors by normalizing by population
	data[dem_color] = data[name_dem].values / data[name_pop].values

	""" Us this if name_inc = 'income per capita'
	# calculate income per capita from mean income per household and people per household
	if int(year) > 2009:
		data[name_inc] = data['mean income per household'].values / data['people per household'].values

	# calculate income per capita from median income per household and people per household (no mean values)
	if year=='1950' or year=='1960':
		data[name_inc] = data['median income per household'].values / data['people per household'].values
	"""

	# determine income colors and finding missing data

	"""
	# determine four highest and lowest values to make outliers less prominent in color scheme
	four_high = data[name_inc].nlargest(4)
	four_low = data[name_inc].nsmallest(4)

	max_inc = four_high.min()
	min_inc = four_low.max()
	"""

	# apply function to distinguish colors easier by reducing significance of outliers if necessary
	#data[name_inc] = np.log(data[name_inc])

	max_inc = data[name_inc].max()
	min_inc = data[name_inc].min()

	# normalize income data
	data[inc_color] = (data[name_inc].values - min_inc) / (max_inc - min_inc)

	# if value greater than 1 change to 1 (only necessary if normalizing by non largest number)
	#data[inc_color].loc[data[inc_color]>1] = 1.0

	# if value less than 0 change to 0 (only necessary if normalizing by non smallest number)
	#data[inc_color].loc[data[inc_color]<0] = 0.0

	# check for missing data or zeros
	inc_names = []

	for name in data.index:
		color_val = data.loc[name][inc_color].item()
		if color_val!=color_val: # nan does not equal itself
			#print(year, name, color_val)
			color_val = 0
			inc_names.append(name)
		data.at[name, inc_color] = color_val

	# make list of names with no data into numpy arrays for easier use
	inc_names = np.array(inc_names)

	## plot demographic data
	data.plot(column=dem_color,cmap='gray', edgecolor='black', ax=ax1[0], legend=False)

	## plot income data
	data.plot(column=inc_color,cmap='gray', edgecolor='black', ax=ax1[1], legend=False)


	# copy shape dataframe of neighborhoods with no data and add to plot
	if len(inc_names) != 0:
		inc_no_data = gpd.GeoDataFrame(data, index=inc_names)
		inc_no_data.plot(color='r', edgecolor='black', ax=ax1[1])

	
	# add parks data
	parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[0], linewidth=1)
	parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[1], linewidth=1)


	# add annotation as a legend for data source
	data_source = 'Data Source: U.S. Census'
	if int(year) > 2009:
		data_source = 'Data Source: American Community Survey'

	fake_line = Line2D([0], [0], color='white', lw=1)
	ax1[0].legend([fake_line], [data_source], loc=3, bbox_to_anchor=(0.70,-0.05), frameon=False)

	# add custom legend for parks and no data or zero population
	custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10), Line2D([0], [0], color='r', lw=10)]
	ax1[1].legend(custom_lines, ['Parks', 'Mississippi River', 'No data'], loc=4, frameon=False)

	# if last, then add arrow and text to show Delmar divide
	if year == '2018':
		count = count + 1
		if count == 2:
			ax1[0].annotate('Delmar Blvd', fontsize=12,
				xy=(0.26, 0.51), xycoords='axes fraction', xytext=(0.12,0.63),
				arrowprops=dict(facecolor='red', shrink=0, lw=0.8),
				horizontalalignment='right', verticalalignment='top')
			
			# add Delmar Blvd in bold red
			delmar_df.plot(color='red', edgecolor='red', ax=ax1[0], linewidth=4)
			delmar_df.plot(color='red', edgecolor='red', ax=ax1[1], linewidth=4)


	# year as figure title
	fig1.suptitle(year, x=0.5, y=0.9, fontsize=18)
	
	# pause for viewing
	plt.show(block=False)
	plt.pause(1)

	# save the images by increasing the name by one for each frame
	"""
	vid_count = vid_count + 1
	vid_num = str(vid_count).zfill(5)
	savename = 'video/STLouis_' + vid_num + '.png'
	plt.savefig(savename, dpi=100)
	"""

#plt.show()
plt.pause(5)
plt.close()


#### String together as video using ffmpeg
# ffmpeg -r 2 -f image2 -s 1400x1200 -start_number 3 -i STLouis_%05d.png -vframes 16 -vcodec libx264 -crf 15 -pix_fmt yuv420p out.mp4

# for timelaps video at 10 fps
# ffmpeg -r 10 -f image2 -s 1920x1080 -start_number 1 -i  %05d.png -vframes 219 -vcodec libx264 -crf 15 -pix_fmt yuv420p out.mp4
