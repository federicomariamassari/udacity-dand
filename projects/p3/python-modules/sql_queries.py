"""Provide a statistical overview of the dataset using SQL queries.

Note: Use Python 3 to run this script.

Required installation: THE BASEMAP TOOLKIT (v1.0.7)
-------------------------------------------------------------------------------
This script requires installation of the basemap toolkit, version 1.0.7.
The toolkit is available on PyPI (https://pypi.python.org/), and it can be
installed using conda on Command Prompt or Terminal:

 $ conda install basemap

The latest PyPI version, 1.0.7, raises several Matplotlib deprecation warnings;
however, the latest GitHub version, 1.1.0, is not fully compatible yet. Hence,
the former must be used (all deprecation warnings are suppressed in the script).

* Module 6 of 6

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

Custom 'ORDER BY' statement:
[6] https://stackoverflow.com/questions/3303851/sqlite-and-custom-order-by

Basemap toolkit resources:
[7] http://server.arcgisonline.com/arcgis/rest/services
[8] https://matplotlib.org/basemap/index.html
[9] http://basemaptutorial.readthedocs.io/en/latest/

Print dots while waiting:
[10] https://mail.python.org/pipermail/python-list/2008-January/509830.html

Lombardy postcodes resources:
[11] http://www.tuttitalia.it/lombardia/
[12] https://en.wikipedia.org/wiki/Province_of_Monza_and_Brianza

2017 - Federico Maria Massari / federico.massari@bocconialumni.it
"""

import os
import time
import sys
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import seaborn as sns

# Time script execution
tic = time.time()

"""Make directory img to store output figures [2] if not already present.
If so, set flag = 0, whith 'flag' a variable used when saving maps to file.
"""
directory = './img'
flag = -1
if not os.path.exists(directory):
    os.makedirs(directory)
    flag += 1

# Suppress matplotlib deprecation warnings from basemap 1.0.7 [3]
import warnings
import matplotlib.cbook
warnings.filterwarnings('ignore', category=matplotlib.cbook.mplDeprecation)

"""A. REQUIRED QUERIES
-------------------------------------------------------------------------------

A.1 - Size of files in the current working directory (Python script)

This Python script, slightly modified from [4] and [5], prints both names and
size (in descending order) of all .csv, .db, and .osm files in the current
working directory.
"""
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
print('{:<42s}{}'.format('FILENAME','SIZE')), print('-' * 51)

for filename, size in files_list:

    # Filter files to print based on extension, convert size to MB
    if filename.split('.')[-1] in ['csv', 'db', 'osm']:

        # Convert size to MB or kb (if file size smaller than 1 MB)
        if (size * 1e-6 < 1) & (size * 1e-3 >= 1):
            print('{:.<40s}: {:.2f} kB'.format(filename, size * 1e-3))
        else:
            print('{:.<40s}: {:.2f} MB'.format(filename, size * 1e-6))

# Create Connection object representing SQL database and Cursor
sqlite_database = 'milan_italy.db'
conn = sqlite3.connect(sqlite_database)
c = conn.cursor()

def execute_query(query):
    """Execute SQL query and return a list of fetched results as strings."""
    c.execute(query)
    return c.fetchall()

"""A.2 - Number of unique users (modified from [1])
"""
unique = "SELECT count(DISTINCT e.{0}) AS num \
            FROM (SELECT nodes.{0} FROM nodes \
                UNION ALL \
                SELECT ways.{0} FROM ways) e;"

n_unique_users = execute_query(unique.format('user'))
n_unique_uids = execute_query(unique.format('uid'))

print('\n\nQUERY 2: Find the number of unique users.\n')
print("No. of unique users, 'user' tag: {}".format(n_unique_users[0][0]))
print("No. of unique users, 'uid' tag: {}".format(n_unique_uids[0][0]))

"""If the results above are different, separately look for discrepancies in the
two tables 'nodes', 'ways'.
"""
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

"""A.3 - Top 15 contributing users (taken from [1])
"""
top_contributing = "SELECT all_users.user, count(*) AS num \
                        FROM (SELECT user FROM nodes \
                                UNION ALL \
                                SELECT user FROM ways) all_users \
                        GROUP BY all_users.user \
                        ORDER BY num DESC \
                            LIMIT 15;"

