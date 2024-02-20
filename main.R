# Load the jsonlite package for parsing JSON data
library(jsonlite)

df <- fromJSON("data_ais/api_response_2023-06-08_17-01-17.txt", flatten = TRUE)

# Number of observations
num_observations <- nrow(df)
cat("Number of observations:", num_observations, "\n")

# Number of missing observations
num_missing <- sum(is.na(df))
cat("Number of missing observations:", num_missing, "\n")

# Assess whether additional cleaning or data collection is necessary
if (num_missing > 0) {
  cat("Additional cleaning or data collection may be necessary.\n")
} else {
  cat("No additional cleaning or data collection is necessary.\n")
}

# Number of missing observations
num_missing <- sum(is.na(df))
cat("Number of missing observations:", num_missing, "\n")

# Assess whether additional cleaning or data collection is necessary
if (num_missing > 0) {
  cat("Additional cleaning or data collection may be necessary.\n")
} else {
  cat("No additional cleaning or data collection is necessary.\n")
}
