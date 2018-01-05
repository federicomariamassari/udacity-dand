"""Udacity Data Analyst Nanodegree: P1 Compute Statistics From Card Draws

(2017) Federico Maria Massari / federico.massari@bocconialumni.it

Place the module in your working directory and type 'import p1', then call a
particular function using method notation, e.g. p1.deck() to initialise a deck
of cards. Requires Python 3.
"""

def deck():
    """Initialise a deck of cards and return lists of suits and card values."""

    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    cards = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

    return suits, cards

def draw(n_cards, replacement=False):
    """Draw up to n unique cards from a deck with or without replacement.

    Randomly draw n unique cards from a standard deck until the desired number
    (n_cards) is reached.

    Arguments:
        n_cards --- int. A non-negative integer in [0, 52] if 'replacement' is
            omitted or False. A non-negative integer in [0, Inf) otherwise.

    Keyword arguments:
        replacement -- bool. If True, allow for duplicate cards (default False).
    """
    import random

    # If replacement is True, the same card can be picked multiple times
    if replacement:

        # Initialise hand to the empty list (no card picked yet)
        hand = []

        # Append a random card to the hand
        while len(hand) < n_cards:
            hand.append((random.choice(suits), random.choice(cards)))

    else:

        # Initialise hand to the empty set (no card picked yet)
        hand = set()

        # Add n unique cards to the hand, if n is less than or equal to total
        # deck size (52)
        if n_cards > len(suits)*len(cards):
            raise ValueError('Not enough cards in the deck.')
        else:
            while len(hand) < n_cards:
                hand.add((random.choice(suits), random.choice(cards)))

    return hand

def card_values(hand):
    """Extract card values from drawn cards.

    Extract values out of all cards in the hand. Assign numerical value to
    special cards: 'A' = 1, {'J', 'Q', 'K'} = 10. Return value for all others.

    Arguments:
        hand -- list or tuple. Output of the function 'draw'.
    """

    # Extract card values
    card_values = [value for (suit, value) in hand]

    # Convert special card names to values
    card_values = [10 if value in ('J', 'Q', 'K') else 1 if value == 'A' \
                   else value for value in card_values]

    return card_values

def hands(n_cards, k_hands, replacement=False):
    """Draw n cards with or without replacement for each of k hands.

    Randomly draw n cards from the deck until the desired number is reached.
    Repeat the step k times to obtain k distinct hands. Return already converted
    card values. If 'replacement' is omitted or False, the cards are drawn
    without replacement (maximum no. of cards to pick: 52). Otherwise, the cards
    are drawn with replacement (maximum no. of cards to pick: Inf).

    Arguments:
        n_cards -- int. An integer in [0, 52] if 'replacement' is omitted.
            Else, an integer in [0, Inf).
        k_hands -- int. A non-negative integer, the number of hands (i.e.,
            experiment repetitions).

    Keyword arguments:
        replacement -- bool. If True, replace the card in the deck after draw
            (default False)
    """

    # For each of the k hands draw n cards (with or without replacement) and
    # compute their values
    if replacement:
        hands = [card_values(draw(n_cards, True)) for hand in range(k_hands)]
    else:
        hands = [card_values(draw(n_cards)) for hand in range(k_hands)]

    return hands

def sum_hands(hands):
    """Sum card values for each of the k hands.

    Return the sum of the card values, for each of the k hands provided.

    Arguments:
        hands -- list of lists. Output of the function 'hands'.
    """

    # Give me the sum, for each of the hands provided
    sum_hands = [sum(hand) for hand in hands]

    return sum_hands

def histogram(values, title, xlabel, ylabel, step=1, rotation=0, density=False,
              normalised=False):
    """Plot the empirical distribution of card draws.

    Arguments:
        values -- list. Output of either of the two functions: 'card_values',
            'sum_trials'.
        title, xlabel, ylabel -- str. Title and x- and y- labels of the plot.

    Keyword arguments:
        step -- int. Set bin width (default 1).
        rotation -- int. Rotate xticklabels, in degrees. A common alternative
            is 90 (default 0).
        density -- bool. If True, fit a Gaussian pdf to the histogram data
            (default False).
        normalised -- bool. If True, normalise the histogram so that total area
            is equal to 1 (default False).
    """
    import numpy as np
    from scipy import stats
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import seaborn as sns

    # Define figure size and Axes class (use object-oriented methods)
    plt.figure(figsize=(6,6))
    ax = plt.axes()

    # If True, fit a Gaussian density to data and plot it against the histogram
    if density:

        # Automatically normalise the histogram to ensure correct density
        # visualisation
        bins = np.arange(0, np.max(values) + 2, step) - 0.5*step
        ax.hist(values, bins=bins, edgecolor='k', normed=True)

        # Retrieve density parameters mu and sigma from input data
        mu, sigma = stats.norm.fit(values)

        # Generate x-axis values for the density, set to 1000 to ensure
        # smoothness
        x = np.linspace(np.min(values) - 0.5*step, np.max(values) + 0.5*step, \
                        1000)

        # Generate density values for each provided x-axis value
        y = mlab.normpdf(x, mu, sigma)

        # Plot the density over the histogram
        density = ax.plot(x, y)

    else:

        # Return either normalised or non-normalised histogram, based on user
        # input
        bins = np.arange(0, np.max(values) + 2, step) - 0.5*step
        ax.hist(values, bins=bins, edgecolor='k', normed=normalised)

    # Add title and axes labels
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Define x-axis limits
    ax.set_xlim(np.min(values) - 0.5*step, np.max(values) + 0.5*step)

    # Set x-axis ticks and rotate labels, if applicable
    xticks = np.arange(np.min(values), np.max(values) + 1, step)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, rotation=rotation)

