# Daniel Van Hoesen
# St. Louis Neighborhoods and tracts
# created 7/21/2020
# display neighborhoods and tracts with overlay color for income or demographic
# inerpolate data to get a smooth video


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
import math
#import sys


############################
## Functions
############################


############################
## Main
############################

# read in the boundaries of the small boxes
boxes_file = 'boundaries300.csv'
boxes_csv = pd.read_csv(boxes_file)
boxes_data = gpd.GeoDataFrame(boxes_csv)
boxes_data.set_index("boundaries", inplace=True)
boxes_data['geometry'] = boxes_data['geometry'].apply(wkt.loads)
boxes_data.set_geometry('geometry')
boxes_data['color'] = 0.0
boxes_data['color2'] = 0.0
boxes_data['color3'] = 0.0  # intermediate steps

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
fig1, ax1 = plt.subplots(figsize=(14,12), ncols=2)

# demographic axes parameters and color bar
dem_bar = fig1.colorbar(c_dem, ax=ax1[0], shrink=0.5, ticks=[0.01,0.5,0.99])
dem_bar.ax.set_yticklabels(['0','50','100'])

# add a label to the figure
plt.gcf().text(0.20,0.8, '% Population White', fontsize=12)

# St. Louis boundary data
stl_file = 'stl_boundary.csv'
stl_csv = pd.read_csv(stl_file)
stl_data = gpd.GeoDataFrame(stl_csv)
stl_data.set_index("Name", inplace=True)
stl_data['geometry'] = stl_data['geometry'].apply(wkt.loads)
stl_data.set_geometry('geometry')

# years to show for mapping (2018 twice b/c last and want to show Delmar divide)
years = ['1930','1940','1950','1960','1970','1980','1990','2000',
			'2010','2011','2012','2013','2014','2015','2016','2017','2018']

#years = ['1940','1950','1960']

pause_time = 0.2
save_frames = True
interpolate = True
years_count = 0
vid_count = 0

# demographic variables
dem_color = 'dem_color'
name_dem = 'white'
name_pop = 'population'