top_15 = execute_query(top_contributing)

print('\n\nQUERY 3: Find the top 15 contributing users.\n')
print('{:<42s}{}'.format('USER','NO.')), print('-' * 51)

for username, contributions in top_15:
    print('{:.<40s}: {}'.format(username, contributions))

"""A.4 - Number of nodes and ways in the dataset [1]
"""
number_of_nodes = execute_query("SELECT count(*) FROM nodes;")
number_of_ways = execute_query("SELECT count(*) FROM ways;")

print('\n\nQUERY 4: Find the total number of nodes and ways.\n')
print('Number of nodes: {}'.format(number_of_nodes[0][0]))
print('Number of ways: {}'.format(number_of_ways[0][0]))

"""A.5 - Number of educational establishments by level

Find all kindergartens (age: 0-4), schools (5-18), universities, and colleges.
'university' refers to institutions of higher education, 'college' for further
education. In the query, include both key tags 'amenity', 'building'. Despite
some overlapping, the result is more reasonable than with 'amenity' alone.
"""

"""Auxiliary SQL query string: join tables 'nodes_tags', 'ways_tags' and name
the output 'join_tags'. Factor out as it is frequently used and to make queries
more readable. Every time {join_tags} appears in a query, replace it with this
string.
"""
join_tags = '(SELECT * FROM nodes_tags \
                UNION ALL \
                SELECT * FROM ways_tags) join_tags'

# Use custom 'ORDER BY' statement [6]
schools = "SELECT value, count(*) \
            FROM {join_tags} \
            WHERE join_tags.value \
                IN ('kindergarten', 'school', 'university', 'college') \
            GROUP BY value \
            ORDER BY \
                CASE value \
                    WHEN 'kindergarden' THEN 0 \
                    WHEN 'school' THEN 1 \
                    WHEN 'university' THEN 2 \
                    WHEN 'college' THEN 3 \
                END;".format(join_tags=join_tags)

school_by_type = execute_query(schools)

print('\n\nQUERY 5: Find the number of educational establishments by level.\n')
print('{:<42s}{}'.format('ESTABLISHMENT','COUNT')), print('-' * 51)

for establishment, count_school in school_by_type:
    print('{:.<40s}: {}'.format(establishment, count_school))

"""A.6 - Number of 'fixme' tags

Count the number of 'fixme' key, value, and type tags. Use LIKE '%fixme' to
cover all possible cases: 1) key='fixme'; 2) key='note', value='FIXME'; 3)
key='note', value='FIXME: ...'. '%<text>' finds any value starting with <text>.
"""
fixme = "SELECT count(*) \
            FROM {join_tags} \
            WHERE join_tags.key LIKE '%fixme' \
                OR join_tags.value LIKE '%fixme' \
                OR join_tags.type LIKE '%fixme';".format(join_tags=join_tags)

number_of_fixme_tags = execute_query(fixme)

print('\n\nQUERY 6: Find the number of tags that require fixing.\n')
print("Number of 'fixme' tags: {}".format(number_of_fixme_tags[0][0]))

