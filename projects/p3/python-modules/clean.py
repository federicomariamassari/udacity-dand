"""Clean the most commom problematic features in the 'milan_italy.osm' (or its
sample) OpenStreetMap file.

Note: Use Python 3 to run this script.

* Module 3 of 6

References
-------------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity Data
    Analyst Nanodegree

2017 - Federico Maria Massari / federico.massari@bocconialumni.it
"""

# Import required modules
import audit
from audit import re_library

"""(1) MAPPINGS

Regarding the mapping for 'privato'/'privata', the lowercase version is ~6x
more popular than the capitalized one in the OSM file, so the former was
preserved.
"""
street_type_mapping = {'piazza': 'Piazza',
                       'Stradia': 'Strada',
                       'S.C.': 'Strada Comunale',
                       'S.P.': 'Strada Provinciale',
                       'S.S.': 'Strada Statale',
                       'SC': 'Strada Comunale',
                       'SP': 'Strada Provinciale',
                       'SS': 'Strada Statale',
                       'Strada comunale': 'Strada Comunale',
                       'Strada provinciale': 'Strada Provinciale',
                       'Strada statale': 'Strada Statale',
                       'VIa': 'Via',
                       'via': 'Via',
                       'Via Privata': 'Via privata',
                       'viale': 'Viale',
                       'Vicolo Privato': 'Vicolo privato'}

# Apart from '1°', days in historical dates are written in Roman numerals
day_mapping = {'1°': '1°',      'I' : '1°',     '2' : 'II',
               '3' : 'III',     '4' : 'IV',     '5' : 'V',
               '6' : 'VI',      '7' : 'VII',    '8' : 'VIII',
               '9' : 'IX',      '10': 'X',      '11': 'XI',
               '12': 'XII',     '13': 'XIII',   '14': 'XIV',
               '15': 'XV',      '16': 'XVI',    '17': 'XVII',
               '18': 'XVIII',   '19': 'XIX',    '20': 'XX',
               '21': 'XXI',     '22': 'XXII',   '23': 'XXIII',
               '24': 'XXIV',    '25': 'XXV',    '26': 'XXVI',
               '27': 'XXVII',   '28': 'XXVIII', '29': 'XXIX',
               '30': 'XXX',     '31': 'XXXI'}

abbreviations_mapping = {'C.na': 'Cascina',
                         'Cav.': 'Cavalier',
                         'F.lli': 'Fratelli',
                         'Ing.': 'Ingegner',
                         'Geom.': 'Geometra',
                         'On.': 'Onorevole'}

"""(2) CLEANING STREET NAMES

Store variables 'query_types' and 'mappings', to be used as arguments in the
function 'update_name'.
"""
query_types = ['street_type',
               'additional_road_types',
               'date',
               'abbreviations',
               'apostrophes',
               'street_numbers']

mappings = [street_type_mapping,
            street_type_mapping,
            day_mapping,
            abbreviations_mapping,
            None,
            None]

