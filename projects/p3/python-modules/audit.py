'''
Audit common features of an OpenStreetMap (XML) dataset: street names,
postal codes, city names. Store problematic data in distinct dictionaries.

References
--------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity
    Data Analyst Nanodegree
'''

# Import required libraries
import xml.etree.cElementTree as ET
from collections import defaultdict
import re

'''
The name of the OpenStreetMap file to audit. Either the full OSM file or a
sample, output of 'make_sample'.
'''
filename = 'milan_italy_sample.osm'

# Open OSM file in read mode
OSM_FILE = open(filename, 'r')

'''
A. STREET FEATURES
--------------------------------------------------------------------------

1. Street Types

Include a list of possible street qualifiers contained in street names
(ignoring case):
 - Comunale: local road (invariant);
 - Privat[ao]: private road (-a: feminine; -o: masculine);
 - Provinciale: county road (invariant);
 - Statale: trunk road (invariant).
'''
street_qualifiers = set(['Comunale',
                         'Privat[ao]',
                         'Provinciale',
                         'Statale'])

'''
Join qualifiers in a single string for re.compile using list comprehension.
Look for at most one single qualifier per street name (after blank space).
'''
street_qualifiers_re = ''.join(['(\s{})?'.format(qualifier)
                                for qualifier in street_qualifiers])

'''
Qualifiers, if present, strictly follow street names, e.g. <street name> +
+ <blank space> + <qualifier>.
'''
street_type_re = re.compile(r'\S+' + street_qualifiers_re, re.IGNORECASE)

expected_types = set(['Alzaia',
                      'Bastioni',
                      'Cascina',
                      'Circonvallazione',
                      'Corso',
                      'Corte',
                      'Cortile',
                      'Foro',
                      'Galleria',
                      'Galleria privata',
                      'Giardino',
                      'Largo',
                      'Località',
                      'Passaggio',
                      'Passerella',
                      'Piazza',
                      'Piazzale',
                      'Piazzaletto',
                      'Piazzetta',
                      'Residenza',
                      'Ripa',
                      'Spalto',
                      'Strada',
                      'Strada Provinciale',
                      'Strada Statale',
                      'Torri',
                      'Via',
                      'Via privata',
                      'Via Provinciale',
                      'Viale',
                      'Vicolo',
                      'Vicolo privato'])

'''
Catch additional road types which are hard to clean based on the previous
regular expression. This mainly covers cases in which there is no blank
space between an abbreviated road type and the road number, e.g. 'SP14'
or 'S.P.208'.
'''
additional_road_types_re = re.compile(r'''
S         # String must begin with 'S' (S or S., for 'Strada')
\.*       # Optional punctuation
[\w+]*    # Optional second word
\.*       # Optional additional punctuation
\d+       # String must end with one or more digits
''', re.VERBOSE)

'''
2. Street Names / Historical Date in Name

It is not uncommon to find streets or squares named after a date in which
a historical event took place, usually <day> + <month> [+ <year>].
Apart from 1° (primo, first), days in dates are commonly written in Roman
numerals, as in 'Via XX Settembre'. Months, which are often written in
lowercase, should instead always be capitalized.
'''
expected_months = set(['Gennaio',
                       'Febbraio',
                       'Marzo',
                       'Aprile',
                       'Maggio',
                       'Giugno',
                       'Luglio',
                       'Agosto',
                       'Settembre',
                       'Ottobre',
                       'Novembre',
                       'Dicembre'])

# Join month names with bitwise OR '|', strip last one
expected_months_re = ''.join(['{}|'.format(month)
                          for month in expected_months]).strip('|')

date_in_street_re = re.compile(r'''
\d{1,2}   # Start with day number, one or two digits;
[°]*      # Optionally, account for °, as in 1° (1st);
\s        # One single blank space must follow a number or °;
('''
+ expected_months_re  # Must be followed by a month, ignoring lowercase.
+ ''')
\s*       # Optional space before year
[\d+]*$   # Optional year at the end
''',
re.IGNORECASE | re.VERBOSE)

'''
3. Street Names / Abbreviations

Abbreviations in street names are generally used for both common words,
e.g. 'F.lli' instead of 'Fratelli' (same as 'Bros.' for 'Brothers') and
personal names, e.g. 'A.' instead of 'Ada'. The former are quite easy to
fix, despite the added complication of punctuation both inside ('F.lli')
and outside ('Ing.', for 'Ingegner', i.e. 'Engineer') the word. The latter
are much more difficult to fix, and should be dealt with on a case-by-case
basis, so only words in the first category are replaced.
'''
abbreviations_re = re.compile(r'''
\w+       # Start with letter (e.g. 'F' in 'F.lli') or word (e.g. 'Ing.')
\.        # Required punctuation
\w*       # Optional second word
''', re.VERBOSE)

'''
4. Street Names / Apostrophes

This regular expression covers one bad use of apostrophes in street names,
i.e. a trailing space between l' (letter l + apostrophe) and the word that
follows.
'''
apostrophes_re = re.compile(r'''
\w*       # Start with preposition
l\'       # Preposition must end with l + apostrophe, e.g. l', dell'
\s        # Required blank space
\w+       # Required word after blankspace
''', re.VERBOSE)