def statistics(draws, df=0, sample_bias=True, output=False):
    """Print measures of location, scale, and shape.

    Calculate and print useful measures of location (mean, median), scale
    (standard deviation, interquartile range), and shape (skewness, excess
    kurtosis).

    Arguments:
        draws -- list. Output of either function: 'card_values', 'sum_trials'.

    Keyword arguments:
        df -- int. Number of degrees of freedom. Input 1 for Bessel's correction
            for finite samples (default 0).
        sample_bias -- bool. If False, provides sample bias correction for
            skewness and excess kurtosis (default True).
        output -- bool. If True, the function also returns mean and standard
            deviation of the data (default False).
    """
    import numpy as np
    from scipy import stats

    mean = np.average(draws)
    median = np.median(draws)

    # Measures of dispersion (scale)
    standard_deviation = np.std(draws, ddof=df)
    q25, q75 = np.percentile(draws, [25, 75])

    # Measure of shape
    skewness = stats.skew(draws, bias=sample_bias)
    excess_kurtosis = stats.kurtosis(draws, bias=sample_bias)

    # Print statistics in a user-friendly format
    print('Mean: {:.2f}'.format(mean))
    print('Median: {:.2f}'.format(median))
    print('Standard deviation: {:.2f}'.format(standard_deviation))
    print('Skewness: {:.4f}'.format(skewness))
    print('Excess kurtosis: {:.4f}'.format(excess_kurtosis))
    print('Interquartile range: {:.0f} - {:.0f} = {:.0f}'\
          .format(q75, q25, q75 - q25))

    # Also return mean and standard deviation if set to True
    if output:
        return mean, standard_deviation

def confidence_interval(m, s, n, alpha):
    """Print confidence intervals for the mean with unknown population variance.

    Compute and print confidence intervals for the mean when population variance
    is unknown.

    Arguments:
        m -- float. The sample mean, output of the function 'statistics'.
        s -- float. The sample standard deviation, also an output of the
            function 'statistics'.
        n -- int. The sample size.
        alpha -- float. The significance level, alpha in [0, 1], e.g.
            alpha = 0.05 for the 95% c.l.
    """
    import numpy as np
    from scipy import stats

    # Compute one-tailed Student's t quantile with (0.5 * alpha) significance
    # per tail, n - 1 degrees of freedom
    t = stats.t.ppf(1 - (0.5*alpha), n - 1)

    # Compute lower and upper confidence intervals for the mean
    lower = m - t * s/np.sqrt(n)
    upper = m + t * s/np.sqrt(n)

    print('{:.0f}% confidence interval for the population mean:\n'\
          .format((1-alpha) * 100))
    print('Sample size: {:.0f}'.format(n))
    print('Sample mean: {:.2f}'.format(m))
    print('Sample standard deviation: {:.2f}'.format(s))
    print('\n(lower; upper) = ({:.4f}; {:.4f})'.format(lower, upper))

def tcdf(x, m, s, n, upper=False):
    """Compute Student's t cumulative distribution function (cdf).

    Compute Student's t cumulative distribution function, F(x) = P(X <= x).
    Compute 1 - F(x)if upper = True.

    Arguments:
        x -- int or float. Realisation of random variable X.
        m -- float. The sample mean, output of the function 'statistics'.
        s -- float. The sample standard deviation, output of the function
            'statistics'.
        n: int. The sample size.

    Keyword arguments:
        upper: bool. If True, print 1 - F(x) = P(X >= x) (default False).
    """
    from scipy import stats

    # If upper is set to True, compute 1 - F(x); else, compute F(x)
    if upper:
        tcdf = 1 - stats.t.cdf(x, n - 1, m, s)
        print('P(X >= %s) = %.4f'%(x, tcdf))
    else:
        tcdf = stats.t.cdf(x, n - 1, m, s)
        print('P(X <= %s) = %.4f'%(x, tcdf))