"""B. ADDITIONAL STATISTICS
-------------------------------------------------------------------------------
"""
def street_map(query, query_constr, diff, colors, labels, title, fig_name, \
                query_keys=None, join_tags=join_tags, \
                service='ESRI_StreetMap_World_2D'):
    """Scatter plot OpenStreetMap data on top of a 2D world map.

    Arguments:
        query -- str. The SQL query to process. Must produce a table of
            coordinates (longitude, latitude). Must contain a pair of brackets
            {}, in which case list 'query_constr' must also be provided. If an
            additional pair of brackets is present, also supply 'query_keys'.
        query_constr -- list of str. The list of constraints on tag values.
        diff -- float. Parameter added to the max, or subtracted to the min,
            longitude and latitude values to zoom on the map, which is centered
            on the data.
        colors, labels -- lists of str. List of colors and labels for the
            scatter plot.
        title -- str. Title of the plot.
        fig_name -- str. The name of the saved figure, without extension
        (default 'png'). The figures are stored in directory 'img', which is
        generated if not already present.

    Keyword arguments:
        query_keys -- list of str. List of constraints on tag keys.
        join_tags -- str. Auxiliary SQL query string.
        service -- str. The ArcGIS Server REST API used to get, and display as
            plot background, an area of the world map [7].

    Returns:
        plt_flag -- A flag used to notify the user whenever map creation is
            successful (i.e., there is at least one mark to plot).
        A png figure (2D world map with scattered OSM data) available in the
        'img' folder, if applicable.
    """

    # Assign convenient name to frequently used iterable object
    n = range(len(query_constr))

    # Use this flag to notify user when a picture is saved in './img' folder
    plt_flag = -1

    """Generate a list of full SQL queries, each one obtained by replacing the
    {} brackets in the supplied query with the string element in 'query_constr'
    (and 'query_keys', if applicable).
    """
    if query_keys != None:
        full_query = [query.format(query_keys[i], query_constr[i], \
                        join_tags=join_tags) for i in n]

    else:
        full_query = [query.format(query_constr[i], join_tags=join_tags) \
                        for i in n]

    """Store query results into NumPy arrays, convert string elements into
    floating point values (dtype=np.float).
    """
    query_res = [np.array(execute_query(full_query[i]), dtype=np.float) \
                    for i in n]

    # Separately store longitudes (x-axis) and latitudes (y-axis)
    lons, lats = [], []

    # Continue in case one or more list pairs are empty
    for i in n:
        try:
            lons.append(query_res[i][:, 0])
            lats.append(query_res[i][:, 1])
        except:
            pass

    # Check that list length is still equal to n; shorten otherwise
    if range(len(lons)) != n:
        n = range(len(lons))

    """If lons, lats are not empty, find the minimum and maximum longitude and
    latitude in the set, then plot the data using basemap. Otherwise, pass.
    """
    try:
        concat_lons = np.concatenate([lons[i] for i in n])
        concat_lats = np.concatenate([lats[i] for i in n])
        min_lon, max_lon = concat_lons.min(), concat_lons.max()
        min_lat, max_lat = concat_lats.min(), concat_lats.max()

        plt.figure(figsize=(10, 8))

        """The matplotlib basemap toolkit is a library for plotting 2D data on
        maps in Python [8]. It allows to transform coordinates to map projec-
        tions so that matplotlib can then be used to plot on such transformed
        coordinates. The 'Basemap' class creates the map [9]; the boundaries
        are set by supplying minimum and maximum longitude (x-axis limits) and
        latitude (y-axis limits). The map is centered on the data to plot,
        using both the previously found minima and maxima, and parameter 'diff'.
        """
        m = Basemap(llcrnrlon=min_lon - diff, llcrnrlat=min_lat - diff, \
                    urcrnrlon=max_lon + diff, urcrnrlat=max_lat + diff, \
                    resolution = 'l')

        """Retrieve background map using the ArcGIS Server REST API and display
        it on the plot. 'ESRI_StreetMap_World_2D' is the default map server.
        * IMPORTANT: Internet connection required.
        """
        m.arcgisimage(service=service, xpixels=900)

        # Supply coordinates to the Basemap object
        x, y = m(lons, lats)

        # Make scatter plot of query results in the OSM file, divided by group
        scatterplot = [m.scatter(x[i], y[i], s=15, color=colors[i], \
                                    label=labels[i]) for i in n]
        plt.title(title)
        plt.legend(handles=[scatterplot[i] for i in n], loc=3)

        # Notify user a picture is being generated [10]
        sys.stdout.write("\n* Generating '{}.png'".format(fig_name))
        start = time.time()
        time.sleep(.5)
        while (time.time() - start) < 2:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(.5)

        # Store all pictures in subdirectory 'img'; set image quality with 'dpi'
        directory = './img'
        fig_name = fig_name
        plt.savefig('{}/{}.png'.format(directory, fig_name), dpi=150, \
                    format='png', bbox_inches='tight')

        # Increment flag in case plot generation is successful
        plt_flag += 1

    except:
        pass

    return plt_flag

"""B.1 - Most represented cities
"""
most_represented_cities = "SELECT join_tags.value, \
                                    municipalities.province, count(*) AS num \
                            FROM municipalities, {join_tags} \
                            WHERE join_tags.value \
                                    = municipalities.municipality \
                            GROUP BY join_tags.value \
                            ORDER BY num DESC \
                                LIMIT 15;".format(join_tags=join_tags)

top_15_cities = execute_query(most_represented_cities)

