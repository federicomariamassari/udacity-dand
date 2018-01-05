"""Udacity Data Analyst Nanodegree: P2 Investigate a Dataset

(2017) Federico Maria Massari / federico.massari@bocconialumni.it

Place the module in your working directory and type 'import p2', then call a
particular function using method notation. Requires Python 3.
"""

def age_of_majority(df, age, new_column_name='Minor/Adult'):
    """Label passenger as 'Minor' or 'Adult' based on age and ignoring NaNs.

    Arguments:
        df -- pd.DataFrame. Pandas' input DataFrame.
        age -- int or float. The age of the passenger, in years.

    Keyword arguments:
        new_column_name -- str. Title of column to add (default 'Minor/Adult').
    """
    import pandas as pd

    # Ignore missing values
    if pd.notnull(age):

        if age < 18:
            df[new_column_name] = 'Minor'
        else:
            df[new_column_name] = 'Adult'

    return df

def count_unique(df, column_name, new_column_name):
    """Count occurrences of unique entries and map results.

    Count the occurrences of unique objects in a DataFrame column, maps the
    results to each item, and stores them in a new column.

    Arguments:
        df -- pd.DataFrame. The DataFrame to expand.
        column_name -- str. The name of the column from which to count the
            occurrences.
        new_column_name -- str. The name of the new column in which to store
            the results.
    """
    import pandas as pd

    # Count unique object occurrences and stores them in a Python dictionary
    counter = df[column_name].value_counts().to_dict()

    # Map the results to each object and store the results in a new DataFrame
    # column
    df[new_column_name] = df[column_name].map(counter)

    return df

def travels_with_spouse(df, title, sib_sp, name_count,
                        new_column_name='Spouse Aboard'):
    """Check whether a passenger is travelling with a spouse.

    Arguments:
        df -- pd.DataFrame. The input DataFrame.
        title, sib_sp, name_count -- pd.Series. DataFrame columns containing,
            in each row, passenger title, number of siblings/spouse onboard the
            Titanic, and number of occurrences of his/her first name.

    Keyword arguments:
        new_column_name -- str. Title of column to add (default 'Spouse Aboard')
    """
    import pandas as pd

    if (title in ['Mrs', 'Mr', 'Dr']) & (sib_sp > 0) & (name_count == 2):
        df[new_column_name] = True
    else:
        df[new_column_name] = False

    return df

def replace_title(title):
    """Shrink the total number of honorifics in a dataset.

    Arguments:
        title -- str. The honorific to evaluate.
    """
    import pandas as pd

    if title in ['Mlle']:
        return 'Miss'
    elif title in ['the Countess', 'Lady', 'Mme', 'Ms']:
        return 'Mrs'
    elif title in ['Capt', 'Col', 'Don', 'Jonkheer', 'Major', 'Master', 'Sir']:
        return 'Mr'
    else:
        return title

def imputed_age(df, age, mean_age, new_column_name='Imputed Age'):
    """Replace missing 'Age' values with sample mean and store in a new column.

    Arguments:
        df -- pd.DataFrame. The input DataFrame.
        age -- int or float. The age of the passenger, in years.
        mean_age -- int or float. Average age in the 'Age' column.

    Keyword arguments:
        new_column_name -- str. Title of column to add (default 'Imputed Age').
    """
    import pandas as pd

    # Fill missing spots with average age
    if pd.isnull(age):
        df[new_column_name] = mean_age
    else:
        df[new_column_name] = age

    return df

def association(x, y, df, yates_correction=False, bias_correction=False):
    """Print phi coefficient, Cramér V and Pearson's independence test result.

    For two columns of a Pandas' DataFrame, print:
    - phi coefficient (2 x 2 contingency tables only); apply Yates' correction
      if sample is small;
    - Cramér's V (n x 2 contingency tables, with n > 1);
    - the result of Pearson's test of independence (chi-squared test statistic,
      p-value, theoretical distribution)

    Arguments:
        x, y -- str. Pandas' DataFrame column names.
        df -- pd.DataFrame. The input DataFrame.

    Keyword arguments:
        yates_correction -- bool. If True, apply Yates' correction for
            continuity. Use when at least one cell of the contingency table has
            an expected count < 5 (default False).
        bias_correction -- bool. If True, apply bias correction to calculate
            Cramér's V (default False).
    """
    import numpy as np
    import scipy as sp
    import pandas as pd

    # Compute contingency table and store values in NumPy 2-D array
    tab = pd.crosstab(df[x], df[y], margins=True)
    n = tab.values

    # Store the dimensions of the contingency table and the total sample size
    n_rows, n_cols = n.shape
    N = n[-1, -1]

    # Calculate phi coefficient iff the shape of the contingency table
    # (marginals excluded) is 2 x 2
    if (n_rows - 1, n_cols - 1) == (2, 2):
        phi = (n[1, 1] * n[0, 0] - (n[1, 0] * n[0, 1])) / \
                np.sqrt(n[-1, 0] * n[-1, 1] * n[0, -1] * n[1, -1])

        print("Phi coefficient for binary variables '{}' == '{}' and '{}': \
{:.4f}".format(x, tab.index[0], y, -phi))
        print("Phi coefficient for binary variables '{}' == '{}' and '{}': \
{:.4f}\n".format(x, tab.index[1], y, phi))

    # Use open multi-dimensional meshgrid to avoid for loops
    i, j = np.ogrid[range(n_rows - 1), range(n_cols - 1)]

    # Compute chi-squared statistic
    chi_squared = np.sum((n[i, j] - (n[i, -1] * n[-1, j]) / N) ** 2 / \
        ((n[i, -1] * n[-1, j]) / N))

    # If True, calculate bias-corrected version of Cramér's V
    if bias_correction:
        phi_squared = np.max([chi_squared / N \
            - (n_cols - 1) * (n_rows - 1) / (N - 1), 0])
        V = np.sqrt(phi_squared / np.min([n_cols - (n_cols - 2) ** 2 / \
            (N - 1) - 2, n_rows - (n_rows - 2) ** 2 / (N - 1) - 2]))
        print("Cramér's V for variables '{}' and '{}' (Bias-Corrected): \
{:.4f}".format(x, y, V))

    else:
        phi_squared = chi_squared / N
        V = np.sqrt(phi_squared / np.min([n_cols - 2, n_rows - 2]))
        print("Cramér's V for variables '{}' and '{}' (No Bias Correction): \
{:.4f}".format(x, y, V))

    # Pearson's test of independence
    # Return chi-squared test statistic, p-value, and theoretical distribution
    chi2, p, df, ex = sp.stats.chi2_contingency(n,
        correction=yates_correction)

    print("\nPearson's chi-squared test of independence:")
    print('Test statistic: {:.2f}'.format(chi2))
    print('p-value: {:.4e}'.format(p))
    print('Theoretical distribution:\n{}'.format(pd.DataFrame(ex, \
        index=[tab.index[i] for i in range(n_rows)],
        columns=[tab.columns[i] for i in range(n_cols)])))
