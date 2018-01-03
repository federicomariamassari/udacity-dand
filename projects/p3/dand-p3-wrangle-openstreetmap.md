# Data Analyst Nanodegree: P3 Wrangle OpenStreetMap
__Federico Maria Massari / federico.massari@bocconialumni.it__
## Map area
Milan, Italy
- Milan county boundaries: https://www.openstreetmap.org/relation/44881#map=10/45.4028/9.1290
- Milan metro extract: https://mapzen.com/data/metro-extracts/metro/milan_italy/
- Compressed OSM XML file: https://s3.amazonaws.com/metro-extracts.mapzen.com/milan_italy.osm.bz2

Milan is my hometown and the city I currently live in, so I'm curious to find out how large the local OpenStreetMap community is, and, from a broader perspective, how seriously the project is taken in Italy.

The sample used for this project was one-tenth the size of the original OSM file (i.e., _k_ = 10) [see: [make_sample.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/make_sample.py)].

## Data auditing and main problems encountered
To audit the OSM file I used Python's `re` (regular expressions) module. I concentrated on four key features: street names `k="addr:street"`, postal codes `k="addr:postcode"`, city names `k="addr:city"` and cuisines `k="cuisine"`. The following are the main issues I encountered [see: [audit.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/audit.py)].
### Street names
- __Lowercase or abbreviated street type__: e.g., _"piazza"_ instead of _"Piazza"_ or _"V.le"_ instead of _"Viale"_;
- __House number in street name__: e.g., _"Via Europa 30"_ instead of _"Via Europa"_;
- __Wrongly formatted date in street name__: e.g., _"Via 20 settembre"_ instead of _"Via XX Settembre"_.
### Postal codes
- __Mistyped postcode__: either too short (_2013_ instead of _2013x_) or too long (_200149_ instead of _20149_);
- __Postcode related to another province__: any code outside the _20010-20900_ range (related to the Metropolitan City of Milan and the Province of Monza and Brianza).
### City names
- __Titlecase preposition__: e.g., _"Cernusco Sul Naviglio"_ instead of _"Cernusco sul Naviglio"_;
- __Province in city name__: e.g., _"Origgio (VA)"_ instead of _"Origgio"_;
- __Missing blank space after truncation__: e.g., _"Cassina de'Pecchi"_ instead of _"Cassina de' Pecchi"_.
### Cuisines
- __Too granular set of cuisines__: in order to produce insightful summaries, the `key=cuisine` tag required a bit of aggregation (e.g., by mapping values _"pizza"_, _"italian"_, and _"greek"_ to label _"mediterranean"_).

