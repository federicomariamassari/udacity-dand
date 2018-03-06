# Run while "R-modules" is the current working directory
system("python3 ../python-modules/get_xls.py")
system("python3 ./python-modules/scrape_webpage.py")
system("python3 ../python-modules/scrape_wikipedia.py")

# Import frequently used libraries
library(ggplot2)
library(dplyr)
library(gridExtra)

# Import file contents as data frames
greatest_pt1 <- readxl::read_excel("./data/xls/1000GreatestFilms.xls")
greatest_pt2 <- readxl::read_excel("./data/xls/Films-Ranked-1001-2000.xls")
directors <- read.csv("./data/csv/top_250_directors.csv")
continents <- read.csv("./data/csv/continents.csv")
gdp <- read.csv("./data/csv/gdp.csv")

# Import world map from ggplot2 library
world <- map_data("world")

# Uniform the data frames, append pt2 to pt1
greatest <- rbind(greatest_pt1[, -c(2:3)], greatest_pt2)

# Remove single files to free up space
rm(greatest_pt1, greatest_pt2)

# Single-out main Country of production
greatest$region <- stringr::str_split_fixed(greatest$Country, "-", 2)[,1]

# Convert to factors (before: chr)
world$region <- factor(world$region)
greatest$region <- factor(greatest$region)

# Add factor levels
levels(greatest$region) <- c(levels(greatest$region),
c("China", "Czech Republic", "Serbia"))

# Automate factor renaming
rename_factor <- function(df_column, old_name, new_name) {
    # Rename data frame factor.
    #
    # Arguments:
    #   df_column: The factor column.
    #   old_name: The factor name to replace.
    #   new_name: The new factor name.
    #
    # Returns:
    #   A data frame column with replaced factor name.
    df_column[df_column == old_name] <- new_name
    return(df_column)
}

# Uniform names with those of world map
old_names <- c("Czechoslovakia", "Hong Kong", "USSR", "West Germany",
"Yugoslavia")
new_names <- c("Czech Republic", "China", "Russia", "Germany", "Serbia")

for (i in 1:length(old_names)) {
    greatest$region <- rename_factor(greatest$region, old_names[i], new_names[i])
}

make_chart <- function(df, column, column_id) {
    # Create a dplyr summary chart with custom column names [1].
    #
    # Arguments:
    #   df: The data frame to summarise.
    #   column: The df column to "group_by".
    #   column_id: A string label to uniquely identify the columns.
    #
    # Returns:
    #   A summary table with log10, log2, and level transformations.
    #
    # References:
    #   [1] http://dplyr.tidyverse.org/articles/programming.html
    
    # Create quosure to use dplyr in function environment
    column <- enquo(column)
    
    # Unquote (evaluate immediately) quosure expression
    df_out <- df %>%
    group_by(!!column) %>%
    summarise(n = n())
    
    # Conveniently group and label factor levels
    df_out$bin <- cut(df_out$n, breaks = c(-Inf, 1,  10, 50, 100, +Inf))

    levels(df_out$bin) <- c("Single", "From 2 to 10", "From 11 to 50",
                            "From 51 to 100", "More than 100")
    
    
    
    # Uniquely label columns using an identifier
    cols <- c("n", "log10", "log2", "bin")
    
    for (i in 1:length(cols)) {
        colnames(df_out)[i+1] <- c(paste(cols[i], column_id, sep = "_"))
    }
    
    return(df_out)
}