# Clean street types and names
def update_name(name, re_query, query_type, mapping=None):
    """Update inconsistent OSM tag values if related key is k="addr:street".

    Arguments:
        name -- str. Tag value to update, if its key is k="addr:street".
        re_query -- _sre.SRE_Pattern. Compiled regular expression object.
        query_type -- str or list of str. Label(s) to discriminate among
            updating algorithms.

    Keyword arguments:
        mapping -- dict. Dictionary with 'key', 'value' respectively the
            substring to replace and its updated version (default None).

    Returns:
        An updated k="addr:street" tag value, processed with the desired
        algorithm and using the provided mapping, if applicable.
    """
    match = re_query.search(name)
    better_name = name
    if match:

        """For street types (including additional road types) replace matched
        key with corresponding value from 'street_type_mapping' dictionary.
        """
        if query_type == 'street_type':
            if match.group() in mapping.keys():
                # If street name is fully lowercase, titlecase it
                if name.islower():
                    name = name.title()
                better_street_type = mapping[match.group()]
                better_name = re_query.sub(better_street_type, name,
                                           count=1)

        elif query_type == 'additional_road_types':
            for key, value in mapping.items():
                if key in match.group():

                    """If string contains key, replace substring with value
                    + blank space + remainder of the string split on key, e.g.
                    'SP14' -> (contains key) -> {'SP': 'Strada Provinciale'}
                    -> 'Strada Provinciale' + ' ' + '14' -> (result) 'Strada
                    Provinciale 14'.
                    """
                    better_road_type = value + ' ' \
                                       + match.group().split(key)[1]
                    better_name = re_query.sub(better_road_type, name,
                                               count=1)

            """For dates, split string on blank spaces, take leftmost element
            (day) and replace it with corresponding value from 'day_mapping';
            then, to the replaced day, add blank space and capitalized month,
            e.g. '24 maggio' -> (split) ['24', 'maggio'] -> '24' (contains key)
            -> {'24': 'XXIV'} -> 'XXIV' + ' ' + (capitalized remainder of the
            string) 'Maggio' -> (result) 'XXIV Maggio'.
            """
        elif query_type == 'date':
            if match.group().split(' ', 1)[0] in mapping.keys():
                split_string = match.group().split(' ')
                better_date = mapping[split_string[0]] + ' ' \
                + ' '.join(split_string[1:]).capitalize()
                better_name = re_query.sub(better_date, name, count=1)

            """For abbreviations, check if any is present in the scanned string;
            if so, split the string on blank spaces, replace abbreviation with
            the corresponding value from the dictionary 'abbreviations_mapping',
            then join the replaced value with blank space and the remainder of
            the split string (removing extra spaces, if any).
            """
        elif query_type == 'abbreviations':
            if any(abbreviation in match.group() for abbreviation \
                   in mapping):
                split_string = match.group().split(' ')
                full_word = ' '.join((mapping[split_string[0]] + ' ' \
                + ' '.join(split_string[1:])).split())
                better_name = re_query.sub(full_word, name,
                                           count=1)

            """For apostrophes, remove blank spaces between apostrophe and the
            following word, and capitalize all words, e.g. "dell' artigianato"
            -> (split on blank space) ["dell'", 'artigianato'] -> (join and
            capitalize) "Dell'Artigianato".
            """
        elif query_type == 'apostrophes':
            better_apostrophe_use = ''.join(match.group().title().split())
            better_name = re_query.sub(better_apostrophe_use, name,
                                       count=1)

            """For street numbers embedded in street names, split string on
            blank spaces, then join all but the last element, e.g. 'Europa 30'
            -> (split on blank space) -> ['Europa', '30'] -> (join all but last)
            -> (result) 'Europa'.
        """
        elif query_type == 'street_numbers':
            stripped_number = ' '.join(match.group().split(' ')[:-1])
            better_name = re_query.sub(stripped_number, name, count=1)

    return better_name

"""(3) CLEANING POSTAL CODES
"""
def update_postcode(postcode, re_query):
    """Update inconsistent OSM tag values if related key is k="addr:postcode".

    Arguments:
        postcode -- str. Tag value to update, if its key is k="addr:postcode".
        re_query -- _sre.SRE_Pattern. Compiled regular expression object.

    Returns:
        An updated k="addr:postcode" tag value.
    """
    match = re_query.search(postcode)
    better_postcode = postcode
    if match:
        if len(match.group()) < 5:
            """If postcode is shorter than five digits add trailing zeros at
            the end, e.g. '2013' -> '20130'. This is the most reasonable way to
            fix the problem, without additional information.
            """
            better_postcode = match.group() + '0' * (5-len(match.group()))

        elif len(match.group()) > 5:
            """The only postal code longer than 5 digits in the full OSM file
            is '200149'. The code likely contains an extra 0, since '20149' is
            a legitimate Milan area postcode.
            """
            better_postcode = match.group().replace('0', '', 1)

    return better_postcode

