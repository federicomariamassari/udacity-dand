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
the former must be used (all deprecation warnings are suppressed in the script).

References
-------------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity Data
     Analyst Nanodegree

Make new directory from script:
[2] https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-
    if-it-does-not-exist

Suppress matplotlib deprecation warnings:
[3] https://stackoverflow.com/questions/24502500/python-matplotlib-getting-rid-
    of-matplotlib-mpl-warning

Display files list and size:
[4] https://discussions.udacity.com/t/display-files-and-their-sizes-in-
    directory/186741/2
[5] https://stackoverflow.com/questions/10695139/sort-a-list-of-tuples-by-2nd-
    item-integer-value

Lombardy postcodes resources:
[6] http://www.tuttitalia.it/lombardia/
[7] https://en.wikipedia.org/wiki/Province_of_Monza_and_Brianza

Basemap toolkit resources:
[8] https://matplotlib.org/basemap/index.html
[9] http://basemaptutorial.readthedocs.io/en/latest/
[10] http://server.arcgisonline.com/arcgis/rest/services
'''

import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import seaborn as sns

# Make directory img to store output figures [2]
directory = './img'
if not os.path.exists(directory):
    os.makedirs(directory)

# Suppress matplotlib deprecation warnings from basemap 1.0.7 [3]
import warnings
import matplotlib.cbook
warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)

'''
A. REQUIRED QUERIES
-------------------------------------------------------------------------------

A.1 - Files Size (Python script)

