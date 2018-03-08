"""Scrape HTML content from additional webpages and write to csv.

Use Python 3 to run this file.

Run the module while in the 'p4' directory (not 'p4/python-modules').
On Terminal or Command Prompt: python3 python-modules/scrape_others.py

2018 - Federico Massari / federico.massari@libero.it
"""
from collections import OrderedDict

# Import auxiliary functions
from main import get_soup
from main import write_csv

def scrape_webpage(page):

    soup = get_soup(page['link'])

    # Scrape Country coordinates from Google's public data
    if page['id'] == 'Country coordinates':

        fieldnames = []
        for field in soup.find_all("th"):
            fieldnames.append(field.get_text())

        # Rename dictionary field 'name' to 'region'
        fieldnames[-1] = 'region'

        entries = []
        for row in soup.find_all("tr"):
            entry = OrderedDict()
            for i, cell in enumerate(row.find_all("td")):
                if "[" in cell.get_text():
                    entry[fieldnames[i]] = cell.get_text().split("[")[0].strip()
                else:
                    entry[fieldnames[i]] = cell.get_text()

            if entry != {}:
                entries.append(entry)

    return fieldnames, entries

def scrape_all(pages, directory='./data/csv/', sleep_time=10):
    import time

    # Set sleep_time to at least 5 seconds, if manually input
    if sleep_time < 5:
        sleep_time = 5

    for page in pages:
        fieldnames, entries = scrape_webpage(page)
        write_csv(entries, fieldnames, page['filename'])

        # Wait unless page is last in the list
        if page != pages[-1]:
            time.sleep = sleep_time


if __name__ == '__main__':
    """Automatically scrape all pages in the list."""

    """A list of pages to scrape. Each 'page' is a dictionary containing a
    custom defined page identifier, a link which, appended to the base_url,
    produces a fully working web address, and the name of the file to save.
    """
    pages = [
    {'id': 'Country coordinates',
     'link': \
     'https://developers.google.com/public-data/docs/canonical/countries_csv',
     'filename': 'coordinates.csv'}
    ]

    scrape_all(pages)
