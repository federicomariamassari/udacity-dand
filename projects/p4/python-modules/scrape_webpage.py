"""Scrape HTML content from 'They Shoot Pictures' and write to csv.

For the specified pages, this module allows to:
- retrieve the page HTML structure;
- extract the content of a table and store it in a list of dictionaries;
- write each key, value pair on a csv file.

Use Python 3 to run this file.
Run the module while in the 'p4' directory (not 'p4/python-modules').

2018 - Federico Massari / federico.massari@libero.it
"""

# Import auxiliary functions
from main import get_soup
from main import write_csv

def top_directors(soup):

    import re
    from collections import OrderedDict

    entries = []

    # Add first column 'rank', a counter increasing at each row
    rank = 1

    # Make custom field names as there are none in the page
    fieldnames = ['Rank', 'Director']

    compiled_re = re.compile(r'''
    [^\d\.\s]     # Do not start with digit, dot, or blank space
    [\w\s\.\-]*   # Find string with any among word, space, dot, or dash
    ''', re.VERBOSE)

    # Get entries within the <div class> tag
    for e in soup.find_all('div', {'class': 'stacks_in text_stack'}):

        """Only pick lines whose first character is a digit (i.e., of the
        form <Rank>. <Director> <Previous Rank> <# Greatest> / <# Cited>),
        and only include rank and director's name.
        """
        if e.get_text()[0].isdigit():

            entry = OrderedDict()

            # Set first entry 'rank' to 1 and augment by one
            entry['Rank'] = rank
            rank += 1

            match_director = re.search(compiled_re, e.get_text())

            if match_director:
                entry['Director'] = match_director.group().strip(' ').split(' ')

                """Make column uniform with those of the xls files with
                the same information. Store names as <surname>, <name>,
                accounting for surnames with a nobility particle.
                """
                particle = ['De', 'de', 'dos', 'Van', 'von']

                if any(char in particle for char in entry['Director']):
                    entry['Director'] = ' '.join(entry['Director'][-2:]) + \
                        ', ' + ' '.join(entry['Director'][:-2])
                else:
                    entry['Director'] = entry['Director'][-1] + \
                        ', ' + ' '.join(entry['Director'][:-1])

            entries.append(entry)

    return fieldnames, entries

def scrape_webpage(base_url, pages, directory='./data/csv/', sleep_time=10):
    """Main function to download a list of pages, scraping ethically.

    Arguments:
        base_url -- str. The common prefix of a given web site.
        pages -- list of dict. Each dictionary must have the form:
            {'id': <str>,       # Page identifier, custom-defined
             'link': <str>,     # Link, to append to 'base_url'
             'filename:' <str>  # Name of the csv file to save*
            }
        * '.csv' automatically appended to filenames without extension.

    Keyword arguments:
        directory -- str. Name of the directory in which the file is stored
            (default './data/csv/').
        sleep_time -- float. Number of seconds to wait before downloading a
            new xls file. For ethical scraping, set this parameter to at least
            5 seconds (default 10).

    Returns:
        A set of csv documents, stored in the desired folder.
    """
    import time

    # Set sleep_time to at least 5 seconds, if manually input
    if sleep_time < 5:
        sleep_time = 5

    # Scrape web page
    for page in pages:
        url = ''.join(base_url + page['link'])
        soup = get_soup(url)

        if page['id'] == 'Top 250 Directors':
            fieldnames, entries = top_directors(soup)

        write_csv(entries, fieldnames, page['filename'])

        # Wait at least 5 seconds unless page is last in the list
        if page != pages[-1]:
            print('Waiting {} seconds for ethical scraping...'\
                    .format(sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    """Automatically scrape all pages in the list."""

    base_url = 'http://www.theyshootpictures.com/'

    """A list of pages to scrape. Each 'page' is a dictionary containing a
    custom defined page identifier, a link which, appended to the base_url,
    produces a fully working web address, and the name of the file to save.
    """
    pages = [
    {'id': 'Top 250 Directors',
     'link': 'gf1000_top250directors.htm',
     'filename': 'top_250_directors.csv'}
    ]

    scrape_webpage(base_url, pages, directory='./data/csv/', sleep_time=10)