## Data cleaning
The OSM file proved remarkably clean for its size (~831 MB), with very few typos. Most modifications I made related to either applying uniform formatting to tag values (street names, city names) or grouping the latter into broader categories (cuisines) [see: [clean.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/clean.py)].
### Street names
Formatting street names was a rather difficult task to perform: despite the presence of a [clear set of guidelines](http://wiki.openstreetmap.org/wiki/IT:Editing_Standards_and_Conventions#Nomi_delle_strade) (e.g., use titlecase for street types, avoid abbreviations), these are not always followed, especially by occasional mappers. The best examples relate to abbreviations and to historical dates in street names.

__Abbreviations.__ Common issues with this kind were the absence of unambiguous mappings, most notably with personal names (e.g., _"Ada"_, _"Alessandro"_, etc. in place of _"A."_), and the difficulty to update an entry whenever no clear separator, such as blank space, was present between the abbreviation and the word that followed (replacing _"SP"_ with _"Strada Provinciale"_ was intuitive for entries like _"SP 227"_, but not so for those like _"SP14"_, which also required a trailing space).

To partially solve the first problem, I replaced common abbreviations and left personal names unchanged:
```
Via On. R. Besana -> Via Onorevole R. Besana
```
To fix the second one, I applied a mapping every time a clear separator was available:

```python
if match.group() in mapping.keys():
    better_street_type = mapping[match.group()]
    better_name = re_query.sub(better_street_type, name, count=1)
```
```
SP 227 -> Strada Provinciale 227
```
Otherwise, I split the string on the matched key and joined the replaced value to a blank space and the string remainder:
```python
for key, value in mapping.items():
    if key in match.group():
        better_road_type = value + ' ' + match.group().split(key)[1]
        better_name = re_query.sub(better_road_type, name, count=1)
```
```
SP14 Rivoltana -> Strada Provinciale 14 Rivoltana
```
__Historical dates.__ Common issues with this kind were days as one- or two-digit numbers, spelled-out numbers, and lowercase months. The first and last issues were easy to fix, I simply mapped Latin numbers to Roman numerals (apart from _"1°"_), and titlecased month names:
```
Piazza 25 aprile -> Piazza XXV Aprile
```
However, I did not incorporate spelled-out numbers into regular expressions: a full mapping would have required both ordinal (e.g., _"Primo Maggio"_, _"May 1st"_) and cardinal (e.g., _"Due Giugno"_, _"June 2"_) numbers, and the added complexity of the regular expression would have been unjustified, given that few numbers are actually spelled-out.
```
via primo maggio -> Via Primo Maggio
```
### Postal codes
Admissible postal codes had to be five digits long, and have format _20xxx_ (with _2_ the Region Code for Lombardy, and _0_ the County Code for the Metropolitan City of Milan and the Province of Monza and Brianza). Even though most codes were consistent, for a significant group two problems arose: unusual length (rare) and misplacement (quite common).

__Unusual code length.__ A few codes were four (e.g., _2013_), and one was six (i.e., _200149_) digits long. I padded the former with a trailing zero, since they all began with _2_ (e.g., _20130_), and stripped the latter of the redundant digit (e.g., _20149_):
```python
if len(match.group()) < 5:
    better_postcode = match.group() + '0' * (5-len(match.group()))
elif len(match.group()) > 5:
    better_postcode = match.group().replace('0', '', 1)
```
__Code misplacement.__ A considerable number of postal codes belonged to different provinces of Lombardy, such as Varese (_21xxx_) or Como (_22xxx_). I did not remove these codes; instead, I added them to the SQL database for further exploration.
### City names
City names were made consistent with the entries of a csv file containing information on all municipalities of Italy. The file was used, among the others, to associate towns with the corresponding provinces in SQL queries [see: [data.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/data.py)]:
- Municipalities of Italy (compressed): http://lab.comuni-italiani.it/files/listacomuni.zip

Recurring problems at this stage were titlecase propositions and misspelled truncations. In the first case, I singled out the matched prepositions and converted them to lowercase before concatenation with the string remainder. In the other, I checked whether the last letter before the apostrophe was _"e"_, and if so, I added a blank space after the apostrophe:
```python
if "'" in match.group():
    if city_name.split("'")[0][-1] == 'e':
        better_city_name = better_city_name.replace("'", "' ")
```
This way, I correctly discriminated between names such as _"Cassina de' Pecchi"_ and those like _"Torre d'Isola"_.
### Cuisines
Cuisines were grouped into eight categories by geographical area: `african`, `asian`, `continental`, `latin american`, `mediterranean`, `middle eastern`, `north american`, and `oceanic`. Another one, `international`, was used for restaurants offering more cuisines. The aggregation was made for explanatory analysis: I would advise against applying the same mapping to the original OSM file, since the ability to summarise the data does not make up for the significant loss of detail (whether an Asian restaurant serves Japanese or Indian dishes is actually very useful information).
## Data exploration
After the data were cleaned and stored into csv files, they were imported into the SQL database `milan_italy.db` for querying [see: [csv_to_sql.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/csv_to_sql.py)]. Query output can be accessed from any command-line interface [see: [sql_queries.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/sql_queries.py)].

### Size of files in the current working directory
The SQL database is the most effective way to store data: it is ~54% the size of the sample OSM document, and it is lighter than the csv files combined (~51.28 MB).
```
FILENAME                                  SIZE
---------------------------------------------------
milan_italy.osm.........................: 830.97 MB
milan_italy_sample.osm..................: 84.08 MB
milan_italy.db..........................: 45.04 MB
nodes.csv...............................: 29.79 MB
ways_nodes.csv..........................: 11.01 MB
ways_tags.csv...........................: 4.54 MB
ways.csv................................: 3.35 MB
nodes_tags.csv..........................: 2.52 MB
municipalities.csv......................: 64.84 kB
```
### Number of nodes and ways
The ratio of nodes to ways in the dataset was approximately 6.5 to 1.
```sql
SELECT count(*) FROM nodes;
SELECT count(*) FROM ways;
```
```
Number of nodes: 369964
Number of ways: 56992
```
### Number of unique users
To find the number of unique users, I counted all distinct `user` and `uid` (user id) tags across the two tables `nodes` and `ways`. I supposed there would be a one-to-one link between the tag types; however, the result was puzzling:
```
No. of unique users, 'user' tag: 1546
No. of unique users, 'uid' tag: 1545
```
Curious, I checked for the incongruous record, and discovered it is in table `ways`: one user registered with two names but a single id. Interestingly, this is the only odd entry in the full OSM file.
```sql
SELECT a.uid, b.uid, a.user, b.user
    FROM (SELECT uid, user FROM ways GROUP BY uid) a,
         (SELECT uid, user FROM ways GROUP BY user) b
    WHERE a.uid = b.uid AND a.user != b.user;
```
```
Table: 'ways'
(1726553, 1726553, 'Tommasky', 'Tommaso Abbate')
count: 1
```
### Top 5 contributing users
Contribution data exhibit skewness, a property often seen in OSM files, with very few users committing most entries.
```sql
SELECT all_users.user, count(*) AS num
    FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) all_users
    GROUP BY all_users.user
    ORDER BY num DESC LIMIT 5;
```
```
USER                                      NO.
---------------------------------------------------
Alecs01.................................: 70665
ilrobi..................................: 28800
adirricor...............................: 28366
fedc....................................: 25543
Guido_RL................................: 23044
```
### Number of tags that require fixing
Approximately 500 `fixme` tags needing further attention exist in the sample file. `LIKE '%fixme'` covers all possible cases, notably `key=fixme` and `key=note`, `value=FIXME`.
```sql
SELECT count(*)
    FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) join_tags
    WHERE join_tags.key LIKE '%fixme'
        OR join_tags.value LIKE '%fixme'
        OR join_tags.type LIKE '%fixme';
```
```
Number of 'fixme' tags: 497
```
### Most represented cities
Unsurprisingly, the most represented city is Milan, followed by Monza (the second largest, and capital of the homonym province) and, at a great distance, by other municipalities. All centers in the list belong to either of the two provinces, aside from one, Busto Arsizio (position 14), which is part of Varese. The latter is clearly misplaced, and also rather significant (~1.43% of `key=city` tags in the table have such value).
```sql
SELECT join_tags.value, municipalities.province, count(*) AS num
    FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) join_tags, municipalities
    WHERE join_tags.value = municipalities.municipality
    GROUP BY join_tags.value
    ORDER BY num DESC LIMIT 15;
```
```
MUNICIPALITY             PROVINCE         COUNT
---------------------------------------------------
Milano                   Milano           2228
Monza                    Monza-Brianza    845
...
Busto Arsizio            Varese           76          <- Significant but unrelated
```
So, how "dirty" is the OSM file? Two maps can help answer this question.
### Map of postal codes
_Figure 1_ is a scatter plot of all postal codes in the sample. It was made with the [Basemap Toolkit](https://matplotlib.org/basemap/). Blue and green dots symbolise Milan and its metropolitan area, so they are definitely pertinent. Orange dots belong to the Province of Monza and Brianza: they are accepted (the latter was "officially created by splitting the north-eastern part from the Province of Milan, and became executive after June 2009"), though in the future they should be discarded. Red dots are out of place: the big clusters are Busto Arsizio (NW) and Saronno (NNW), both belonging to Varese, as well as Verderio (NE), in the Province of Lecco. To the South, a few spots relate to Pavia and Lodi.
### Map of parks
_Figure 2_ maps all parks (i.e., the set of trees, benches, waste baskets, and drinking fountains) in the document. Apart from a few spots referring to the red clusters analysed above, the surprise is a huge green area to the South-East, clearly part of the Province of Lodi.  This area, which makes for half the parks in the file, should be removed.

<table>
  <tr>
      <td align="center"><b>Figure 1: Map of postal codes</b></td>
      <td align="center"><b>Figure 2: Location of parks</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
    <td><img align="center" src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/postcodes.png"/></td>
    <td><img align="center" src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/parks.png"/></td>
  </tr>
</table>

### Eateries in Milan
To locate all the eateries (i.e., restaurants, bars, cafés, and fast food places) in Milan, I traced the coordinates of all nodes and ways corresponding to the desired amenities and having the `key=city`, `value=Milano` tag pair. The spots, however, were far fewer than expected (_Figure 3.A_). Why? As it turned out, amenity elements rarely include the `key=city` tag, and simply let the coordinates hint at the municipality:
```xml
<node changeset="43304255" id="1301095604" lat="45.4804683" lon="9.1716521"
   timestamp="2016-10-31T13:37:43Z" uid="417672" user="Guidus" version="2">
  <tag k="name" v="Pizzeria da Mimmo" />
  <tag k="amenity" v="restaurant" />
  <tag k="cuisine" v="pizza" />
</node>
```
Therefore, I extracted the boundary coordinates (i.e., minimum and maximum latitude and longitude) from the set of tags with the string `<tag k="addr:city" v="Milano" />`, and mapped out all eateries within the boundaries (_Figure 3.B_):
<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 3: Eateries in Milan</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
    <td align="center"><b>Figure 3.A</b>: Eateries by <code>key=city</code><img align="center" src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_city_tag.png"/></td>
    <td align="center"><b>Figure 3.B</b>: Eateries by boundaries<img align="center" src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_boundaries.png"/></td>
  </tr>
</table>

### Most represented cuisines
Mediterranean cuisine, by far the most popular, mainly encompasses pizzerias and traditional Italian restaurants.
```sql
SELECT value, count(*) AS num
    FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) join_tags
    WHERE key = 'cuisine' AND value != 'other'
    GROUP BY value
    ORDER BY num DESC LIMIT 5;
```
```
CUISINE                                   COUNT
---------------------------------------------------
mediterranean...........................: 117
asian...................................: 19
north_american..........................: 19
middle_eastern..........................: 6
latin_american..........................: 2
```
## Ideas for improvement
### Enhance this OSM document
The information contained in the OSM file for Milan, Italy is, at best, outdated. The two biggest issues seem to be the huge amount of data related to the Province of Monza and Brianza (several nodes and ways date back to 2006-2009, when the province was still part of Milan) and the vast park area belonging to the Province of Lodi.

__Proposed solution.__ In my opinion, the most effective way to deal with the misplaced data is the two-step procedure outlined in the previous section: query the database to find the boundary coordinates of the Metropolitan City of Milan, then remove all elements outside the region borders.

__Benefits.__ With this method, several elements in the first category, as well as the irrelevant park data, should be effortlessly cleared away.

__Anticipated problems.__ A limit of this procedure is the need to manually delete the unrelated points within the area boundaries, and a large number of these, unfortunately, lie in the Province of Monza and Brianza.

As for the `addr:<type>` tags, I believe these have been successfully cleaned.

### Enhance OSM data in general
I tried the [OSM Editing API](http://api.openstreetmap.org/) (specifically, the iD Editor), and I admit that not only it is immediate, but also feels like a good game: it is both engaging and rewarding. Yet, as seen before, systematic contributions to OpenStreetMap are made by a very small group of users, probably because the project is not marketed to the general public in the most effective way.

__Proposed solutions.__ In my opinion, the site could grow its active user base and improve the quality of its service by:
- Embedding OSM data into augmented reality (AR) applications;
- Using the [blockchain technology](https://www.gim-international.com/content/blog/blockchain-in-geospatial-applications-2) to verify contributions.

__Benefits.__ Feeding real-time, easy to modify geospatial information to AR applications for outdoor activities (e.g., trekking, gaming) would not only make input and validation simple and fun steps, but also enrich the data supplied. For example, [_Pokémon GO_](https://www.bustle.com/articles/172317-how-does-pokemon-go-work-heres-everything-we-know-about-the-tech-behind-the-augmented-reality) collects statistics on climate and soil kind to define the type of pocket monsters that players can encounter: if it used OpenStreetMap, these data would effectively enter the OSM database; in turn, up-to-date information would improve safety while playing. Using a public, immutable, decentralised ledger like blockchain to unmistakably record contributions, and rewarding active mappers with tokens, would definitely stimulate competition and boost data quality.

__Anticipated problems.__ Open data need a robust network of users to be fully trustable. AR applications may result unsafe (e.g., if malicious users provide fraudolent directions), and the blockchain technology vulnerable (e.g., if attackers succeed in rewriting history) if the base is too narrow. With time, however, these issues should gradually diminish in importance.
