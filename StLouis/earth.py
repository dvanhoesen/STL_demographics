import fiona 
import geopandas as gpd
import shapely
import matplotlib.pyplot as plt

# Enable fiona driver
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

#path = "1980_edits.kml"
#path = "1970_tracts.kml"
#path = "1950_edits.kml"
#path = "parks.kml"
#path = "1940_edits.kml"
#path = "2010_edits.kml"
#path = "2000_edits.kml"
#path = "1930_tracts.kml"
path = "1900_wards.kml"

# Read file
df = gpd.read_file(path, driver='KML')
    
# Drop Z dimension of polygons that occurs often in kml 
df.geometry = df.geometry.map(lambda polygon: shapely.ops.transform(lambda x, y, z: (x, y), polygon))


print(df.head(5))

df.plot()
plt.show()


# save dataframe as csv
df.to_csv('temp.csv')