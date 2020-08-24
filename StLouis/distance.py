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

# calculate the great circle distance for distance on a sphere
def haversine(coord1, coord2):
	
	# radius of Earth in meters in St. Louis at 142 meters above sea level
	R = 6369988
	
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
	lon1, lat1 = coord1
	lon2, lat2 = coord2
    
	phi_1 = math.radians(lat1)
	phi_2 = math.radians(lat2)

	delta_phi = math.radians(lat2 - lat1)
	delta_lambda = math.radians(lon2 - lon1)

	a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

	dist = R * c  # output distance in meters
	return abs(dist)


stl_x = 38.6270
stl_y = 90.1994

ny_x = 40.7128
ny_y = 74.0060

dist = haversine((stl_x,stl_y),(ny_x,ny_y))

print('distance (km): ', dist/1000.)