'''
A Python module containing the core functions of 'P1 Compute Statistics from
Card Draws', Udacity Data Analyst Nanodegree, 2017, by Federico Maria Massari
(federico.massari@bocconialumni.it). Requires Python 3+.

Place the module in your working directory and type 'import p1', then call a
particular function using method notation, e.g. p1.deck() to initialise a deck
of cards.

To be able to use the module, you should:

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import seaborn as sns
from scipy import stats
'''

def deck():
    '''
    Initialise a deck of cards. Return separate lists of suits and card values.

    Input
    ----------------------------------------------------------------------------
    No input required.
    '''

    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    cards = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

    return suits, cards

def draw(n_cards, replacement = False):
    '''
    Randomly draw n unique cards from a standard deck until the desired number
    (n_cards) is reached.

    Input
    ----------------------------------------------------------------------------
    n_cards: int, required argument. A non-negative integer in [0, 52] if
             'replacement' is omitted or False. A non-negative integer in
             [0, Inf) if 'replacement' is True.
    '''

    # If replacement is True, the same card can be picked multiple times
    if replacement:

        # Initialise hand to the empty list (no card picked yet)
        hand = []

        # Append a random card to the hand
        while len(hand) < n_cards:
            hand.append([random.choice(suits), random.choice(cards)])

    else:

        # Initialise hand to the empty set (no card picked yet)
        hand = set()

        # Add n unique cards to the hand, if n is a number smaller than or
        #equal to total deck size (52)
        if n_cards > len(suits) * len(cards):
            raise ValueError('Not enough cards in the deck.')
        else:
            while len(hand) < n_cards:
                hand.add((random.choice(suits), random.choice(cards)))

    return hand

def card_values(hand):
    '''
    Extract values out of all cards in the hand. Assign numerical value to
    special cards: 'A' = 1, {'J', 'Q', 'K'} = 10. Return value for all others.

    Input
    ----------------------------------------------------------------------------
    hand: list or tuple, required argument. Output of the function 'draw'.
    '''

    # Extract card values
    card_values = [value for (suit, value) in hand]

    # Convert special card names to values
    card_values = [10 if value in ('J', 'Q', 'K') else 1 if value == 'A' \
                   else value for value in card_values]

    return card_values

def hands(n_cards, k_hands, replacement = False):
    '''
    Randomly draw n cards from the deck until the desired number is reached.
    Repeat the step k times to obtain k distinct hands. Return already
    converted card values. If 'replacement' is omitted or False, cards are
    drawn without replacement (maximum number of cards to pick: 52).
    If replacement is set to True, cards are drawn with replacement (maximum
    number of cards to pick: Inf).

    Input
    ----------------------------------------------------------------------------
    n_cards: int, required argument. An integer in [0, 52] if replacement is
             omitted. An integer in [0, Inf) otherwise.
    k_hands: int, required argument. A non-negative integer, the number of
             hands (experiment repetitions).
    replacement: bool, optional argument. If True, replace the card in deck
                 after draw. Default is False.
    '''

    # For each of the k hands draw n cards (with or without replacement) and
    # compute their values
    if replacement:
        hands = [card_values(draw(n_cards, True)) for hand in range(k_hands)]
    else:
        hands = [card_values(draw(n_cards)) for hand in range(k_hands)]

    return hands

def sum_hands(hands):
    '''
    Return the sum of the card values, for each of the k hands provided.

    Input
    ----------------------------------------------------------------------------
    hands: list of lists, required argument. Output of the function 'hands'.
    '''

    # Give me the sum, for each of the hands provided
    sum_hands = [sum(hand) for hand in hands]

    return sum_hands

def histogram(values, title, xlabel, ylabel, step = 1, rotation = 0,
              density = False, normalised = False):
    '''
    Plot the empirical distribution of card draws.

    Input
    ----------------------------------------------------------------------------
    values: list, required argument. Output of either function: 'card_values',
            'sum_trials'.
    title, xlabel, ylabel: str, required arguments. Title and x- and y- labels
                           of the plot.
    step: int, optional argument. Set bin width. Default value is 1.
    rotation: int, optional argument. Rotate xticks, in degrees. Default value
              is 0. Common alternative 90.
    density: bool, optional argument. If True, fit a Gaussian pdf to the
             histogram data. Default value is False.
    normalised: bool, optional argument. If True, normalise the histogram so
                that total area is equal to 1. Must be True if density is True,
                otherwise an exception is raised.
    '''

    # Plot histogram, create and centre the bins, normalise area if applicable
    plt.figure(figsize = (7,7))
    plt.hist(values, bins = np.arange(0, max(values)+2, step) - 0.5*step,
             normed = normalised)

    # Add title and axes labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Set x-axis ticks and rotate them, if applicable
    plt.xticks(np.arange(min(values), max(values)+1, step),
               rotation = rotation)

    # Define x-axis limits
    plt.xlim(min(values) - 0.5*step, max(values) + 0.5*step)

    # Fit Gaussian density to data and plot it against the histogram, if
    # applicable
    if density:

        # If normalised is also set to True, run the code, else raise exception
        if normalised:

            # Retrieve density parameters mu and sigma from input data
            mu, sigma = stats.norm.fit(values)

            # Generate x-axis values for the density, set to 1000 to ensure
            # smoothness
            x = np.linspace(min(values) - 0.5*step, max(values) + 0.5*step,
                            1000)

            # Generate density values for each provided x-axis value
            y = mlab.normpdf(x, mu, sigma)

            # Plot the density over the histogram
            density = plt.plot(x, y)

        else:
            raise ValueError('normalised must be True if density is True.')

