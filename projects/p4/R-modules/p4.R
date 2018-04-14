# Udacity Data Analyst Nanodegree - P4 Explore and Analyse Data

# Run this command while "p4" is the current working directory
modules <- c("get_xls.py", "scrape_webpage.py", "scrape_wikipedia.py",
             "scrape_others.py")
sapply(modules,
       function(x) system(paste("python3 ./python-modules/", x, sep = "")))
