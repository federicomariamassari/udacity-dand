def get_url(url, parser='lxml', sleep_time=10):
    """Request a web page and pass it to a BeautifulSoup constructor.

    Arguments:
        url -- str. The url of the web site to scrape.

    Keyword arguments:
        parser -- str. The HTML or XML parser; for various options see [1]
            (default 'lxml').
        sleep_time -- float. The number of seconds to wait before accessing
            a new web page. For ethical scraping, set to at least 5 seconds
            (default 10).

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

    # Wait before accessing the next web page
    time.sleep(sleep_time)

    print('Retrieved content from: {}'.format(url))

    return soup

def get_content(base_url, links):
    """Retrieve HTML content from a list of web pages.

    Arguments:
        base_url -- str. The common prefix of a given web site.
        links -- list. A list of web site links; each link, appended
            to the base url, produces a fully working web address.

    Returns:
        A list of HTML structures from the desired web pages.
    """

    pages = []
    for link in links:
        pages.append(get_url(base_url + link))

    return pages

def write_csv(header, entries, file_out, directory='./'):
    """Write content of a web page on csv file.

    Arguments:
        header -- list. A list of field names, the header row of the csv file.
        entries -- list of dict. A list of dictionaries, each containing a row,
            or entry, of the table.
        file_out -- str. The name of the output csv file.

    Keyword arguments:
        directory -- str. The path in which to save the file (default './').

    Returns:
        A csv document distilling the information of the selected web page.
    """
    import csv

    if len(header) != len(entries[0]):
        raise IndexError('Lengths of header and entries do not match.')

    with open(''.join([directory, file_out]), 'w', newline='') as w:
        writer = csv.DictWriter(w, fieldnames = header)
        writer.writeheader()
        writer.writerows(entries)
