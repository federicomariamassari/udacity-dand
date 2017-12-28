# Data Analyst Nanodegree: P3 Wrangle OpenStreetMap
__Federico Maria Massari / federico.massari@bocconialumni.it__
## Map area
Milan, Italy
- Milan county boundaries: https://www.openstreetmap.org/relation/44881#map=10/45.4028/9.1290
- Milan metro extract: https://mapzen.com/data/metro-extracts/metro/milan_italy/
- Compressed OSM XML file: https://s3.amazonaws.com/metro-extracts.mapzen.com/milan_italy.osm.bz2

Milan is my hometown and the city I currently live in, so I'm curious to find out how large the local OpenStreetMap community is, and, from a broader perspective, how seriously the project is taken in Italy.

## Data auditing and main problems encountered
To audit the OSM file I used Python's `re` (regular expressions) module. I concentrated on four key features: street names `key=addr:street`, postal codes `key=addr:postcode`, city names `key=addr:city` and cuisines `key=cuisine`. The following are the main issues encountered [see: [audit.py](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/audit.py)].
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
Admissible postal codes had to be five digits long, and have format _20xxx_ (_2_: Region Code for Lombardy; _0_: County Code for the Metropolitan City of Milan and the Province of Monza and Brianza).

__Unusual code length.__ A few codes were either four (e.g., _2013_) or six (e.g., _200149_) digits long. I padded the former with trailing zeros (e.g., _20130_) and stripped the latter of the redundant digits (e.g., _20149_):
```python
if len(match.group()) < 5:
    better_postcode = match.group() + '0' * (5-len(match.group()))
elif len(match.group()) > 5:
    better_postcode = match.group().replace('0', '', 1)
```
__Wrong code format.__ All codes in the OSM file related to Lombardy (i.e., _2xxxx_), but a significant number belonged to different provinces (e.g., _21xxx_: Varese).


__Figure 3: Eateries in Milan__
<p float>
  <img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_city_tag.png" width="434"/>
  <img src="https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/python-modules/img/eateries_by_boundaries.png" width="434"/>
</p>
