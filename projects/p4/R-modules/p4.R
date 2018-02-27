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

# Uniform the data frames, append pt2 to pt1
greatest <- rbind(greatest_pt1[, -c(2:3)], greatest_pt2)

# Remove single files to free up space
rm(greatest_pt1, greatest_pt2)

# Single-out main country of production
greatest$region <- stringr::str_split_fixed(greatest$Country, "-", 2)[,1]

# Convert to factors (before: chr)
world$region <- factor(world$region)
greatest$region <- factor(greatest$region)

# Add factor levels
levels(greatest$region) <- c(levels(greatest$region),
c("China", "Czech Republic", "Serbia"))