This Python script, slightly modified from [4] and [5], prints both names and
size (in descending order) of all .csv, .db, and .osm files in the current
working directory.
'''
files_list = []

# The files are supposed to be in the same directory. Modify path otherwise
dirpath = '.'

for path, dirs, files in os.walk(dirpath):
        files_list.extend([(filename, os.path.getsize(os.path.join(path, \
                            filename))) for filename in files])

# Sort 'files_list' based on descending file size [5]
files_list =  sorted(files_list, key=lambda file: file[1], reverse=True)

print('\nA. REQUIRED QUERIES')
print('\nQUERY 1: Find the total size of all .csv, .db, and .osm files')
print(' '*9 + 'in the current working directory (Python script).\n')

# Add header to 'files_list' table
print('{:<42s}{}'.format('FILENAME','SIZE')), print('-'*51)

for filename, size in files_list:

    # Filter files to print based on extension, convert size to MB
    if filename.split('.')[-1] in ['csv', 'db', 'osm']:

        # Convert size to MB or kb (if file size smaller than 1 MB)
        if (size*1e-6 < 1) & (size*1e-3 >= 1):
            print('{:.<40s}: {:.2f} kB'.format(filename, size*1e-3))
        else:
            print('{:.<40s}: {:.2f} MB'.format(filename, size*1e-6))


# Create Connection object representing SQL database and Cursor
sqlite_database = 'milan_italy.db'
conn = sqlite3.connect(sqlite_database)
c = conn.cursor()

def execute_query(query):
    # Execute SQL query and return a list of fetched results (in string format)
    c.execute(query)
    return c.fetchall()

'''
A.2 - Number of unique users (modified from [1])
'''
unique = "SELECT count(DISTINCT e.{0}) AS num \
            FROM (SELECT nodes.{0} FROM nodes \
                UNION ALL \
                SELECT ways.{0} FROM ways) e;"

n_unique_users = execute_query(unique.format('user'))
n_unique_uids = execute_query(unique.format('uid'))

print('\n\nQUERY 2: Find the number of unique users.\n')
print("No. of unique users, 'user' tag: {}".format(n_unique_users[0][0]))
print("No. of unique users, 'uid' tag: {}".format(n_unique_uids[0][0]))

'''
If the results above are different, separately look for discrepancies in the
two tables 'nodes', 'ways'.
'''
if n_unique_users != n_unique_uids:
    print('\nIf the numbers above differ, find incongruous records:\n')

    discrepancies = "SELECT a.uid, b.uid, a.user, b.user \
                        FROM (SELECT uid, user FROM {0} GROUP BY uid) a, \
                            (SELECT uid, user FROM {0} GROUP BY user) b \
                        WHERE a.uid = b.uid AND a.user != b.user;"

    discrepancies_nodes = execute_query(discrepancies.format('nodes'))
    discrepancies_ways = execute_query(discrepancies.format('ways'))

    for table in [discrepancies_nodes, discrepancies_ways]:
        # Print all incongruous entries if the table is not empty
        if table != []:
            if table == discrepancies_nodes:
                print("Table: 'nodes'")
            else:
                print("Table: 'ways'")

            [print(entry) for entry in table]

            # Also print the total number of incongruous entries in the table
            print('count: {}'.format(len(table)))

'''
A.3 - Top 15 contributing users (taken from [1])
'''
top_contributing = "SELECT all_users.user, count(*) AS num \
                        FROM (SELECT user FROM nodes \
                                UNION ALL \
                                SELECT user FROM ways) all_users \
                        GROUP BY all_users.user \
                        ORDER BY num DESC \
                            LIMIT 15;"

top_15 = execute_query(top_contributing)

print('\n\nQUERY 3: Find the top 15 contributing users.\n')
print('{:<42s}{}'.format('USER','NO.')), print('-'*51)

for username, contributions in top_15:
    print('{:.<40s}: {}'.format(username, contributions))

'''
A.4 - Number of nodes and ways in the dataset [1]
'''
number_of_nodes = execute_query("SELECT count(*) FROM nodes;")
number_of_ways = execute_query("SELECT count(*) FROM ways;")

print('\n\nQUERY 4: Find the total number of nodes and ways.\n')
print('Number of nodes: {}'.format(number_of_nodes[0][0]))
print('Number of ways: {}'.format(number_of_ways[0][0]))

'''
B. ADDITIONAL STATISTICS
-------------------------------------------------------------------------------
'''
def street_map(query, diff, colors, labels, title, fig_name, query_args=None, \
                service='ESRI_StreetMap_World_2D'):
    '''
    Scatter plot OpenStreetMap data on top of a 2D world map.

    Input
    ---------------------------------------------------------------------------
    query: str, required argument. The SQL query to process. Must produce a
           table of coordinates of the form (longitude, latitude). May contain
           a pair of brackets {}, in which case list 'query_args' must also be
           supplied.
    diff: float, required argument. Parameter added to the max, or subtracted
          to the min, longitude and latitude values to zoom on the map, which
          is centered on the data.
    colors, labels: lists of str, required arguments. List of colors and labels
                    for the scatter plot.
    title: str, required argument. Title of the plot.
    fig_name: str, required argument. The name of the saved figure, without
              extension (default='png'). The figures are stored in directory
              'img', which is generated if not already present.
    query_args: list of str, optional argument. The variable part of the query
                to process. Only provide in case 'query' contains brackets {}.
    service: str, optional argument. The ArcGIS Server REST API used to get,
             and display as plot background, an area of the world map [10].
    '''

    '''
    If 'query_args' is supplied, build a list of full queries; otherwise, if
    'query' is self-contained, simply append 'query' to empty list 'full_query'.
    '''
    try:
        # Assign convenient name to frequently used iterable object
        n = range(len(query_args))

        '''
        Generate a list of full SQL queries, each one obtained by replacing
        the {} space in 'query' with a string element in 'query_args'.
        '''
        full_query = [query.format(query_args[i]) for i in n]

    except:
        n = range(1)
        full_query = []
        full_query.append(query)

    '''
    Store query results into NumPy arrays, convert string elements into
    floating point values (dtype=np.float).
    '''
    query_res = [np.array(execute_query(full_query[i]), dtype=np.float) \
                    for i in n]

    # Separately store longitudes (x-axis) and latitudes (y-axis)
    lons = [query_res[i][:,0] for i in n]
    lats = [query_res[i][:,1] for i in n]

    # Find the minimum and maximum longitude and latitude in the set
    concat_lons = np.concatenate([lons[i] for i in n])
    concat_lats = np.concatenate([lats[i] for i in n])
    min_lon, max_lon = concat_lons.min(), concat_lons.max()
    min_lat, max_lat = concat_lats.min(), concat_lats.max()

    plt.figure(figsize=(10,8))

    '''
    The matplotlib basemap toolkit is a library for plotting 2D data on maps in
    Python [8]. It allows to transform coordinates to map projections, so that
    matplotlib can then be used to plot on such transformed coordinates.
    The 'Basemap' class creates the map [9]; the boundaries are set by supplying
    minimum and maximum longitude (x-axis limits) and latitude (y-axis limits).
    The map is centered on the data to plot, using both the previously found
    minima and maxima, and parameter 'diff'.
    '''
    m = Basemap(llcrnrlon=min_lon-diff, llcrnrlat=min_lat-diff, \
                urcrnrlon=max_lon+diff, urcrnrlat=max_lat+diff, \
                resolution = 'h')

    '''
    Retrieve a background map using the ArcGIS Server REST API and display it
    on the plot. 'ESRI_StreetMap_World_2D' is the default map server.
    * Important: Internet connection required.
    '''
    m.arcgisimage(service=service, xpixels = 900)

    # Supply coordinates to the Basemap object
    x, y = m(lons, lats)

    # Make scatter plot of query results in the OSM file, divided by group
    scatterplot = [m.scatter(x[i], y[i], s=15, color=colors[i], \
                                label=labels[i]) for i in n]
    plt.title(title)
    plt.legend(handles=[scatterplot[i] for i in n], loc=1)

    # Store all pictures in subdirectory 'img'; set image quality with 'dpi'
    directory = './img'
    fig_name = fig_name
    plt.savefig('{}/{}.png'.format(directory, fig_name), dpi=150, \
                format='png', bbox_inches='tight')

'''
B.1 - Postal Codes

