'''
Parse the elements in an OpenStreetMap file, transforming them from document
format to tabular format, and write the data to .csv files, to be imported to
a SQL database as tables.

The transformation process is as follows:
 - Use iterparse ('get_element' function) to iteratively step through each top
   level element in the XML file;
 - Shape each element into several data structures using the 'shape_element'
   custom function;
 - Use a schema ('schema') and a validation library ('cerberus') to ensure the
   transformed data is in the correct format ('validate_element');
 - Write each data structure to the appropriate .csv files ('process_map').

Apart from the 'shape_element' function, all code (with minor modifications)
taken from [1]. Input to the 'shape_element' function provided by [2].

Note: Use Python 3 to run this script. Conversion was made using [3].


References
-------------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity
    Data Analyst Nanodegree
[2] https://discussions.udacity.com/t/p3-project-combining-auditing-cleaning-
    and-csv-creation/231037
[3] https://discussions.udacity.com/t/add-cleaning-functions-to-shape-element
    /348188/3
'''

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
from schema import schema

# Import custom scripts
import audit
import clean
'''
Import the list of compiled regular expressions from audit.py, and the lists
of query_types and mappings from clean.py, all to be used in 'shape_element'.
'''
from audit import re_library
from clean import query_types, mappings

OSM_PATH = 'milan_italy_sample.osm'

NODES_PATH = 'nodes.csv'
NODE_TAGS_PATH = 'nodes_tags.csv'
WAYS_PATH = 'ways.csv'
WAY_NODES_PATH = 'ways_nodes.csv'
WAY_TAGS_PATH = 'ways_tags.csv'

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

SCHEMA = schema

'''
Make sure the field order in the csvs matches the column order in the SQL
table schema.
'''
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset',
               'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

'''
The 'shape_element' function takes as input an iterparse Element object and
returns a dictionary.
'''
def shape_element(element, node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS,
                  lower_colon=LOWER_COLON, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    # The starting index of the 'nd' tag in 'way_nodes.csv', see below
    position = 0

    # For each child (secondary tag) of <node> or <way>, look for <tag>
    for child in element:
        tag = {}
        if child.tag == 'tag':

            # If tag 'k' value contains problematic characters, ignore it
            if problem_chars.search(child.attrib['k']):
                continue

            '''
            If tag 'k' value contains colon, set the character before colon as
            the tag type, and characters after it as the tag key. If there are
            additional colons in the 'k' value, ignore and keep as part of the
            tag key.
            '''
            elif lower_colon.search(child.attrib['k']):
                tag['id'] = element.attrib['id']
                tag['type'] = child.attrib['k'].split(':', 1)[0]
                tag['key'] = child.attrib['k'].split(':', 1)[1]

                '''
                Programmatically clean 'street', 'postcode', and 'city' tag
                values using functions from module clean.py
                '''
                if tag['key'] == 'street':
                    for i in range(len(query_types)):
                        child.attrib['v'] = \
                        clean.update_name(child.attrib['v'], re_library[i],
                                          query_types[i], mappings[i])
                        tag['value'] = child.attrib['v']

                elif tag['key'] == 'postcode':
                    tag['value'] = clean.update_postcode(child.attrib['v'],
                                                         re_library[-2])

                elif tag['key'] == 'city':
                    tag['value'] = clean.update_city_name(child.attrib['v'],
                                                          re_library[-1])

                # Leave other tag values unmodified
                else:
                    tag['value'] = child.attrib['v']

            else:
                '''
                Set tag type to 'regular' (default) if no colon in the tag 'k'
                value is present.
                '''
                tag['type'] = default_tag_type
                tag['key'] = child.attrib['k']
                tag['value'] = child.attrib['v']
                tag['id'] = element.attrib['id']

            if tag:
                tags.append(tag)

        '''
        'way_nodes.csv' holds a list of dictionaries, one for each 'nd' child
        tag. Each dictionary has the fields:
         - 'id': the top level element (way) id;
         - 'node_id': the ref attribute value of the 'nd' tag;
         - 'position': the index, starting at 0, of the 'nd' tag, i.e. what
            order the 'nd' tag appears within the way element.
        '''
        way_node = {}
        if child.tag == 'nd':
            way_node['id'] = element.attrib['id']
            way_node['node_id'] = child.attrib['ref']
            way_node['position'] = position
            way_nodes.append(way_node)
            position += 1

    '''
    Return dictionaries for 'nodes.csv', 'nodes_tags.csv', 'ways.csv', and
    'ways_tags.csv'.
    '''
    if element.tag == 'node':
        for field in NODE_FIELDS:
            node_attribs[field] = element.attrib[field]
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# Helper functions
def get_element(osm_file, tags=('node', 'way', 'relation')):
    '''Yield element if it is the right type of tag'''

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    '''Raise ValidationError if element does not match schema'''
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.items())
        message_string = "\nElement of type '{0}' has following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


# Main function
def process_map(file_in, validate):
    '''Iteratively process each XML element and write to csv(s)'''

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    '''
    Note: Validation is ~ 10X slower. For the project consider using a small
    sample of the map when validating.
    '''
    process_map(OSM_PATH, validate=False)
