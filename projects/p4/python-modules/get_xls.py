"""Download the list of the 2,000 greatest movies ever made, from Bill
Georgaris' and Vicki Platt's excellent site: http://www.theyshootpictures.com

'They Shoot Pictures, Don't They?' provides a reasonable cinematic resource
for fellow enthusiasts. It is, in my opinion, the best site for cinema lovers.

If you use this module, please consider visiting the site, which I *strongly*
recommend if you are interested in the topic. I have been a fan for several
years already.

Use Python 3 to run this file.

2018 - Federico Massari / federico.massari@libero.it
"""

def download_all(base_url, links, directory='./xls/', sleep_time=10):
    """Download a list of Excel files, scraping ethically.

    Arguments:
        base_url -- str. The common prefix of a given web site.
        links -- list of str. A list of links. Each link, appended to the
            base url, must produce a fully working web address.

    Keyword arguments:
        directory -- str. Name of the directory in which the file is stored
            (default './xls/').
        sleep_time -- float. Number of seconds to wait before downloading a
            new xls file. For ethical scraping, set this parameter to at least
            5 seconds (default 10).

    Returns:
        The downloaded Excel files, stored in the desired folder.
    """

    import time

    # Set sleep_time to at least 5 seconds, if manually input
    if sleep_time < 5:
        sleep_time = 5

    for link in links:
        xls_file = download_xls(base_url, link)
        write_xls(xls_file, filename=link, directory=directory)

        # Do not wait if link is the last item in the list.
        if link != links[-1]:
            print("Waiting {} seconds for ethical scraping..."\
                    .format(sleep_time))
            time.sleep(sleep_time)

def download_xls(base_url, link):
    """Download Excel file from the url specified."""

    import requests

    url = ''.join(base_url + link)

    return requests.get(url)

def write_xls(xls_file, filename, directory='./xls/'):
    """Write content to xls file.

    Arguments:
        xls_file -- requests.models.Response. requests' Response object,
            Output of requests.get() in 'download_xls'.
        filename -- str. Name of the file to save, with or without extension.

    Keyword arguments:
        directory -- str. Name of the directory in which the file is stored
            (default './xls/').

    Returns:
        An Excel document with the content of 'xls_file'.
    """

    import os

    # Make directory if it does not exist yet
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Add extension to filename if not present
    if filename.split('.')[-1] not in ['xls', 'xlsx']:
        filename = ''.join(filename + '.xls')

    path = ''.join(directory + filename)

    with open(path, 'wb') as file_out:
        file_out.write(xls_file.content)

    print("Saved '{}' in folder '{}'".format(filename, directory))


if __name__ == '__main__':
    """Automatically download all files in the list."""

    base_url = 'http://www.theyshootpictures.com/resources/'

    links = ['1000GreatestFilms.xls',
             'Films-Ranked-1001-2000.xls']

    download_all(base_url, links)
