Previous: [P3 Wrangle OpenStreetMap](https://github.com/federicomariamassari/udacity-dand/blob/master/projects/p3/dand-p3-wrangle-openstreetmap.md) | [Table of Contents](https://github.com/federicomariamassari/udacity-dand/blob/master/README.md) | Next:
# Data Analyst Nanodegree: P4 Explore and Summarise Data
__Federico Maria Massari / federico.massari@bocconialumni.it__

The project is connected to the course _[Data Analysis with R](https://eu.udacity.com/course/data-analysis-with-r--ud651)_.

__Datasets__
- _[TheyShootPictures.com](http://www.theyshootpictures.com)_ — The 2,000 Greatest Films, Top 250 Directors;
- _Wikipedia_: List of Countries by continent; Percentage of GDP to the Service sector by Country.

## Introduction
To acquire and partially clean the data I used Python's `requests` and `BeautifulSoup` modules. Additional processing (e.g., uniforming and merging data frames, adding and replacing factor levels) was done in R.

Auxiliary data are retrieved from Wikipedia.

## Geography of the greatest movies
Let's have a quick and dirty look to the contribution by Country.

We first consider the main Country of production only. __Figure 1__ shows that:

- Only three Countries contributed, single handedly, more than 100 movies to the list: these are the United States, France, and the United Kingdom;
- North America and Oceania are the most represented continents (i.e., with the greatest area covered), followed by Europe;
- Africa, by contrast, is the least represented continent, with both the lowest number of Countries and that of movies in the list;
- The choropleth map of Asia (excluding South-East Asia) is pretty uniform, as most Countries in the region contributed between 11 and 100 movies.

<img align="center" src="./img/figure-01.png"/>

Does something change when co-production contributions are included in the map? __Figure 2__ shows that little does.

- Now Germany, Italy, and Japan also total more than 100 movies in the list;
- South-East Asia is now slightly more represented, with the inclusion of Bangladesh and Vietnam (with a single movie each);
- Africa remains the least represented continent; although six new Countries make it into the list (Algeria, Burkina Faso, Cameroon, Mauritania, Morocco, Tunisia), all do with very few contributions (1-2).

<img align="center" src="./img/figure-02.png"/>

We have seen the geographic distribution of the greatest movies. But _how many_ movies did these Countries actually produce? __Figure 3__ exactly shows this magnitude:

- By far, the largest contributor is the United States, with over 800 movies (over 900 if co-productions are also included). France follows, with half that figure;
- The only African Country contributing more than two movies is Senegal (5-10);

<img align="center" src="./img/figure-03.png"/>

<img align="center" src="./img/figure-04.png"/>

```
y <- Resources destined to the service sector, as a percentage of Country GDP
x <- Number of movies produced by Country

Call:
lm(formula = y ~ x)

Residuals:
     Min       1Q   Median       3Q      Max
-26.5737  -5.8390   0.8142   4.9851  27.3688

Coefficients:
            Estimate Std. Error t value Pr(>|t|)    
(Intercept)   56.442      2.057  27.437  < 2e-16 ***
x              7.272      1.776   4.094 0.000129 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Residual standard error: 9.959 on 60 degrees of freedom
Multiple R-squared:  0.2183,	Adjusted R-squared:  0.2053
F-statistic: 16.76 on 1 and 60 DF,  p-value: 0.0001288
```
