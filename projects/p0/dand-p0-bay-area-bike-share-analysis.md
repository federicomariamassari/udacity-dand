[Table of Contents](https://github.com/federicomariamassari/udacity-dand/blob/master/README.md) | Next: [P1 Compute Statistics from Card Draws](https://nbviewer.jupyter.org/github/federicomariamassari/udacity-dand/blob/master/projects/p1/dand-p1-compute-statistics-from-card-draws.ipynb)
# Data Analyst Nanodegree: P0 Bay Area Bike Share Analysis
__Federico Maria Massari / federico.massari@bocconialumni.it__
## Introduction
[Bay Area Bike Share](https://www.fordgobike.com) (now _Ford GoBike_) provides on-demand bike rentals for customers in San Francisco, Redwood City, Palo Alto, Mountain View, and San Jose. Users can unlock bikes from various stations throughout each city, and return them to any station within the same city. Clients pay for the service either through a yearly subscription or by purchasing a 24-hour or 3-day pass. Under service conditions, they can make an unlimited number of trips: trips under thirty minutes in length have no additional charge, longer trips will incur overtime fees.

__Figure 1__ maps all Bay Area Bike Share stations available in the period 8-29-13 (inception date) to 8-29-15.

<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 1: Maps of Bay Area Bike Share stations</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
  <td align="center"><b>Figure 1.A</b>: Stations throughout California<img align="center"></td>
  <td align="center"><b>Figure 1.B</b>: Stations in the San Francisco Bay Area<img align="center"></td>
  <tr>
  </tr>
  <tr>
    <td align="center"><img align="center" src="./img/babs-full.png"/></td>
    <td align="center"><img align="center" src="./img/babs-sf.png"/></td>
  </tr>
</table>

### Individual trips by subscription type

<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 2: Statistics of trips by subscription type</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
  <td align="center"><b>Figure 2.A</b>: Number of trips<img align="center"></td>
  <td align="center"><b>Figure 2.B</b>: Boxplot of trip duration (minutes)<img align="center"></td>
  <tr>
  </tr>
  <tr>
    <td align="center"><img align="center" src="./img/trips_by_subtype.png"/></td>
    <td align="center"><img align="center" src="./img/boxplot.png"/></td>
  </tr>
</table>

### Daily and weekly use
__Annual subscribers.__ As Tyler pointed out, annual subscribers are generally workers who use the service from Monday to Friday, at around 8-9am and 5-6pm (_Figure 3_). A few (but not as many as he found out) also use it to go to lunch, at 12 noon.
<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 3: Daily and weekly habits of annual subscribers</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
  <td align="center"><b>Figure 3.A</b>: Number of trips by hour<img align="center"></td>
  <td align="center"><b>Figure 3.B</b>: Number of trips by weekday<img align="center"></td>
  <tr>
  </tr>
  <tr>
    <td align="center"><img align="center" src="./img/trips_hour_subs.png"/></td>
    <td align="center"><img align="center" src="./img/trips_week_subs.png"/></td>
  </tr>
</table>

__Customers.__ Casual riders generally use the service on weekends and, in Tyler's words, their hourly usage falls along a bell-shaped distribution, with a peak at 2pm (_Figure 4_). Also, on weekends, both the number of customers and that of subscribers renting a bike are the same, approximately 20-22k.
<table>
  <tr>
      <td align="center" colspan="2"><b>Figure 4: Daily and weekly habits of customers</b></td>
  </tr>
  <tr>
  </tr>
  <tr>
  <td align="center"><b>Figure 4.A</b>: Number of trips by hour<img align="center"></td>
  <td align="center"><b>Figure 4.B</b>: Number of trips by weekday<img align="center"></td>
  <tr>
  </tr>
  <tr>
    <td align="center"><img align="center" src="./img/trips_hour_cust.png"/></td>
    <td align="center"><img align="center" src="./img/trips_week_cust.png"/></td>
  </tr>
</table>

[Table of Contents](https://github.com/federicomariamassari/udacity-dand/blob/master/README.md) | Next: [P1 Compute Statistics from Card Draws](https://nbviewer.jupyter.org/github/federicomariamassari/udacity-dand/blob/master/projects/p1/dand-p1-compute-statistics-from-card-draws.ipynb)
