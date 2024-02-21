# Load the jsonlite package for parsing JSON data
library(jsonlite)

# Load your JSON data from the file
df <- fromJSON("data_ais/api_response_2024-02-14_20-10-06.json", flatten = TRUE)

# Number of observations
num_observations <- nrow(df)
cat("Number of observations:", num_observations, "\n")

# Number of missing observations
num_missing <- sum(is.na(df))
cat("Number of missing observations:", num_missing, "\n")
