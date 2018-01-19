"""Clean 'Kickstarter projects' dataset from Kaggle.

This Python 3 module reads 'ks-projects-201801.csv' [1], fixes a delimiter
error, and prints the lines of the cleaned document to a new file 'ks.csv'.

Delimiter error
------------------------------------------------------------------------------
The error occurs in ~3800 rows, in which the penultimate element lacks the
closing quotation marks. For instance, line 171:

171  "1000694855","STREETFIGHTERZ WHEELIE MURICA",...,"0","N,"0"

The module replaces "N,"0" with "N","0".

Additional fixes
------------------------------------------------------------------------------
The column of "N" contains country codes. In most cases, it is possible to
substitute the corrupted code with one inferred from the 'currency' column
(column 4). This cannot be done if the currency is 'EUR' (~200 observations).

R-Python interaction
------------------------------------------------------------------------------
If you are using R for exploratory data analysis, use the command window
interface 'system()' to call this module:

system('python3 clean_csv.py')

References
------------------------------------------------------------------------------
[1] https://www.kaggle.com/kemical/kickstarter-projects/data
"""
import csv

directory = './data/'
file_in = 'ks-projects-201801.csv'
file_out = 'ks.csv'

with open(''.join([directory, file_in]), 'r', newline='') as f, \
     open(''.join([directory, file_out]), 'w', newline='') as w:

    reader = csv.reader(f)
    writer = csv.writer(w)

    # If possible, replace "N" with one value from the mapping
    mapping = {'USD': 'US', 'CAD': 'CA', 'GBP': 'GB',
               'CHF': 'CH', 'AUD': 'AU', 'NZD': 'NZ',
               'SEK': 'SE', 'NOK': 'NO', 'DKK': 'DK'}

    for row in reader:
        if row[-1] == 'N,0"':
            e = row[-1].split(',')
            row.remove(row[-1])
            row.extend((e[0], e[1].rstrip('\"')))

            # If currency == 'EUR', cannot discriminate among countries
            if row[4] != 'EUR':
                row[-2] = mapping[row[4]]

        writer.writerow(row)
