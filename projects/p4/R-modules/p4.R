# Run while "R-modules" is the current working directory
system("python3 ../python-modules/get_xls.py")
system("python3 ../python-modules/scrape_wikipedia.py")

# Import libraries
library(ggplot2)
library(dplyr)
library(gridExtra)

# Import file content as data frames
greatest_pt1 <- readxl::read_excel("../data/xls/1000GreatestFilms.xls")
greatest_pt2 <- readxl::read_excel("../data/xls/Films-Ranked-1001-2000.xls")
gdp <- read.csv("../data/csv/gdp.csv")
continents <- read.csv("../data/csv/continents.csv")
world <- map_data("world")
