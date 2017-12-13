'''
Use Python 3 to run this script.

THE BASEMAP TOOLKIT (v1.0.7)
-------------------------------------------------------------------------------
This script requires installation of the basemap toolkit, version 1.0.7.
The toolkit is available on PyPI (https://pypi.python.org/), and it can be
installed using conda on Command Prompt or Terminal:

 $ conda install basemap

The latest PyPI version, 1.0.7, raises several Matplotlib deprecation warnings;
however, the latest GitHub version, 1.1.0, is not fully compatible yet. Hence,
the former must be used.

References
-------------------------------------------------------------------------------
Display files list and size:
[1] https://discussions.udacity.com/t/display-files-and-their-sizes-in-
    directory/186741/2
[2] https://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-
    item-integer-value

Lombardy postcodes resources:
[3] http://www.tuttitalia.it/lombardia/
[4] https://en.wikipedia.org/wiki/Province_of_Monza_and_Brianza

Basemap toolkit resources:
[5] https://matplotlib.org/basemap/index.html
[6] http://basemaptutorial.readthedocs.io/en/latest/
[7] http://server.arcgisonline.com/arcgis/rest/services
'''

import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import seaborn as sns

'''
A. SIZE OF FILES
-------------------------------------------------------------------------------
This Python script, slightly modified from [1] and [2], prints both names and
size (in descending order) of all .csv, .db, and .osm files in the current
working directory.
'''
files_list = []

# The files are supposed to be in the same directory. Modify path otherwise
dirpath = '.'

for path, dirs, files in os.walk(dirpath):
        files_list.extend([(filename, os.path.getsize(os.path.join(path, \
                            filename))) for filename in files])

# Sort 'files_list' based on descending file size [2]
files_list =  sorted(files_list, key=lambda file: file[1], reverse=True)

print('FILENAME', ' '*32, 'SIZE'), print('-'*51)
for filename, size in files_list:

    # Filter files to print based on extension, convert size to MB
    if filename.split('.')[-1] in ['csv', 'db', 'osm']:
        print('{:.<40s}: {:.2f} MB'.format(filename, size*1e-6))




# Create Connection object representing SQL database and Cursor
sqlite_database = 'milan_italy.db'
conn = sqlite3.connect(sqlite_database)
c = conn.cursor()

'''
B. POSTAL CODES
-------------------------------------------------------------------------------
Admissible postcodes in the OSM file for Milan, Italy are [3]:

 20010 - 20099: Municipalities in the Metropolitan City of Milan area
 20121 - 20162: City of Milan
 20811 - 20900: Province of Monza and Brianza

The province of Monza and Brianza 'was officially created by splitting the
north-eastern part from the province of Milan [...] and became executive after
[...] June 2009' [4]. It is, therefore, quite common to find postcodes related
to such province in the OSM file. However, they should not belong in the map.
'''

# Join tables 'nodes' and 'nodes_tags' to find coordinates of all postal codes
postcode_query = "SELECT nodes.lon, nodes.lat \
FROM nodes_tags, nodes \
WHERE nodes_tags.id = nodes.id \
AND nodes_tags.key = 'postcode' AND {} \
ORDER BY nodes_tags.value;"

# Fill {} in the query above with the following strings using 'execute_query'
mcm_postcodes = postcode_query.format("nodes_tags.value BETWEEN '20010' \
AND '20099'")
milan_postcodes = postcode_query.format("nodes_tags.value BETWEEN '20121' \
AND '20162'")
mb_postcodes = postcode_query.format("nodes_tags.value BETWEEN '20811' \
AND '20900'")
out_postcodes = postcode_query.format("(nodes_tags.value < '20010' \
OR nodes_tags.value > '20900')")

def execute_query(query):
    # Execute SQL query and return a list of fetched results (in string format)
    c.execute(query)
    return c.fetchall()

'''
Store the results of the queries into NumPy arrays, convert string postcodes
into floating point values (dtype=np.float).
'''
mcm_postcode_map = np.array(execute_query(mcm_postcodes), dtype=np.float)
milan_postcode_map = np.array(execute_query(milan_postcodes), dtype=np.float)
mb_postcode_map = np.array(execute_query(mb_postcodes), dtype=np.float)
out_postcode_map = np.array(execute_query(out_postcodes), dtype=np.float)

# Separately store longitudes (x) and latitudes (y)
mcm_lons, mcm_lats = mcm_postcode_map[:,0], mcm_postcode_map[:,1]
milan_lons, milan_lats = milan_postcode_map[:,0], milan_postcode_map[:,1]
mb_lons, mb_lats = mb_postcode_map[:,0], mb_postcode_map[:,1]
out_lons, out_lats = out_postcode_map[:,0], out_postcode_map[:,1]

# Find approximate (proxy=out) minimum and maximum coordinates to center plot
min_lon, max_lon = np.min(out_lons), np.max(out_lons)
min_lat, max_lat = np.min(out_lats), np.max(out_lats)

# Vary the following parameter to zoom into the plot
diff = 0.18

plt.figure(figsize=(10,8))

'''
The matplotlib basemap toolkit is a library for plotting 2D data on maps in
Python [5]. It allows to transform coordinates to map projections, so that
matplotlib can then be used to plot on such transformed coordinates.
The 'Basemap' class creates the map [6]; the boundaries are set by supplying
minimum and maximum longitude (x-axis limits) and latitude (y-axis limits).
The map is centered on the data to plot.
'''
m = Basemap(llcrnrlon=min_lon-diff, llcrnrlat=min_lat-diff, \
            urcrnrlon=max_lon+diff, urcrnrlat=max_lat+diff, resolution = 'h')

'''
Retrieve an image using the ArcGIS Server REST API [7] and display it on map
Note: An internet connection is required.
'''
m.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 900, dpi=1500)

# Supply coordinates to the Basemap object
x_mcm, y_mcm = m(mcm_lons, mcm_lats)
x_milan, y_milan = m(milan_lons, milan_lats)
x_mb, y_mb = m(mb_lons, mb_lats)
x_out, y_out = m(out_lons, out_lats)

# Make scatter plot of postcodes in the OSM file, divided by group
mcm = m.scatter(x_mcm, y_mcm, s=25, color='black', \
                    label='Municipalities in the MCM area')
milan = m.scatter(x_milan, y_milan, s=25, color='royalblue', \
                    label='City of Milan')
mb = m.scatter(x_mb, y_mb, s=25, color='darkorange', \
                    label='Province of Monza and Brianza')
out = m.scatter(x_out, y_out, s=25, color='crimson', label='Other Provinces')

plt.title('Map of postal codes for the Metropolitan City of Milan, Italy, \
OpenStreetMap')
plt.legend(handles=[milan, mcm, mb, out], loc=1)
plt.show()

# Close the Connection object (i.e. the database)
conn.close()
