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
        elif page['id'] == 'Country by area':
            fieldnames, entries = country_by_area(soup)
        elif page['id'] == 'Country by alpha-2 code':
            fieldnames, entries = country_by_code(soup)
        elif page['id'] == 'Country by religion':
            fieldnames, entries = country_by_religion(soup)

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
            country = element.a.get("title")

            # Strip unnecessary text
            if '(' in country:
                entry['Country'] = country.split('(')[0].strip()
            else:
                entry['Country'] = country

            entries.append(entry)

    return fieldnames, entries

def country_by_area(soup):
    """Retrieve Country area divided between land and water.

    Return a list of Countries by area (total and land/water only), from
    https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_area.

    Arguments:
        soup -- bs4.BeautifulSoup. BeautifulSoup constructor from 'get_soup'.

    Returns:
        fieldnames -- list. List of field names, header row of the csv file.
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.

    Pass the output to function 'write_csv'.
    """
    from collections import OrderedDict

    # Make custom fieldnames
    fieldnames = ['Country', 'Total Area', 'Land', 'Water']

    entries = []
    for table in soup.find_all("table", {"class": "wikitable sortable"}):
        for tr in table.find_all("tr"):

            entry = OrderedDict()
            for i, row in enumerate(tr.find_all("td")):
                if i == 1:
                    """Country name is the content of tag <a>. This method
                    ignored the names of those Countries whose entry includes
                    a clickable flag (a few small islands). An alternative
                    method would look at the content of attribute 'title' in
                    row.find("a")['title'], however this also fails whenever
                    no or multiple attributes 'title' are available.
                    """
                    entry[fieldnames[i-1]] = row.a.get_text()

                elif 1 < i < 5:
                    """Each entry value corresponding to keys 'total area',
                    'land', and 'water', is the so-called next sibling of the
                    related <span> tag (i.e., the value is outside any tag, and
                    it is to the right of </span>).
                    """
                    try:
                        if row.span.next_sibling[0].isdigit():
                            # Remove thousands separator from entries
                            entry[fieldnames[i-1]] = row.span.next_sibling\
                                                        .replace(',', '')
                        else:
                            entry[fieldnames[i-1]] = ''

                    # Empty cells have no attribute span
                    except (AttributeError, KeyError) as e:
                        entry[fieldnames[i-1]] = ''

            if entry != {}:
                entries.append(entry)

    return fieldnames, entries

def country_by_code(soup):
    """Retrieve ISO 3166-1 alpha-2 Country codes.

    Return a list of Countries by area (total and land/water only), from
    https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.

    Arguments:
        soup -- bs4.BeautifulSoup. BeautifulSoup constructor from 'get_soup'.

    Returns:
        fieldnames -- list. List of field names, header row of the csv file.
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.

    Pass the output to function 'write_csv'.
    """
    from collections import OrderedDict

    # Make custom fieldnames
    fieldnames = ['Code', 'Country']
    entries = []

    for e, table in enumerate(soup.find_all("table", \
                                            {"class", "wikitable sortable"})):

        """Only retrieve content from the wikitable containing 'officially
        assigned code elements'.
        """
        if e == 0:
            for row in table.find_all("tr"):
                entry = OrderedDict()

                for i, row in enumerate(row.find_all("td")):

                    # Only consider content in the first two columns
                    if i == 0:
                        entry['Code'] = row['id']
                    elif i == 1:
                        entry['Country'] = row.a['title']

                if entry != {}:
                    entries.append(entry)

    return fieldnames, entries

def country_by_religion(soup):
    """Return a breakdown of countries by religion.

    https://en.wikipedia.org/wiki/Religions_by_country
    """

    from collections import OrderedDict

    fieldnames = ['Country', 'Main']

    table = soup.find("table", {"class": "wikitable sortable"})

    for th in table.find_all("th", {"colspan": "2"}):
        fieldname = th.get_text()
        while fieldname not in fieldnames:
            fieldnames.append(fieldname)

    entries = []

    exclude = ['Central Africa', 'Eastern Africa', 'North Africa',
               'Middle East and North Africa', 'Southern Africa',
               'Sub-Saharan Africa', 'Western Africa', 'Asia',
               'Latin America and the Caribbean', 'Total', 'World']

    for table in soup.find_all("table", {"class": "wikitable sortable"}):
        for tr in table.find_all("tr"):
            i = 2
            entry = OrderedDict()
            for td in tr.find_all("td"):
                try:
                    country = td.a.get_text()

                    if country == '[3]':
                        entry['Country'] = 'Philippines'
                    elif country == 'dubious':
                        entry['Country'] = 'Netherlands'
                    elif country == 'Mainland China':
                        entry['Country'] = 'China'
                    else:
                        entry['Country'] = country

                except AttributeError:
                    stat = td.get_text()

                    if '.' in stat:
                        try:
                            entry[fieldnames[i]] = float(stat.strip('%'))
                        except ValueError:
                            # Replace statistics with value '<0.1'
                            entry[fieldnames[i]] = 0.0
                        i += 1

            if entry != {}:

                main = max([v for v in entry.values() if type(v) == float])
                entry['Main'] = [k for k, v in entry.items() if v == main][0]

                try:
                    if entry['Country'] not in exclude:
                        entries.append(entry)
                except KeyError:
                    pass

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
     'filename': 'continents.csv'},

    {'id': 'Country by area',
     'link': 'List_of_countries_and_dependencies_by_area',
     'filename': 'country_area.csv'},

    {'id': 'Country by alpha-2 code',
     'link': 'ISO_3166-1_alpha-2',
     'filename': 'country_codes.csv'},

    {'id': 'Country by religion',
     'link': 'Religions_by_country',
     'filename': 'religions.csv'}
     ]

    scrape_wiki(base_url, pages, directory='./data/csv/', sleep_time=10)
