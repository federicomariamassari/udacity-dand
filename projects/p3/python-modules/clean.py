'''
Clean the most commom problematic features in the 'milan_italy.osm' (or
its sample) OpenStreetMap file.

References
--------------------------------------------------------------------------
[1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity
    Data Analyst Nanodegree
'''

# Import required modules
import audit

'''
(1) MAPPINGS

Regarding the mapping for 'privato'/'privata', the lowercase version is
~6x more popular than the capitalized one in the OSM file, so the former
was preserved.
'''
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

'''
(2) CLEANING STREET NAMES

Store variables 'query_types' and 'mappings', to be used as arguments in
the function 'update_name'.
'''
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
    match = re_query.search(name)
    better_name = name
    if match:

        '''
        For street types (including additional road types) replace matched
        key with corresponding value from 'street_type_mapping' dictionary.
        '''
        if query_type == 'street_type':
            if match.group() in mapping.keys():
                better_street_type = mapping[match.group()]
                better_name = re_query.sub(better_street_type, name,
                                           count=1)

        elif query_type == 'additional_road_types':
            for key, value in mapping.items():
                if key in match.group():

                    '''
                    If string contains key, replace the substring with
                    value + blank space + remainder of the string split
                    on the key, e.g. 'SP14' -> (contains key) -> {'SP':
                    'Strada Provinciale'} -> 'Strada Provinciale' + ' ' +
                    '14' -> (result) 'Strada Provinciale 14'.
                    '''
                    better_road_type = value + ' ' \
                                       + match.group().split(key)[1]
                    better_name = re_query.sub(better_road_type, name,
                                               count=1)

            '''
            For dates, split string on blank spaces, take the leftmost
            element (day) and replace it with corresponding value from
            'day_mapping'; then, to the replaced day, add blank space and
            capitalized month, e.g. '24 maggio' -> (split) ['24', 'maggio']
            -> '24' (contains key) -> {'24': 'XXIV'} -> 'XXIV' + ' ' +
            (capitalized remainder of the string) 'Maggio' -> (result)
            'XXIV Maggio'.
            '''
        elif query_type == 'date':
            if match.group().split(' ', 1)[0] in mapping.keys():
                split_string = match.group().split(' ')
                better_date = mapping[split_string[0]] + ' ' \
                + ' '.join(split_string[1:]).capitalize()
                better_name = re_query.sub(better_date, name, count=1)

            '''
            For abbreviations, check if any is present in the examined
            string; if so, split the string on blank spaces, replace the
            abbreviation with the corresponding value from the dictionary
            'abbreviations_mapping', then join the replaced value with
            blank space and the remainder of the split string (removing
            extra spaces, if any).
            '''
        elif query_type == 'abbreviations':
            if any(abbreviation in match.group() for abbreviation \
                   in mapping):
                split_string = match.group().split(' ')
                full_word = ' '.join((mapping[split_string[0]] + ' ' \
                + ' '.join(split_string[1:])).split())
                better_name = re_query.sub(full_word, name,
                                           count=1)

            '''
            For apostrophes, remove blank spaces between the apostrophe
            and the following word, and capitalize all words, e.g. "dell'
            artigianato" -> (split on blank space) ["dell'", 'artigianato']
            -> (join, capitalize) "Dell'Artigianato".
            '''
        elif query_type == 'apostrophes':
            better_apostrophe_use = ''.join(match.group().title().split())
            better_name = re_query.sub(better_apostrophe_use, name,
                                       count=1)

            '''
            For street numbers embedded in street names, split string on
            blank spaces, then join all but the last element, e.g. 'Europa
            30' -> (split on blank space) -> ['Europa', '30'] -> (join all
            but last) -> (result) 'Europa'.
        '''
        elif query_type == 'street_numbers':
            stripped_number = ' '.join(match.group().split(' ')[:-1])
            better_name = re_query.sub(stripped_number, name, count=1)

    return better_name

'''
(3) CLEANING POSTAL CODES
'''
def update_postcode(postcode, re_query):
    match = re_query.search(postcode)
    better_postcode = postcode
    if match:
        if len(match.group()) < 5:
            '''
            If postcode is shorter than five digits add trailing zeros at
            the end, e.g. '2013' -> '20130'. This is the most reasonable
            way to fix the problem, without additional information.
            '''
            better_postcode = match.group() + '0' * (5-len(match.group()))

        elif len(match.group()) > 5:
            '''
            The only postal code longer than 5 digits in the OSM file is
            '200149'. The code contains an extra 0, since '20149' is a
            legitimate Milan area postcode.
            '''
            better_postcode = match.group().replace('0', '', 1)

    return better_postcode
