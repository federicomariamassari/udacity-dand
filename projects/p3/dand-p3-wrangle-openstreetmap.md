# Data Analyst Nanodegree: P3 Wrangle OpenStreetMap
__Federico Maria Massari / federico.massari@bocconialumni.it__
## Map Area
Milan, Italy
- Milan county boundaries: https://www.openstreetmap.org/relation/44881#map=10/45.4028/9.1290
- Milan metro extract: https://mapzen.com/data/metro-extracts/metro/milan_italy/
- Compressed OSM XML file: https://s3.amazonaws.com/metro-extracts.mapzen.com/milan_italy.osm.bz2

Milan is my hometown and the city I currently live in.

## Main Problems Encountered
### Street names
- __Lowercase or abbreviated street type__: e.g. _"piazza"_ instead of _"Piazza"_ or _"V.le"_ instead of _"Viale"_;
- __House number in street name__: e.g. _"Via Europa 30"_ instead of _"Via Europa"_;
- __Wrongly formatted date in street name__: e.g. _"Via 20 settembre"_ instead of _"Via XX Settembre"_.
### Postal codes
- __Mistyped postcode__: either too short (_2013_ instead of _2013x_) or too long (_200149_ instead of _20149_);
- __Postcode related to another province__: any code outside the _20010-20900_ range (related to the Milan metropolitan area and the Monza-Brianza province).
### City names
- __Titlecase preposition__: e.g. _"Cernusco Sul Naviglio"_ instead of _"Cernusco sul Naviglio"_;
- __Province in city name__: e.g. _"Origgio (VA)"_ instead of _"Origgio"_;
- __Missing blank space after truncation__: e.g. _"Cassina de'Pecchi"_ instead of _"Cassina de' Pecchi"_.
### Cuisines
- __Too granular set of cuisines__: in order to produce insightful summaries, the `key='cuisine'` tag required a bit of aggregation, e.g. by mapping values _"pizza"_, _"italian"_, and _"greek"_ to label _"mediterranean"_.
