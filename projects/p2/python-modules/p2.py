'''
Python module containing the core functions of 'P2 Investigate a Dataset',
Udacity Data Analyst Nanodegree, 2017. Requires Python 3.

Federico Maria Massari / federico.massari@bocconialumni.it

Place the module in your working directory and type 'import p2', then call a
particular function using method notation.

To be able to use the module, you should:

import random
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import seaborn as sns
'''

def age_of_majority(df, age, new_column_name = 'Minor/Adult'):
    '''
    Label a passenger as 'Minor' or 'Adult' based on his or her age.
    Ignore NaN values.

    Input
    ---------------------------------------------------------------------------
    df: pd.DataFrame, required argument. Pandas' input DataFrame.
    age: int or float, required argument. The age of the passenger, in years.
    new_column_name: str, optional argument. The title of the column to add.
                     'Minor/Adult', if omitted.
    '''

    # Ignore missing values
    if pd.notnull(age):

        if age < 18:
            df[new_column_name] = 'Minor'
        else:
            df[new_column_name] = 'Adult'

    return df

def count_unique(df, column_name, new_column_name):
    '''
    Count the occurrences of unique objects in a DataFrame column, maps the
    results to each item, and stores them in a new column.

    Input
    ---------------------------------------------------------------------------
    df: pd.DataFrame, required argument. The DataFrame to expand.
    column_name: str, required argument. The name of the column from which to
                 count the occurrences.
    new_column_name: str, required argument. The name of the new column in
                     which to store the results.
    '''

    # Count unique object occurrences and stores them in a Python dictionary
    counter = df[column_name].value_counts().to_dict()

    # Map the results to each object and store the results in a new DataFrame
    # column
    df[new_column_name] = df[column_name].map(counter)

    return df

def travels_with_spouse(df, title, sib_sp, name_count, new_column_name = \
                        'Spouse Aboard'):
    '''
    Check whether a passenger is travelling with a spouse.

    Input
    ---------------------------------------------------------------------------
    df: pd.DataFrame, required argument. The input DataFrame.
    title, sib_sp, name_count: pd.Series, required arguments. DataFrame columns
                               containing, in each row, passenger title, number
                               of siblings/spouse onboard the Titanic, and
                               number of occurrences of his/her first name.
    new_column_name: str, optional argument. The title of the column to add.
                     'Spouse Aboard', if omitted.
    '''

    if (title in ['Mrs', 'Mr', 'Dr']) & (sib_sp > 0) & (name_count == 2):
        df[new_column_name] = True
    else:
        df[new_column_name] = False

    return df

def replace_title(title):
    '''
    Shrink the total number of honorifics in a dataset.

    Input
    ---------------------------------------------------------------------------
    title: str, required argument. The honorific to evaluate.
    '''

    if title in ['Mlle']:
        return 'Miss'
    elif title in ['the Countess', 'Lady', 'Mme', 'Ms']:
        return 'Mrs'
    elif title in ['Capt', 'Col', 'Don', 'Jonkheer', 'Major', 'Master', 'Sir']:
        return 'Mr'
    else:
        return title

def imputed_age(df, age, mean_age, new_column_name = 'Imputed Age'):
    '''
    Replace missing values in the 'Age' column with the sample mean and store
    the result in a new column.

    Input
    ---------------------------------------------------------------------------
    df: pd.DataFrame, required argument. The input DataFrame.
    age: int or float, required argument. The age of the passenger, in years.
    mean_age: int or float, required argument. Average age in the 'Age' column.
    new_column_name: str, optional argument. The title of the column to add.
                     'Imputed Age', if omitted.
    '''

    # Fill missing spots with average age
    if pd.isnull(age):
        df[new_column_name] = mean_age
    else:
        df[new_column_name] = age

    return df

def association(x, y, df, yates_correction = False, bias_correction = False):
    '''
    For two columns of a Pandas' DataFrame, print:
     - phi coefficient (2 x 2 contingency tables only); apply Yates' correction
       if sample is small;
     - Cramér's V (n x 2 contingency tables, with n > 1);
     - the result of Pearson's test of independence (chi-squared test
       statistic, p-value, theoretical distribution).

    Input
    ---------------------------------------------------------------------------
    x, y: str, required arguments. Pandas' DataFrame column names.
    df: pd.DataFrame, required argument. The input DataFrame.
    yates_correction: bool, optional argument. If True, apply Yates' correction
                      for continuity. Use when at least one cell of the
                      contingency table has an expected count < 5.
    bias_correction: bool, optional argument. If True, apply bias correction to
                     calculate Cramér's V.
    '''

    # Compute contingency table and store values in NumPy 2-D array
    tab = pd.crosstab(df[x], df[y], margins = True)
    n = tab.values

    # Store the dimensions of the contingency table and the total sample size
    n_rows, n_cols = n.shape
    N = n[-1,-1]

    # Calculate phi coefficient iff the shape of the contingency table
    # (marginals excluded) is 2 x 2
    if (n_rows - 1, n_cols - 1) == (2, 2):
        phi = (n[1,1]*n[0,0] - (n[1,0]*n[0,1])) / np.sqrt(n[-1,0]*n[-1,1]\
                                                          *n[0,-1]*n[1,-1])

        print(\
        "Phi coefficient for binary variables '{}' == '{}' and '{}': {:.4f}"\
        .format(x, tab.index[0], y, -phi))
        print(\
        "Phi coefficient for binary variables '{}' == '{}' and '{}': {:.4f}\n"\
        .format(x, tab.index[1], y, phi))

    # Use open multi-dimensional meshgrid to avoid for loops
    i, j = np.ogrid[range(n_rows - 1), range(n_cols - 1)]

    # Compute chi-squared statistic
    chi_squared = np.sum((n[i,j] - (n[i,-1]*n[-1,j])/N)**2 \
                         / ((n[i,-1]*n[-1,j])/N))

    # If True, calculate bias-corrected version of Cramér's V
    if bias_correction:
        phi_squared = np.max([chi_squared / N - (n_cols - 1) * (n_rows - 1) \
                              / (N - 1), 0])
        V = np.sqrt(phi_squared / np.min([n_cols - (n_cols-2) ** 2 / (N-1) \
                                          - 2, n_rows - (n_rows-2) ** 2 / \
                                          (N-1) - 2]))
        print(\
        "Cramér's V for variables '{}' and '{}' (Bias-Corrected): {:.4f}"\
        .format(x, y, V))

    else:
        phi_squared = chi_squared / N
        V = np.sqrt(phi_squared / np.min([n_cols - 2, n_rows - 2]))
        print(\
        "Cramér's V for variables '{}' and '{}' (No Bias Correction): {:.4f}"\
        .format(x, y, V))

    # Pearson's test of independence
    # Return chi-squared test statistic, p-value, and theoretical distribution
    chi2, p, df, ex = sp.stats.chi2_contingency(n, correction = \
                                                yates_correction)

    print("\nPearson's chi-squared test of independence:")
    print('Test statistic: {:.2f}'.format(chi2))
    print('p-value: {:.4e}'.format(p))
    print('Theoretical distribution:\n{}'\
          .format(pd.DataFrame(ex, index = [tab.index[i] for i in \
          range(n_rows)], columns = [tab.columns[i] for i in range(n_cols)])))
