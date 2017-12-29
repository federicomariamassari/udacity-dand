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
To audit the OSM file I used Python's `re` (regular expressions) module. I concentrated on four key features: street names `key=addr:street`, postal codes `key=addr:postcode`, city names `key=addr:city` and cuisines `key=cuisine`. The following are the main issues I encountered [see: [audit.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/audit.py)].
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
- __Missing blank space after truncation__: e.g. _"Cassina de'Pecchi"_ instead of _"Cassina de' Pecchi"_.
### Cuisines
- __Too granular set of cuisines__: in order to produce insightful summaries, the `key=cuisine` tag required a bit of aggregation, e.g., by mapping values _"pizza"_, _"italian"_, and _"greek"_ to label _"mediterranean"_.

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

__Unusual code length.__ A few codes were four (e.g., _2013_), and one was six (i.e., _200149_) digits long. I padded the former with a trailing zero, since all began with _2_ (e.g., _20130_), and stripped the latter of the redundant digit (e.g., _20149_):
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
Contribution data exhibit left skewness, a property often seen in OSM files, with very few users committing most entries.
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
`fixme` tags are used to mark objects and places that need further attention. There are approximately 500 such tags in the sample. `LIKE '%fixme'` allows to cover all possible cases, notably `key=fixme` and `key=note`, `value=FIXME`.

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
```sql
SELECT join_tags.value, municipalities.province, count(*)
    FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) join_tags, municipalities
    WHERE join_tags.value = municipalities.municipality
    GROUP BY join_tags.value
    ORDER BY count(*) DESC LIMIT 15;
```
```
MUNICIPALITY             PROVINCE         COUNT
---------------------------------------------------
Milano                   Milano           2228
Monza                    Monza-Brianza    845
...
Busto Arsizio            Varese           76          <- Significant but unrelated
```
<table>
  <tr>
      <td align="center"><b>Figure 1: Map of postal codes</b></td>
      <td align="center"><b>Figure 2: Location of parks</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
    <td><img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/postcodes.png"/></td>
    <td><img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/parks.png"/></td>
  </tr>
</table>

<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 3: Eateries in Milan</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
    <td><img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_city_tag.png"/></td>
    <td><img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_boundaries.png"/></td>
  </tr>
</table>

### Most represented cuisines
```sql
SELECT value, count(*) AS num
    FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) join_tags
    WHERE key = 'cuisine' AND value != 'other'
    GROUP BY value
    ORDER BY num DESC;
```
```
CUISINE                                   COUNT
---------------------------------------------------
mediterranean...........................: 117
asian...................................: 19
north_american..........................: 19
middle_eastern..........................: 6
latin_american..........................: 2
continental.............................: 1
international...........................: 1
```