for year in years:

	# if the year is not the first year, then clear the plot contents
	if year != years[0]:
		ax1[0].cla()
		ax1[1].cla()

		# clear data from memory and replace with data2
		del data
		data = data2.copy(deep=True)
		del data2

		# copy the box data from the next year
		# instead of copying the data, just rename the columns and delete the old one
		boxes_data = boxes_data.drop(['color', 'color3'], axis=1)
		boxes_data = boxes_data.rename(columns={'color2': 'color'})
		boxes_data['color2'] = 0.0
		boxes_data['color3'] = 0.0


	else: 
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

		# initialize demographic colors by normalizing by population
		data[dem_color] = data[name_dem].values / data[name_pop].values

		previous_val = 0.0
		for bind in boxes_data.index:

			# calculate center of box and assign its value to the tract it is in
			center = boxes_data.loc[bind].geometry.centroid
			inside_tf = np.array(data.loc[data.geometry.contains(center), dem_color])
			
			if len(inside_tf)==0:
				color_val = previous_val
			
			else:
				color_val = np.average(inside_tf)			
			
			boxes_data.loc[bind, 'color'] = color_val
			previous_val = color_val

	# add Forest Park label
	ct = parks_data.loc['Forest Park'].geometry.centroid
	ax1[0].annotate('Forest Park', xy=(ct.x, ct.y), rotation=-6, size=9, va='center', ha='center')

	# turn off axis
	ax1[0].set_axis_off()
	ax1[1].set_axis_off()

	## plot demographic data
	boxes_data.plot(column='color',cmap='gray', ax=ax1[0], legend=False, edgecolor='face', linewidth=0.05)

	# add parks data
	parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[0], linewidth=1)

	# add St. Louis boundary
	stl_data.geometry.boundary.plot(color=None, edgecolor='black', ax=ax1[0], linewidth=1.2)

	# add annotation as a legend for data source
	data_source = 'Data Source: U.S. Census'
	if int(year) > 2009:
		data_source = 'Data Source: American Community Survey'

	fake_line = Line2D([0], [0], color='white', lw=1)
	ax1[0].legend([fake_line], [data_source], loc=3, bbox_to_anchor=(-0.3,-0.023), frameon=False)

	# add custom legend for parks and no data or zero population
	#custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10), Line2D([0], [0], color='r', lw=10)]
	#ax1[1].legend(custom_lines, ['Parks', 'Mississippi River', 'No data'], loc=3, bbox_to_anchor=(-0.6,-0.05), frameon=False)

	custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10)]
	ax1[1].legend(custom_lines, ['Parks', 'Mississippi River'], loc=3, bbox_to_anchor=(-0.6,-0.05), frameon=False)

	# year as figure title
	fig1.suptitle(year, x=0.5, y=0.9, fontsize=18)
	
	# pause for viewing
	plt.show(block=False)
	plt.pause(pause_time)

	# save the images by increasing the name by one for each frame
	if save_frames:
		vid_count = vid_count + 1
		vid_num = str(vid_count).zfill(5)
		savename = 'video/' + vid_num + '.png'
		plt.savefig(savename, dpi=100)
	

	# if last, then add arrow and text to show Delmar divide
	if year == years[-1]:
		ax1[0].annotate('Delmar Blvd', fontsize=12,
			xy=(0.26, 0.51), xycoords='axes fraction', xytext=(0.12,0.63),
			arrowprops=dict(facecolor='red', shrink=0, lw=0.8),
			horizontalalignment='right', verticalalignment='top')
			
		# add Delmar Blvd in bold red
		delmar_df.plot(color='red', edgecolor='red', ax=ax1[0], linewidth=4)

		plt.show(block=False)
		plt.pause(pause_time)

		# save the images by increasing the name by one for each frame
		if save_frames:
			vid_count = vid_count + 1
			vid_num = str(vid_count).zfill(5)
			savename = 'video/' + vid_num + '.png'
			plt.savefig(savename, dpi=100)

	if year!=years[-1] and interpolate==True:

		year2 = years[years_count+1]
		data_file2 = year2 + '_data.csv'

		# data 2010 to 2018 are ACS (American Community Survey) estimates 
		if int(year2) > 2009:
			data_file2 = year2 + '_data_ACS_estimates.csv'

		
		data_csv2 = pd.read_csv(data_file2)
		data2 = gpd.GeoDataFrame(data_csv2)

		# set the tracts as the index
		data2.set_index("tract", inplace=True)

		# set the geometry column to the geometry
		data2['geometry'] = data2['geometry'].apply(wkt.loads)
		data2 = data2.set_geometry('geometry')

		# initialize demographic colors by normalizing by population
		data2[dem_color] = data2[name_dem].values / data2[name_pop].values


		previous_val = 0.0
		for bind in boxes_data.index:

			# calculate center of box and assign its value to the tract it is in
			center = boxes_data.loc[bind].geometry.centroid
			inside_tf = np.array(data2.loc[data2.geometry.contains(center), dem_color])

			if len(inside_tf)==0:
				color_val = previous_val

			else:
				color_val = np.average(inside_tf)

			boxes_data.loc[bind, 'color2'] = color_val
			previous_val = color_val


		# calculating the intermediate steps and plotting them
		num_steps = 200
		if int(year) > 2009:
			num_steps = int(num_steps/10)

		year_diff = float(int(year2)-int(year))
		time_diff = year_diff / (num_steps+1)

		for s in range(num_steps):

			#clear the axis
			ax1[0].cla()
			ax1[1].cla()

			t = (s + 1.0)*time_diff
			slope = (boxes_data['color2'].values - boxes_data['color'].values) / year_diff
			boxes_data['color3'] = slope*t + boxes_data['color'].values

			# add Forest Park label
			ct = parks_data.loc['Forest Park'].geometry.centroid
			ax1[0].annotate('Forest Park', xy=(ct.x, ct.y), rotation=-6, size=9, va='center', ha='center')

			# turn off axis
			ax1[0].set_axis_off()
			ax1[1].set_axis_off()

			## plot demographic data
			boxes_data.plot(column='color3',cmap='gray', ax=ax1[0], legend=False, edgecolor='face', linewidth=0.05)

			# add parks data
			parks_data.plot(color=parks_data.color, edgecolor='black', ax=ax1[0], linewidth=1)

			# add St. Louis boundary
			stl_data.geometry.boundary.plot(color=None, edgecolor='black', ax=ax1[0], linewidth=1.2)
			
			# add annotation as a legend for data source
			fake_line = Line2D([0], [0], color='white', lw=1)
			ax1[0].legend([fake_line], [data_source], loc=3, bbox_to_anchor=(-0.3,-0.023), frameon=False)

			# add custom legend for parks and no data or zero population
			#custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10), Line2D([0], [0], color='r', lw=10)]
			#ax1[1].legend(custom_lines, ['Parks', 'Mississippi River', 'No data'], loc=3, bbox_to_anchor=(-0.6,-0.05), frameon=False)
			custom_lines = [Line2D([0], [0], color='g', lw=10), Line2D([0], [0], color='blue', lw=10)]
			ax1[1].legend(custom_lines, ['Parks', 'Mississippi River'], loc=3, bbox_to_anchor=(-0.6,-0.05), frameon=False)

			# year as figure title
			fig1.suptitle(year, x=0.5, y=0.9, fontsize=18)
	
			# pause for viewing
			plt.show(block=False)
			plt.pause(pause_time)

			# save the images by increasing the name by one for each frame
			if save_frames:
				vid_count = vid_count + 1
				vid_num = str(vid_count).zfill(5)
				savename = 'video/' + vid_num + '.png'
				plt.savefig(savename, dpi=100)
			


	years_count = years_count + 1


#plt.show()
plt.pause(2)
plt.close()


#### String together as video using ffmpeg
# ffmpeg -r 2 -f image2 -s 1400x1200 -start_number 3 -i STLouis_%05d.png -vframes 16 -vcodec libx264 -crf 15 -pix_fmt yuv420p out.mp4

# 10 fps from image 1
# ffmpeg -r 10 -f image2 -s 1400x1200 -start_number 1 -i %05d.png -vframes 178 -vcodec libx264 -crf 15 -pix_fmt yuv420p out.mp4