Admissible postcodes in the OSM file for Milan, Italy are [6]:

 20010 - 20099: Municipalities in the Metropolitan City of Milan area
 20121 - 20162: City of Milan
 20811 - 20900: Province of Monza and Brianza

The province of Monza and Brianza 'was officially created by splitting the
north-eastern part from the province of Milan [...] and became executive after
[...] June 2009' [7]. It is, therefore, quite common to find postcodes related
to such province in the OSM file. In the future, however, these should be
removed from the dataset.
'''

# Join tables 'nodes' and 'join_tags' to find coordinates of all postal codes
postcode_query = "SELECT nodes.lon, nodes.lat \
                    FROM nodes, (SELECT * FROM nodes_tags \
                                    UNION ALL \
                                    SELECT * FROM ways_tags) join_tags \
                    WHERE join_tags.id = nodes.id \
                        AND join_tags.key = 'postcode' \
                        AND {} \
                    ORDER BY join_tags.value;"

# Fill {} in the query above with the following strings using 'execute_query'
query_args = ["join_tags.value BETWEEN '20121' AND '20162'", \
              "join_tags.value BETWEEN '20010' AND '20099'", \
              "join_tags.value BETWEEN '20811' AND '20900'", \
              "(join_tags.value < '20010' OR join_tags.value > '20900')"]

pc_colors = ['royalblue', 'limegreen', 'darkorange', 'crimson']
pc_labels = ['City of Milan', 'Municipalities in the MCM area', \
            'Province of Monza and Brianza', 'Other Provinces']
pc_title = 'Map of postal codes in the OpenStreetMap sample file for Milan, \
Italy'

'''
Create a visual map of all postcodes in the OSM sample file for Milan, Italy.
Store the output figure in './img' folder, with name 'postcode.png'.
'''
street_map(postcode_query, 0.18, pc_colors, pc_labels, pc_title, 'postcode',\
            query_args)

'''

'''
postcode_by_province = "SELECT municipalities.postcode AS postcode, \
                                join_tags.value AS city_name, \
                                municipalities.province AS province \
                            FROM (SELECT * FROM nodes_tags \
                                    UNION ALL \
                                    SELECT * FROM ways_tags) join_tags, \
                                    municipalities \
                            WHERE join_tags.key='city' \
                                AND (postcode < 20010 OR postcode > 20900) \
                                AND city_name = municipalities.municipality \
                            GROUP BY city_name \
                            ORDER BY postcode;"

pbp = execute_query(postcode_by_province)

print('\n\nB. ADDITIONAL STATISTICS')
print('\nQUERY 1: Print postal code, municipality, and province for all')
print(' '*9 + 'the entries which should not belong in the Milan OSM file.\n')

print('{:<12s}{:<30}{}'.format('POSTCODE','MUNICIPALITY','PROVINCE'))
print('-'*51)
for postcode, municipality, province in pbp:
    print('{:<12}{:<30}{}'.format(postcode, municipality, province))

# Print total number of entries in the table
print('count: {}'.format(len(pbp)))

# Close the Connection object (i.e. the database)
conn.close()