print('\n\nB. ADDITIONAL STATISTICS')
print('\nQUERY 1: Print a list of the 15 most represented municipalities')
print(' ' * 9 + 'and associated provinces.\n')

print('{:<25s}{:<17}{}'.format('MUNICIPALITY', 'PROVINCE', 'COUNT'))
print('-' * 51)
for municipality, province, count in top_15_cities:
    print('{:<25}{:<17}{}'.format(municipality, province, count))

"""B.2 - Postal Codes

Admissible postcodes in the OSM file for Milan, Italy are [11]:

 20010 - 20099: Municipalities in the Metropolitan City of Milan area
 20121 - 20162: City of Milan
 20811 - 20900: Province of Monza and Brianza (*)

(*) The province of Monza and Brianza 'was officially created by splitting the
north-eastern part from the province of Milan [...] and became executive after
[...] June 2009' [12]. Postcodes related to this province are very common in
the OSM file; however, these do not belong in the dataset anymore.
"""

"""SQL query to find the coordinates of a set of OpenStreetMap nodes, given
input constraints on tag keys and values. Valid for 'postcodes', 'parks'.
"""
query = "SELECT nodes.lon, nodes.lat \
            FROM nodes, {join_tags} \
            WHERE join_tags.id = nodes.id \
                AND join_tags.key = {} \
                AND {} \
            ORDER BY join_tags.value;"

# Fill the empty brackets in the query above with each (key, constraint) pair
postcode_keys = ["'postcode'"]*4

postcode_constr = ["join_tags.value BETWEEN '20121' AND '20162'", \
                    "join_tags.value BETWEEN '20010' AND '20099'", \
                    "join_tags.value BETWEEN '20811' AND '20900'", \
                    "(join_tags.value < '20010' OR join_tags.value > '20900')"]

# Additional required arguments for 'street_map'
postcode_colors = ['royalblue', 'limegreen', 'darkorange', 'crimson']
postcode_labels = ['City of Milan', 'Municipalities in the MCM area', \
                    'Province of Monza and Brianza', 'Other Provinces']
postcode_title = 'Map of postal codes in the OpenStreetMap sample file for \
Milan, Italy'

"""Create a visual map of all postcodes in the OSM sample file for Milan, Italy.
Store output figure in './img' folder with name 'postcode.png', if flag != -1.
"""
postcode_fig_title = 'postcodes'
postcode_flag = street_map(query, postcode_constr, 0.18, postcode_colors,
            postcode_labels, postcode_title, postcode_fig_title, postcode_keys)

"""If (postcode < 20010) | (postcode > 20900), find which city and province it
refers to:
"""
postcode_by_province = "SELECT municipalities.postcode AS postcode, \
                                join_tags.value AS city_name, \
                                municipalities.province AS province \
                            FROM municipalities, {join_tags} \
                            WHERE join_tags.key='city' \
                                AND (postcode < 20010 OR postcode > 20900) \
                                AND city_name = municipalities.municipality \
                            GROUP BY city_name \
                            ORDER BY postcode;".format(join_tags=join_tags)

pbp = execute_query(postcode_by_province)

print('\n\nQUERY 2: Print postal code, municipality, and province for all')
print(' ' * 9 + 'the entries which should not belong in the Milan OSM file.\n')

print('{:<12s}{:<30}{}'.format('POSTCODE','MUNICIPALITY','PROVINCE'))
print('-' * 51)
for postcode, municipality, province in pbp:
    print('{:<12}{:<30}{}'.format(postcode, municipality, province))

# Print total number of entries in the table
print('count: {}'.format(len(pbp)))

"""B.3 - Most popular shops
"""
shops = "SELECT value, count(*) AS num \
            FROM {join_tags} \
            WHERE key = 'shop' \
            GROUP BY value \
            ORDER BY num DESC \
                LIMIT 15;".format(join_tags=join_tags)

shops_exec = execute_query(shops)

print('\n\nQUERY 3.A: Print a list of the 15 most popular shop types.\n')
print('{:<42s}{}'.format('SHOP', 'COUNT'))
print('-' * 51)
for shop, count in shops_exec:
    print('{:.<40}: {}'.format(shop, count))

"""A prominent tag value related to shops is value='yes'. Use of this tag is
considered bad practice by wiki.openstreetmap.org: find out where, when, and
by whom it was used. Only return the most recent 15 entries.
"""

