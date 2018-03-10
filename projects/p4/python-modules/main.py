"""Auxiliary functions to retrieve HTML content (requests + BeautifulSoup)
and write the output to csv.

Do not run this module, simply import it.

2018 - Federico Massari / federico.massari@libero.it
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

    html = requests.get(url)
    soup = BeautifulSoup(html.text, parser)

    print('Retrieved content from: {}'.format(url))

    return soup

def write_csv(entries, fieldnames, filename, directory='./data/csv/'):
    """Write content of a web page on a csv file.

    Arguments:
        entries -- list of dict. List of dictionaries, each containing a row,
            or entry, of the table.
        fieldnames -- list. List of field names, header row of the csv file.
        filename -- str. Name of the output csv file.

    Keyword arguments:
        directory -- str. Destination path of the file (default './data/csv/').

    Returns:
        A csv document distilling the information of the selected web page.
    """
    import os
    import csv

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Add extension to filenames if not present
    if filename.split('.')[-1] not in 'csv':
        filename = ''.join(filename + '.csv')

    path = ''.join([directory, filename])

    with open(path, 'w', newline='') as w:
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