"""(4) CLEANING CITY NAMES
"""
def update_city_name(city_name, re_query):
    """Update inconsistent OSM tag values if related key is k="addr:city".

    Arguments:
        city_name -- str. Tag value to update, if its key is k="addr:city".
        re_query -- _sre.SRE_Pattern. Compiled regular expression object.

    Returns:
        An updated k="addr:city" tag value.
    """
    match = re_query.search(city_name)
    better_city_name = city_name
    if match:
        if city_name[0].islower():
            # Capitalize first letter of city name if lowercase
            better_city_name = city_name.title()

        elif "'" in match.group():
            """If apostrophe in city name, check if the letter before apostrophe
            is 'e'. If so, the word is de', an abbreviation of del/degli/dei,
            and it requires blank space after it, e.g. 'Cassina de' Pecchi'.
            Otherwise, no space is required, e.g. 'Torre d'Isola'.
            """

            """Split string by apostrophe first: e.g. "Cassina De'Pecchi" ->
            ['Cassina De', 'Pecchi'], then by blank space -> ['Cassina', 'De',
            'Pecchi'].
            """
            split_string = city_name.split("'")[0].split(' ')

            # Join words, make preposition lowercase
            better_city_name = ''.join(split_string[0] + ' ' \
                                       + split_string[1].lower() + "'" \
                                       + city_name.split("'")[1].strip())

            # Add blank space after de'
            if city_name.split("'")[0][-1] == 'e':
                better_city_name = better_city_name.replace("'", "' ")

        elif '(' in match.group():
            """Strip the two-letter Province code from city name. Usually,
            the code follows the city name, in brackets, e.g. 'Origgio (VA)'.
            Remove what follows the opening bracket, then strip blank space.
            """
            better_city_name = city_name.split(match.group())[0].strip()

        elif match.group() == 'é':
            # Replace 'é' with 'è' if last letter of city name
            better_city_name = city_name.split(match.group())[0] + 'è'

        elif any(preposition in match.group() for preposition \
            in ['Al', 'Con', 'Di', 'In', 'Su']):
            """If preposition in city name, split the string on preposition,
            then take the first element, add to it the lowercase preposition,
            and finally add the remainder of the string.
            """
            better_city_name = city_name.split(match.group())[0] \
                                + match.group().lower() + \
                                city_name.split(match.group())[1]

    return better_city_name