"""Print date (YYYY-MM-DD), user, municipality, and province of all entries
where key='shop' and value='yes'. Date is extracted by selecting the first 10
characters from 'timestamp' using SUBSTR().
"""
shops_yes = "SELECT SUBSTR(join_nodes.timestamp, -10,-10) AS date, \
                    join_nodes.user, join_tags.value, municipalities.province \
                FROM {join_tags}, (SELECT id, timestamp, user FROM nodes \
                                    UNION ALL \
                                    SELECT id, timestamp, user FROM ways) \
                                    join_nodes, municipalities \
                WHERE join_tags.id IN (SELECT id FROM {join_tags} \
                                        WHERE key='shop' AND value='yes') \
                    AND join_tags.key='city' \
                    AND join_nodes.id = join_tags.id \
                    AND join_tags.value = municipalities.municipality \
                ORDER BY date DESC \
                    LIMIT 15;".format(join_tags=join_tags)

shops_yes_exec = execute_query(shops_yes)

print('\n\nQUERY 3.B: Print date, user, municipality, and province of the')
print(' ' * 11 + "most recent 15 entries where key='shop' and value='yes'.\n")
print('{:<15s}{:<19s}{:<25s}{}'.format('DATE', 'USER', 'MUNICIPALITY', \
                                        'PROVINCE')),
print('-' * 75)
for date, user, city, province in shops_yes_exec:
    print('{:<15}{:<19}{:<25}{}'.format(date, user, city, province))


yes_shop_types = "SELECT key, value, type, count(*) AS num \
                    FROM {join_tags} \
                    WHERE key = 'shop' AND value = 'yes' \
                    GROUP BY type \
                    ORDER BY num;".format(join_tags=join_tags)

shop_yes_type_exec = execute_query(yes_shop_types)
print("\n\nQUERY 3.C: Breakdown of shop='yes' tag by type.\n")
print('{:<12s}{:<13}{:<17}{}'.format('KEY', 'VALUE', 'TYPE', 'COUNT'))
print('-' * 51)
for key, value, typology, count in shop_yes_type_exec:
    print('{:<12}{:<13}{:<17}{}'.format(key, value, typology, count))

disused_shops = "SELECT value, count(*) AS num \
                    FROM {join_tags} \
                    WHERE id IN (SELECT id \
                                    FROM {join_tags} \
                                    WHERE key = 'shop' \
                                        AND value = 'yes' \
                                        AND type = 'disused') \
                        AND key = 'city' \
                        GROUP by value \
                        ORDER by num DESC \
                            LIMIT 15;".format(join_tags=join_tags)

disused_shops_exec = execute_query(disused_shops)
print('\n\nQUERY 3.D: Location of disused yes shops.\n')
print('{:<42s}{}'.format('MUNICIPALITY', 'COUNT'))
print('-' * 51)
for location, count in disused_shops_exec:
    print('{:.<40}: {}'.format(location, count))

"""B.4 - Parks

Find the location of all parks in the OpenStreetMap file.
Look for the following tags (after joining tables 'nodes_tags', 'ways_tags'):

 - Trees: 'tree', 'tree_row', 'tree_group';
 - Waste baskets: 'waste_basket';
 - Benches: 'bench';
 - Fountains: 'drinking_water'.
"""
parks_keys = ["'natural'", "'amenity'", "'amenity'", "'amenity'"]

parks_constr = ["join_tags.value IN ('tree', 'tree_row', 'tree_group')", \
                "join_tags.value = 'waste_basket'", \
                "join_tags.value = 'bench'", \
                "join_tags.value = 'drinking_water'"]

parks_colors = ['limegreen', 'lightcoral', 'sienna', 'aqua']
parks_labels = ['Tree', 'Waste basket', 'Bench', 'Drinking water']
parks_title = 'Location of parks in the OpenStreetMap sample file for Milan, \
Italy'

parks_fig_title = 'parks'
parks_flag = street_map(query, parks_constr, 0.05, parks_colors, parks_labels,
                        parks_title, parks_fig_title, parks_keys)

