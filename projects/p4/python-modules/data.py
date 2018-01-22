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

def clean_title(entry, fieldname='Title'):
    """Clean title of an entry according to a custom mapping."""

    mapping = {'\x85.': '...',
               '\x85 ': '... ',
               '….': '...',
               '… ': '... ',
               'Ii,': 'II,',
               'Iii,': 'III,',
               'Xiv': 'XIV',
               '7E': '7e',
               "'M": "'m",
               "'S": "'s",
               "'T": "'t",
               '(S)': '(s)',
               'Nd': 'nd',
               'Tv': 'TV',
               'Jfk': 'JFK',
               'Ka-Den': 'ka-den',
               'Mccabe': 'McCabe'}

    for key, value in mapping.items():
        if key in entry[fieldname]:
            entry[fieldname] = entry[fieldname].replace(key, value)

    return entry[fieldname]

def shape_elements(soup):
    """Prepare HTML content for insertion into csv file.

    Arguments:
        soup -- bs4.BeautifulSoup. The BeautifulSoup constructor, output
            of the function 'get_url'.

    Returns:
        fieldnames -- list of str. A list of field names, the header row.
        entries -- list of dict. A list of dictionaries, each containing a
            row, or entry, of the table.

        Pass both objects to 'write_csv' as, respectively, header and entries.
    """
    import re
    from collections import OrderedDict
    from strings import digits

    entries = []

    """Extract the title from the web page. soup.title.get_text() returns
    a row of the form: '<text> (<title>)', so split by left parens, take the
    second element, and strip the right parens to obtain the desired text.
    """
    page_title = soup.title.get_text().split('(')[1].strip(')')

    if page_title == 'Full List':

        # Retrieve field names (within tag 'th') and append them to list
        fieldnames = []
        for tag in soup.find_all('th'):
            fieldnames.append(tag.get_text())

        """Get entries (tags <td> within <tr>), store them inside dictionaries,
        clean values associated to key 'Title', and append to list 'entries'.
        """
        for tag in soup.find_all('tr'):

            entry = {}
            for i, e in enumerate(tag.find_all('td')):

                # Titlecase titles, to make them uniform across csv files
                if fieldnames[i] == 'Title':
                    entry[fieldnames[i]] = e.get_text().title()

                    # Custom clean the title of an entry, if applicable
                    entry[fieldnames[i]] = clean_title(entry)

                else:
                    entry[fieldnames[i]] = e.get_text()

                    # Clean entries which were not ranked the year before
                    if entry[fieldnames[i]] == '---':
                        entry[fieldnames[i]] = ''

            if entry != {}:
                entries.append(entry)

    elif page_title == 'Top 250 Directors':

        # Make custom field names as there are none in the page
        fieldnames = ['Rank', '2017', 'Director', 'Greatest', 'Cited']

        # Add first column 'rank', a counter increasing at each row
        rank = 1

        # Find dictionary values using regular expressions
        def find_value(entry, re):
            """Evaluate entry using regular expression.

            Arguments:
                entry -- str. The row to evaluate.
                re -- str. The regular expression to compile.

            Returns:
                match -- _sre.SRE_Match. The matched string of text, if any.
            """
            compiled_re = re.compile(re)
            match = re.search(compiled_re, entry)

            return match

        # Get entries within the <div class> tag
        for e in soup.find_all('div', {'class': 'stacks_in text_stack'}):

            """Only pick lines whose first char is a digit, i.e. of the form
            <Rank>. <Director> <Previous Rank> <# Greatest> / <# Cited>
            """
            if e.get_text()[0].isdigit():

                entry = OrderedDict()

                # Set first entry 'rank' to 1 and augment by one.
                entry['Rank'] = rank
                rank += 1

                # Match dictionary key, value pairs
                previous = find_value(e.get_text(), r'\(\d+[\s]*\)|(new)')
                director = find_value(e.get_text(), r'\.[\s\.\-\w+]*')
                greatest = find_value(e.get_text(),
                                        r'\d+[*\w+\d+,\s]*(Greatest)')
                cited = find_value(e.get_text(), r'\d+[\s\w]+(cited)')

                if previous:
                    # Replace cell value '(new)' with blank
                    if previous.group() == '(new)':
                        entry['2017'] = ''
                    else:
                        entry['2017'] = previous.group().strip('\(\)\t')

                elif director:
                    entry['Director'] = director.group().strip('\. ')

                elif greatest:
                    entry['Greatest'] = greatest.group().split(' ')[0]\
                                        .strip('*')

                elif cited:
                    entry['Cited'] = cited.group().split(' ')[0]

                entries.append(entry)

    elif page_title == 'Ranking History':
        

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
