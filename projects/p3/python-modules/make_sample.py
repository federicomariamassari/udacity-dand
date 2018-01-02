"""Take a systematic sample of elements from the original OSM region.
Vary parameter k to obtain a coarser or finer sample. The file is slightly
modified from [1].

Note: Place the original OSM file in the same folder as this function.
      Use Python 3 to run this script.

* Module 1 of 6

References
-------------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity Data
    Analyst Nanodegree
[2] https://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-
    generated-via-xml-etree-elementtree-in-python

2017 - Federico Maria Massari / federico.massari@bocconialumni.it
"""

# Import required libraries
import xml.etree.cElementTree as ET

"""Single out region name by stripping the .osm extension from the original
filename, add '_sample.osm' to obtain sample file filename.
"""
OSM_FILE = 'milan_italy.osm'
REGION_NAME = OSM_FILE.split('.')
SAMPLE_FILE = '{}_sample.osm'.format(REGION_NAME[0])

"""Take every k-th top level element. k is the parameter governing the size
of the resulting sample file, about ~N/k MB, with N the size of the full OSM
document. As of November 2017, the sample size is ~850/k MB.
"""
k = 100     # Resulting sample ~8.5 MB.

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag [2].
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Write sample file
with open(SAMPLE_FILE, 'w') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='unicode'))

    output.write('</osm>')
