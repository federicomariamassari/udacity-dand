# Udacity Data Analyst Nanodegree
My Udacity Data Analyst Nanodegree projects. In Python, unless otherwise stated.

## P1 [Compute Statistics from Card Draws](https://nbviewer.jupyter.org/github/federicomariamassari/udacity-dand/blob/master/projects/p1/dand-p1-compute-statistics-from-card-draws.ipynb)

__Completion time:__ 5 days

### Overview
_In this project, you will demonstrate your knowledge of descriptive statistics by conducting an experiment dealing with drawing from a deck of playing cards and creating a write up containing your findings._

This is a practical application of the __central limit theorem__. I generate a deck of cards, draw randomly from it, analyse the distribution of outcomes, compute basic statistics and, if applicable, provide confidence intervals for the population mean when only sample moments are available, as well as the cumulative distribution function for a random variable X, F(x) = P(X ≤ x), the probability of it being below a certain threshold value x.

### What was the biggest challenge?
Dealing with the replacement option, which impacts on the random card drawing algorithm. I took advantage of Python's definition of `set` and `list` as collections of, respectively, unique and repeatable objects. For `replacement == False`, I initialised the hand to the empty set, so that no two identical cards could be drawn; I also limited the maximum number of cards to pick to 52. For `replacement == True`, instead, I initialised the hand to the empty list, so that the same card could be drawn multiple times; I also removed the 52-card constraint.

### Which part of the code do you like best?
The deck generating process. In particular, the way suits and values are stored in different variables, then randomly paired by the card drawing algorithm. I believe this procedure is very intuitive and neat.

[Link to Python module](/projects/p1/python-modules/p1.py)

## P2 [Investigate a Dataset](https://nbviewer.jupyter.org/github/federicomariamassari/udacity-dand/blob/master/projects/p2/dand-p2-investigate-a-dataset.ipynb)

__Completion time:__ 21 days

### Overview
_Choose one of Udacity's curated datasets and investigate it using NumPy and Pandas. Go through the entire data analysis process, starting by posing a question and finishing by sharing your findings._

Digging into the __Titanic dataset__, I go through all the steps involved in a typical data analysis process: formulate questions, wrangle (acquire and clean data), explore, draw conclusions, and communicate findings. I mainly use Pandas to store and handle data in tables, SciPy to detect statistical association among variables, and Seaborn to produce plots.

### What was the biggest challenge?
Performing meaningful tests of association between _binary variables_ and plotting the results, offering enough plot variety. Binary variables are challenging for two reasons: on one hand, they make the correlation coefficient difficult to interpret; on the other, very few plot types are suitable to visualise their relationship. To measure the degree of association between variables, I resorted to _contingency tables_, _phi coefficients_ (binary-to-binary) and _Cramér's V_ (nominal-to-binary). To display such association, I experimented with various Seaborn plots: swarm, strip, violin, and joint, among the others.

### Which part of the code do you like best?
Function `association`, which returns phi coefficients (if applicable), Cramér's V, and the result of Pearson's test of independence. For the first two statistics no built-in Python function was available, so I had to define my own.

[Link to Python module](/projects/p2/python-modules/p2.py)