def statistics(draws, df = 0, sample_bias = True, output = False):
    '''
    Calculate and print useful measures of location (mean, median), scale
    (standard deviation, interquartile range), and shape (skewness, excess
    kurtosis).

    Input
    ----------------------------------------------------------------------------
    draws: list, required argument. Output of either function: 'card_values',
           'sum_trials'.
    df: int, optional argument. Number of degrees of freedom. Default value is
        0 (population), input 1 for Bessel's correction for finite samples.
    sample_bias: bool, optional argument. If False, provides sample bias
                 correction for skewness and excess kurtosis. Default value is
                 True.
    output : bool, optional argument. If True, the function returns mean and
             standard deviation of the data. Default value is False.
    '''

    # Measures of central tendency (location)
    mean = np.average(draws)
    median = np.median(draws)

    # Measures of dispersion (scale)
    standard_deviation = np.std(draws, ddof = df)
    q25, q75 = np.percentile(draws, [25, 75])

    # Measure of shape
    skewness = stats.skew(draws, bias = sample_bias)
    excess_kurtosis = stats.kurtosis(draws, bias = sample_bias)

    # Print statistics in a user-friendly format
    print('\nMean: {:.2f}'.format(mean))
    print('Median: {:.2f}'.format(median))
    print('Standard deviation: {:.2f}'.format(standard_deviation))
    print('Skewness: {:.4f}'.format(skewness))
    print('Excess kurtosis: {:.4f}'.format(excess_kurtosis))
    print('Interquartile range: {:.0f} - {:.0f} = {:.0f}'\
          .format(q75, q25, q75-q25))

    # Also return mean and standard deviation if set to True
    if output:
        return mean, standard_deviation

def confidence_interval(m, s, n, alpha):
    '''
    Compute and print confidence intervals for the mean when population
    variance is unknown.

    Input
    ----------------------------------------------------------------------------
    m: float, required argument. The sample mean, output of the function
       'statistics'.
    s: float, required argument. The sample standard deviation, also an output
       of the function 'statistics'.
    n: int, required argument. The sample size.
    alpha: float, required argument. The significance level, alpha in [0, 1],
           e.g. alpha = 0.05 for the 95% c.l.
    '''

    # Compute one-tailed Student's t quantile with (0.5 * alpha) significance
    # per tail, n - 1 degrees of freedom
    t = stats.t.ppf(1 - (0.5 * alpha), n - 1)

    # Compute lower and upper confidence intervals for the mean
    lower = m - t * s / np.sqrt(n)
    upper = m + t * s / np.sqrt(n)

    print('\n{:.0f}% confidence interval for the population mean:\n'\
          .format((1-alpha) * 100))
    print('Sample size: {:.0f}').format(n)
    print('Sample mean: {:.2f}').format(m)
    print('Sample standard deviation: {:.2f}').format(s)
    print('\n(lower; upper) = ({:.4f}; {:.4f})'.format(lower, upper))

def tcdf(x, m, s, n, upper = False):
    '''
    Compute Student's t cumulative distribution function, F(x) = P(X <= x).
    Compute 1 - F(x) if upper = True.

    Input
    ----------------------------------------------------------------------------
    x: int or float, required argument. Realisation of random variable X.
    m: float, required argument. The sample mean, output of the function
       'statistics'.
    s: float, required argument. The sample standard deviation, also an output
       of the function 'statistics'.
    n: int, required argument. The sample size.
    upper: bool, optional argument. If set to True, print 1 - F(x) = P(X > x).
           Default value is False.
    '''

    # If upper is set to True, compute 1 - F(x); else, compute F(x)
    if upper:
        tcdf = 1 - stats.t.cdf(x, n - 1, m, s)
        print('\nP(X > %s) = %.4f'%(x, tcdf))
    else:
        tcdf = stats.t.cdf(x, n - 1, m, s)
        print('\nP(X <= %s) = %.4f'%(x, tcdf))