"""B.5 - Eateries in Milan

To display all eateries in the City of Milan only, two methods are used:

- tag='city' method: find all tag values in a desired set, e.g. ('restaurant',
                     'bbq'), searching among all nodes and ways that have tag
                     value='Milano' associated with tag key='city'. This is the
                     wrong method: most eateries do not have added key='city';
- min, max coordinates: find all tag values in a desired set, searching among
                        all nodes and ways whose coordinates are within the
                        city boundaries of Milan, as determined by the min, max
                        longitude and latitude for all tags with value='Milano'
                        associated to tag key='city'. This is the right method.
"""
eateries_by_city_tag = "SELECT nodes.lon, nodes.lat \
                            FROM nodes, {join_tags} \
                            WHERE nodes.id IN (SELECT id FROM {join_tags} \
                                    WHERE join_tags.key = 'city' \
                                    AND join_tags.value = 'Milano') \
                                    AND join_tags.id = nodes.id \
                                    AND join_tags.key = 'amenity' \
                                    AND join_tags.value IN {} \
                            ORDER BY join_tags.value;"

eateries_by_boundaries = "SELECT nodes.lon, nodes.lat \
                            FROM nodes, {join_tags}, \
                                (SELECT MIN(nodes.lon) AS min_lon, \
                                        MAX(nodes.lon) AS max_lon, \
                                        MIN(nodes.lat) AS min_lat, \
                                        MAX(nodes.lat) AS max_lat \
                                    FROM nodes, {join_tags} \
                                    WHERE join_tags.key='city' \
                                        AND join_tags.value = 'Milano' \
                                        AND nodes.id = join_tags.id) e \
                            WHERE nodes.lon BETWEEN e.min_lon AND e.max_lon \
                                AND nodes.lat BETWEEN e.min_lat AND e.max_lat \
                                AND nodes.id = join_tags.id \
                                AND join_tags.value IN {};"

# Look for the following tag tuples in the queries above
eateries_constr = ["('bar', 'pub')", \
                    "('restaurant', 'bbq')", \
                    "('cafe', 'ice-cream')", \
                    "('fast_food')"]

eateries_colors = ['lime', 'tomato', 'blue', 'gold']
eateries_labels = ['Bars and pubs', 'Restaurants and BBQs', \
                    'Cafés and ice-cream shops', 'Fast food']

ect_title = "Eateries by tag key='city' in Milan, Italy, OpenStreetMap sample"
ebb_title = 'Eateries by boundaries in Milan, Italy, OpenStreetMap sample'

ect_fig_title = 'eateries_by_city_tag'
ebb_fig_title = 'eateries_by_boundaries'

ect_flag = street_map(eateries_by_city_tag, eateries_constr, 0.1,
                    eateries_colors, eateries_labels, ect_title, ect_fig_title)

ebb_flag = street_map(eateries_by_boundaries, eateries_constr, 0.1,
                    eateries_colors, eateries_labels, ebb_title, ebb_fig_title)

"""B.6 - Most popular cuisines
"""
most_popular_cuisines = "SELECT value, count(*) AS num \
                            FROM {join_tags} \
                            WHERE key='cuisine' \
                                AND value != 'other' \
                            GROUP BY value \
                            ORDER BY num DESC;".format(join_tags=join_tags)

cuisines_exec = execute_query(most_popular_cuisines)

print('\n\nQUERY 4: Find the most popular cuisines.\n')
print('{:<42s}{}'.format('CUISINE', 'COUNT'))
print('-' * 51)
for cuisine, count in cuisines_exec:
    print('{:.<40}: {}'.format(cuisine, count))

"""C. SAVE MAPS TO FILE

Save maps to .png and inform user. Also print folder './img' creation message
if not already present.
"""
print('\n\nC. SAVE MAPS TO FILE\n')
if flag != -1:
    print("Generated folder './img'")
else:
    pass

flag_list = [postcode_flag, parks_flag, ect_flag, ebb_flag]
fig_list = [postcode_fig_title, parks_fig_title, ect_fig_title, ebb_fig_title]

# Only notify user whenever a picture is actually saved
for i in range(len(flag_list)):
    if flag_list[i] != -1:
        print("Saved '{}.png' in folder './img'.".format(fig_list[i]))

# Close the Connection object (i.e. the database)
conn.close()

# Return total elapsed time
toc = time.time() - tic
print('\nTotal elapsed time: {:.2f} seconds\n'.format(toc))