"""(5) CLEANING CUISINES
"""
def update_cuisine(cuisine, re_query):
    """Update inconsistent OSM tag values if related key is k="cuisine".

    Aggregate cuisine values into eight distinct categories by geographical
    area. Include a ninth label, 'international', for eateries offering more
    cuisines. The aggregation is made for explanatory analysis, and should
    not be applied to the original OSM document.

    Arguments:
        cuisine -- str. Tag value to update, if its key is k="cuisine".
        re_query -- _sre.SRE_Pattern. Compiled regular expression object.

    Returns:
        An updated k="cuisine" tag value.
    """

    # Add lists to perform membership operations
    african = ['egyptian', 'eritrean', 'moroccan']

    asian = ['chinese', 'giapponese', 'indian', 'japanese', 'korean',
             'malaysian', 'noodle', 'ramen', 'sri_lankan', 'sri lankan',
             'sushi', 'thai', 'taiwanese', 'vietnamese']

    continental = ['buschenschank', 'danish', 'french', 'heuriger', 'german',
                   'russian']

    latin_american = ['argentinian', 'brazilian', 'cuban', 'latin', 'mexican',
                      'peruvian']

    mediterranean = ['fish', 'flatbread', 'friture', 'greek', 'italian',
                     '_italian', 'italian_pizza', 'local', 'macrobiotica',
                     'pesce', 'piadina', 'pizza', 'pizza_al_trancio_da_asporto',
                     'pizzeria', "pizzeria d'asporto", 'pugliese', 'regional',
                     'regional_and_pizzeria', 'regionale', 'seafood',
                     'sicilian', 'spanish', 'specialita_di_pesce', 'taglieri',
                     'traditional', 'trattoria', 'tuscan', 'vegan',
                     'vegetarian']

    middle_eastern = ['arab', 'kebab', 'kebap', 'kevab', 'kosher', 'lebanese',
                      'libanese', 'oriental', 'persian', 'turkish']

    north_american = ['american', 'barbecue', 'burger', 'chicken', 'chips',
                      'deli', 'donut', 'fast_food', 'fried_chicken',
                      'hamburger', 'hamurger', 'hotdog', 'pancake', 'sandwich',
                      'toast']

    oceanic = ['australian']

    international = ['fusion', 'pizza_kebab']

    match = re_query.search(cuisine)
    better_cuisine = cuisine

    if match:
        if cuisine.lower() in african:
            better_cuisine = 'african'
        elif cuisine.lower() in asian:
            better_cuisine = 'asian'
        elif cuisine.lower() in continental:
            better_cuisine = 'continental'
        elif cuisine.lower() in latin_american:
            better_cuisine = 'latin_american'
        elif cuisine.lower() in mediterranean:
            better_cuisine = 'mediterranean'
        elif cuisine.lower() in middle_eastern:
            better_cuisine = 'middle_eastern'
        elif cuisine.lower() in north_american:
            better_cuisine = 'north_american'
        elif cuisine.lower() in oceanic:
            better_cuisine = 'oceanic'
        elif cuisine.lower() in international:
            better_cuisine = 'international'
        else:
            better_cuisine = 'other'

    return better_cuisine

"""(6) TESTING

On Terminal or Command Prompt, run '$ python3 clean.py' to print the output
of the cleaning procedure.
Note: depending on 'k', the parameter governing the size of the sample file
in 'make_sample.py', some dictionaries may be empty.
"""
def print_library(dictionary, re_library, query_types=None, mappings=None):
    """Update and print values from a supplied dictionary of problematic data.

    Arguments:
        dictionary -- dict. Dictionary of problematic data, output of the
            audit.py function 'audit'.
        re_library -- (list of) _sre.SRE_Pattern. Single regular expression
            or list of regular expressions.

    Keyword arguments:
        query_types -- str. or list of str. Label(s) to discriminate among
            updating algorithms (default None).
        mapping -- dict. Dictionary with 'key', 'value' respectively the
            substring to replace and its updated version (default None).

    Prints:
        The list of all updated entries in the provided dictionary, in the
        form: original value -> updated value. Only display pairs for which
        original value != updated value.
    """
    for dict_values in dictionary.values():
        for value in dict_values:
            better_value = value
            if dictionary == street:
                for i in range(len(query_types)):
                    better_value = update_name(better_value, re_library[i],
                                                query_types[i], mappings[i])
            elif dictionary == postcode:
                better_value = update_postcode(better_value, re_library[-3])
            elif dictionary == city:
                better_value = update_city_name(better_value, re_library[-2])
            elif dictionary == cuisine:
                better_value = update_cuisine(better_value, re_library[-1])

            # Only print single-value tags
            single_tag = all([char not in value for char in [';', ',', ':']])

            # Also avoid printing generic tags, like 'meat' or 'steak'
            if (value != better_value) & (single_tag) \
                & (value not in ['meat', 'steak', 'steak_house']):
                print(value, '->', better_value)

# Comment the remaining lines of code to suppress output
filename = 'milan_italy_sample.osm'
street, postcode, city, cuisine = audit.audit(filename, re_library)
print('\nSTREET FEATURES:')
print_library(street, re_library, query_types, mappings)
print('\nPOSTCODE FEATURES:')
print_library(postcode, re_library)
print('\nCITY FEATURES:')
print_library(city, re_library)
print("\nCUISINE FEATURES:")
print("NOTE: Multiple tags and generic words cleaned in 'data.py'.")
print_library(cuisine, re_library)