'''
5. Street Names / Street Number in Name

This regular expression detects street numbers in street names, e.g. 'Via
Europa 30', ignoring admissible cases such as county road numbers or years.
'''
# Concatenate months and street qualifiers, to be avoided in the re.search
street_with_valid_number = ''.join(['{}|'.format(term) for term in \
                           (expected_months|street_qualifiers)])

# stackoverflow.com/questions/1240275/how-to-negate-specific-word-in-regex
number_in_street_re = re.compile(r'''
^(?!.*(   # Only include street name if it does not begin with any of
'''       # the values included in the following strings
+ street_with_valid_number +
'''
Km|SP|SS  # Other street names with admissible number at the end
)).*
\s        # Include blank space; rule out cases such as '99 for 1899.
\d+$      # End with one or more digits
''', re.VERBOSE | re.IGNORECASE)

def is_street_name(elem):
    return (elem.tag == 'tag') & (elem.attrib['k'] == 'addr:street')


'''
B. POSTCODE FEATURES
--------------------------------------------------------------------------
Italy has five-digit postal codes. The Lombardy region has codes in the
2XXXX range although the acceptable ones, those for the Milan and Monza
provinces, must start with 20, i.e. 20010 - 20900. All codes outside this
range belong to different provinces and are not part of the Milan area.
'''
postcode_re = re.compile(r'''
^\d{0,4}$|     # Find postal codes shorter than 5 digits, OR
^\d{6,}|       # longer than 5 digits, OR
^2[^0]\d{3,}   # whose second digit != 0 (outside the Milan-Monza area)
''', re.VERBOSE)

def is_postcode(elem):
    return (elem.tag == 'tag') & (elem.attrib['k'] == 'addr:postcode')


'''
C. CITY NAMES
--------------------------------------------------------------------------
Uppercase/lowercase prepositions, e.g. 'Cernusco [Ss]ul Naviglio', special
characters (accents, apostrophes), e.g. 'Bascapè/Bascapé', and Provinces
in names, e.g. 'Origgio (VA)' are the most frequent issues in city names.
All lead to unnecessary duplicates in the dataset. Prepositions should
always be lowercase.
'''
prepositions = set(['Al', 'Con', 'Di', 'In', 'Su[l]*'])

prepositions_re = ''.join(['{}|'.format(preposition) \
                           for preposition in prepositions]).strip('|')

city_name_re = re.compile(r'''
\s        # Begin with blank space to single out prepositions only
('''
+ prepositions_re +
''')
|\'|\(    # Also single out entries with special characters OR
|^[a-z]   # Entries beginning with lowercase letter OR
|é$       # Entries ending with 'é'
''', re.VERBOSE)

def is_city_name(elem):
    return (elem.tag == 'tag') & (elem.attrib['k'] == 'addr:city')


# Define auxiliary functions
def audit_feature(features, tag_value, compiled_re, expected=None):
    '''
    Add data not conforming to specified criteria to a dictionary.
    A generalised version of 'audit_street_type' [1].

    Input
    ----------------------------------------------------------------------
    features: dict, required. The dictionary to store problematic data.
    tag_value: str, required. Tag value of 'addr:<tag>'.
    compiled_re: _sre.SRE_Pattern, required. Compiled regex object.
    expected: list or set, optional. Expected data features.
    '''
    match = compiled_re.search(tag_value)
    if match:
        feature = match.group()
        if expected != None:
            if feature not in expected:
                features[feature].add(tag_value)
        else:
            features[feature].add(tag_value)


# Generate empty defaultdicts
street_features = defaultdict(set)
postcode_features = defaultdict(set)
city_features = defaultdict(set)

# Store variables to be used as arguments in 'audit_feature'
re_queries = [street_type_re,
              additional_road_types_re,
              date_in_street_re,
              abbreviations_re,
              apostrophes_re,
              number_in_street_re]

expected = [expected_types,
            None,
            expected_months,
            None,
            None,
            None]

for event, elem in ET.iterparse(OSM_FILE, events=('start',)):
    if (elem.tag == 'node') | (elem.tag == 'way'):
        for tag in elem.iter('tag'):

            # Audit street features
            if is_street_name(tag):

                '''
                Update defaultdict with problematic street features.
                Use list comprehension to pack all queries in a single
                line of code.
                '''
                [audit_feature(street_features, tag.attrib['v'],
                              re_queries[i], expected[i]) for i \
                              in range(len(re_queries))]

            # Audit postcode features
            elif is_postcode(tag):
                '''
                If postcode length is != 5 or the code does not start
                with 20, add code to defaultdict.
                '''
                audit_feature(postcode_features, tag.attrib['v'],
                              postcode_re, None)

            # Audit city features
            elif is_city_name(tag):
                audit_feature(city_features, tag.attrib['v'],
                              city_name_re, None)

# Save re patterns in a list, to be passed to function 'clean.py'
query_library = re_queries + [postcode_re, city_name_re]
