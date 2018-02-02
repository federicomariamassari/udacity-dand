"""Scrape HTML content from Wikipedia and write to csv.

For the specified Wikipedia pages, this module allows to:
- retrieve the page HTML structure;
- extract the content of a table and store it in a list of dictionaries;
- write each key, value pair on a csv file.

Use Python 3 to run this file.

2018 - Federico Massari / federico.massari@libero.it
"""

"""A. Auxiliary Functions

Use these functions to retrieve HTML content (requests + BeautifulSoup), and
write the output to csv (csv).
"""
def get_soup(url, parser='lxml'):
    """Request a web page and pass it to a BeautifulSoup constructor.

    Arguments:
        url -- str. The url of the web site to scrape.

    Keyword arguments:
        parser -- str. The HTML or XML parser; for various options see [1]
            (default 'lxml').

    Returns:
        The 'soup' BeautifulSoup constructor.

    References:
    [1] https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    from bs4 import BeautifulSoup
    import requests
    import time

    html = requests.get(url)
    soup = BeautifulSoup(html.text, parser)

    print('Retrieved content from: {}'.format(url))

    return soup

def write_csv(entries, fieldnames, filename, directory='./csv/'):
    """Write content of a web page on a csv file.

    Arguments:
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.
        fieldnames -- list. List of field names, header row of the csv file.
        filename -- str. Name of the output csv file.

    Keyword arguments:
        directory -- str. Destination path of the file (default './csv/').

    Returns:
        A csv document distilling the information of the selected web page.
    """
    import os
    import csv

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(''.join([directory, filename]), 'w', newline='') as w:
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

"""B. Scrape Wikipedia

Request HTML content and store it in a BeautifulSoup constructure.
"""
def country_gdp_by_sector(soup):
    """Get Countries' GDP by sector from Wikipedia.

    Retrieve Countries' GDP by sector (Agriculture, Industry, Services) from
    https://en.wikipedia.org/wiki/List_of_countries_by_GDP_sector_composition
    and store the results in a list of dictionaries.

    Arguments:
        soup. bs4.BeautifulSoup. The BeautifulSoup constructor from 'get_soup'.

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

if __name__ == '__main__':
    base_url = 'https://en.wikipedia.org/wiki/'
    links = ['List_of_countries_by_GDP_sector_composition']

    for link in links:
        url = ''.join(base_url + link)
        soup = get_soup(url)
        if link == 'List_of_countries_by_GDP_sector_composition':
            fieldnames, entries = country_gdp_by_sector(soup)
            filename = 'gdp.csv'
            write_csv(entries, fieldnames, filename)
