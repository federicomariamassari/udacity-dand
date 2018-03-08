"""Scrape HTML content from Wikipedia and write to csv.

For the specified Wikipedia pages, this module allows to:
- retrieve the page HTML structure;
- extract the content of a table and store it in a list of dictionaries;
- write each key, value pair on a csv file.

Use Python 3 to run this file.

Run the module while in the 'p4' directory (not 'p4/python-modules').
On Terminal or Command Prompt: python3 python-modules/scrape_wikipedia.py

2018 - Federico Massari / federico.massari@libero.it
"""

# Import auxiliary functions
from main import get_soup
from main import write_csv

def scrape_wiki(base_url, pages, directory='./data/csv/', sleep_time=10):
    """Main function to download a list of Wikipedia pages, scraping ethically.

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

        if page['id'] == 'GDP to services':
            fieldnames, entries = country_gdp_by_sector(soup)
        elif page['id'] == 'Country by continent':
            fieldnames, entries = country_by_continent(soup)

        write_csv(entries, fieldnames, page['filename'])

        # Wait at least 5 seconds unless page is last in the list
        if page != pages[-1]:
            print('Waiting {} seconds for ethical scraping...'\
                    .format(sleep_time))
            time.sleep(sleep_time)

"""Scrape Wikipedia pages

Request HTML content and store it in a BeautifulSoup constructor.
"""
def country_gdp_by_sector(soup):
    """Get Countries' GDP by sector from Wikipedia.

    Retrieve Countries' GDP by sector (Agriculture, Industry, Services) from
    https://en.wikipedia.org/wiki/List_of_countries_by_GDP_sector_composition
    and store the results in a list of dictionaries.

    Arguments:
        soup -- bs4.BeautifulSoup. BeautifulSoup constructor from 'get_soup'.

    Returns:
        fieldnames -- list. List of field names, header row of the csv file.
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.

    Pass the output to function 'write_csv'.
    """
    from collections import OrderedDict

    fieldnames = []
    entries = []

    for e, table in enumerate(soup.find_all("table", \
                                {"class", "wikitable sortable"})):
        if e == 4:
            for header in table.find_all("th"):
                field = header.get_text().split('/')[0]
                fieldnames.append(field)
                if field == 'Services':
                    break

            for row in table.find_all("tr"):
                entry = OrderedDict()
                for i, cell in enumerate(row.find_all("td")):
                    if i < 4:
                        entry[fieldnames[i]] = cell.get_text()\
                                                .lstrip('\xa0').split('[')[0]
                if entry != {}:
                    entries.append(entry)

    return fieldnames, entries

def country_by_continent(soup):
    """Retrieve continent, Country pairs from Wikipedia.

    Return a list of Countries by associated continents, from
    https://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent
    _territories_by_continent

    Arguments:
        soup -- bs4.BeautifulSoup. BeautifulSoup constructor from 'get_soup'.

    Returns:
        fieldnames -- list. List of field names, header row of the csv file.
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.

    Pass the output to function 'write_csv'.
    """
    fieldnames = ['Continent', 'Country']

    # Store continent names in list
    continents = []

    # Get continent names, children of tags <h2>
    for i, continent in enumerate(soup.find_all("h2")):
        # Do not include unnecessary titles, remove [edit] text
        if (i > 0) & (i < 7):
            continents.append(continent.get_text().split('[')[0])

    # Store each key, value pair in list 'entries'
    entries = []

    # Country names are stored in tables
    for i, nation in enumerate(soup.find_all("table", \
                                {"class", "wikitable sortable"})):

        # Relevant countries are boldface (children of tags <b>)
        for element in nation.find_all("b"):
            # Store each k,v pair in a dictionary, append the latter to list
            entry = {}
            entry['Continent'] = continents[i]
            # Country names are nested in attributes <a title="Country">
            entry['Country'] = element.a.get("title")

            entries.append(entry)

    return fieldnames, entries


if __name__ == '__main__':
    """Automatically scrape all pages in the list."""

    base_url = 'https://en.wikipedia.org/wiki/'

    """A list of pages to scrape. Each 'page' is a dictionary containing a
    custom defined page identifier, a link which, appended to the base_url,
    produces a fully working web address, and the name of the file to save.
    """
    pages = [
    {'id': 'GDP to services',
     'link': 'List_of_countries_by_GDP_sector_composition',
     'filename': 'gdp.csv'},

    {'id': 'Country by continent',
     'link': 'List_of_sovereign_states_and_dependent_territories_by_continent',
     'filename': 'continents.csv'}
     ]

    scrape_wiki(base_url, pages, directory='./data/csv/', sleep_time=10)
