# Udacity Data Analyst Nanodegree - P4 Explore and Analyse Data

# DATA ACQUISITION

# Run this command while "p4" is the current working directory
modules <- c("get_xls.py", "scrape_webpage.py", "scrape_wikipedia.py",
             "scrape_others.py")
sapply(modules,
       function(x) system(paste("python3 ./python-modules/", x, sep = "")))

# Import frequently used libraries
libraries <- c("dplyr", "ggplot2", "kableExtra")
sapply(libraries, require, character.only = TRUE)

# Import main files as data frames
greatest_pt1 <- readxl::read_excel("./data/xls/1000GreatestFilms.xls")
greatest_pt2 <- readxl::read_excel("./data/xls/Films-Ranked-1001-2000.xls")
directors <- read.csv("./data/csv/top_250_directors.csv")

# Import auxiliary documents as data frames
variables <- c("continents", "coordinates", "country_area", "country_codes",
"religions", "nominal_gdp", "gdp_by_sector")

for (variable in variables) {
    assign(variable, read.csv(paste("./data/csv/", variable, ".csv", sep = "")))
}

# Import world map from ggplot2 library
world <- filter(map_data("world"), region != "Antarctica")

# Uniform the data frames, append pt2 to pt1
greatest <- rbind(greatest_pt1[, -c(2:3)], greatest_pt2)

# DATA CLEANING

# (1) Character-to-factor conversion
convert.to.factor <- function(df) {
    # Convert all "chr" columns of a data frame to "Factor".
    #
    # Arguments:
    #   df: Data frame with columns of type "chr" to convert to "Factor".
    #
    # Returns:
    #   Data frame df with converted column types.
    #
    df <- as.data.frame(unclass(df))
    return(df)
}

world <- convert.to.factor(world)
greatest <- convert.to.factor(greatest)

# (2)Factor level inclusion
# Distinguish between China and Hong Kong at level "region"
levels(world$region) <- c(levels(world$region), "Hong Kong")
index <- as.numeric(rownames(subset(world, subregion == "Hong Kong")))
world[index, ]$region <- "Hong Kong"

# Add new row related to Hong Kong in auxiliary data frame
continents <- rbind(continents,
data.frame(Continent = "Asia", Country = "Hong Kong"))

# (3) Rename columns
world <- rename(world, Country = region)
greatest <- rename(greatest, Countries = Country)
directors <- rename(directors, Dir.Rank = Rank)
