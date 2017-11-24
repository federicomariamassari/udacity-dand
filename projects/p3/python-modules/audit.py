def audit(filename):
    '''
    References
    --------------------------------------------------------------------------
    [1] 'Project: Wrangle OpenStreetMap Data', Data Wrangling Course, Udacity
        Data Analyst Nanodegree
    '''

    # Import required libraries
    import xml.etree.cElementTree as ET
    from collections import defaultdict
    import re

    # Open OSM file in read mode
    OSM_FILE = open(filename, 'r')

    '''
    1 - STREET FEATURES
    --------------------------------------------------------------------------

    1.1 - STREET TYPES

    Include a list of possible street qualifiers contained in street names:
     - [Pp]rivat[ao]: private road (-a: feminine; -o: masculine)
     - [Pp]rovinciale: county road (invariant)
     - [Ss]tatale: trunk road (invariant).
    '''
    street_qualifiers = set(['Privat[ao]',
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
    1.2 - STREET NAMES / HISTORICAL DATE IN NAME

    1.2.1 - Day

    It is not uncommon to find streets or squares named after a date in which
    a historical event took place, usually <day> + <month>.
    Apart from 1° (primo, first), the most accepted way to refer to such days
    is with Roman numerals, e.g. 'Via XX Settembre'.
    '''
    day_in_street_re = re.compile(r'''
    \w+       # Start with street type, e.g. Via, Piazza;
    [aeio]    # Last letter of street type must be an accepted vowel;
    \s        # One single blank space must follow street type;
    [\d]+     # One or more numbers must follow blank space;
    [°]*      # Optionally, account for °, as in 1° (1st);
    \s        # One single blank space must follow a number or °;
    \S+       # End with month name.
    ''', re.VERBOSE)

    '''
    1.2.2 - Month

    Months appearing in street names are often written in lowercase. However,
    they should be capitalised.
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

    month_in_street_re = re.compile(r'(' + expected_months_re + ')',
                                    re.IGNORECASE)

    '''
    1.3 - ABBREVIATIONS

    Abbreviations in street names are generally used for both common words,
    e.g. 'F.lli' instead of 'Fratelli' (same as 'Bros.', 'Brothers') and
    personal names, e.g. 'A.' instead of 'Ada'. The former are easy to fix,
    while the latter must be dealt with on a case-by-case basis.
    '''
    abbreviations_re = re.compile(r'''
    \w+       # Start with word, street type or first letter of abbreviation
    \s*\w*    # Optional blank space and word (if \w+ was a street type)
    \.        # Required punctuation
    \s*\w*    # Optional blank space and second word
    \.*       # Optional second punctuation (to catch second names, if any)
    \s*\w*    # Remaining part of the string
    ''', re.VERBOSE)

    # Define auxiliary functions
    def audit_feature(features, street_name, compiled_re, expected=None):
        '''
        Add data not conforming to specified criteria to a dictionary.
        A generalised version of 'audit_street_type' [1].

        Input
        ----------------------------------------------------------------------
        features: dict, required. The dictionary to store problematic data.
        street_name: str, required. Street name, tag value of 'addr:street'.
        compiled_re: _sre.SRE_Pattern, required. Compiled regex object.
        expected: list or set, optional. Expected data features.
        '''
        match = compiled_re.search(street_name)
        if match:
            feature = match.group()
            if expected != None:
                if feature not in expected:
                    features[feature].add(street_name)
            else:
                features[feature].add(street_name)

    def is_street_name(elem):
        return (elem.tag == 'tag') & (elem.attrib['k'] == 'addr:street')

    def audit_street(OSM_FILE, features, compiled_re, expected=None):

        # Wind up OSM file for each additional re.search
        OSM_FILE.seek(0)

        for event, elem in ET.iterparse(OSM_FILE, events=('start',)):
            if (elem.tag == 'node') | (elem.tag == 'way'):
                for tag in elem.iter('tag'):
                    if is_street_name(tag):
                        audit_feature(features, tag.attrib['v'], compiled_re,
                                      expected)
        return features

    # Generate empty defaultdict
    street_features = defaultdict(set)

    # Update defaultdict with problematic street features
    audit_street(OSM_FILE, street_features, street_type_re, expected_types)
    audit_street(OSM_FILE, street_features, day_in_street_re)
    audit_street(OSM_FILE, street_features, month_in_street_re, expected_months)
    audit_street(OSM_FILE, street_features, abbreviations_re)

    '''
    2 POSTCODE FEATURES
    --------------------------------------------------------------------------


    '''

    return street_features, postcode_features
