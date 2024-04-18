# Imports
library(ecp)

# R_changepoint_analysis.R takes the smoothed time series and performs changepoint detection with e.divisive
# (https://www.rdocumentation.org/packages/ecp/versions/3.1.3/topics/e.divisive)
# over several parameter settings and outputs a .csv with the changepoints found at these
# different settings.
# You need to specify the root directory

# SPECIFY ROOT DIRECTORY
base_dir <- "/Users/madelinehamilton/Documents/python_stuff/tar_repo/"

# Directory of smoothed normalized time series
ts_name <- paste(base_dir, "output_data/time_series/norm_time_series.csv", sep = "")
# Output .csv directory
changepoints_csv_name <- paste(base_dir, "output_data/changepoints/r_changepoints.csv", sep = "")

# Read in the smoothed time series, remove the first two and last two rows
ts_df <- read.csv(ts_name)
ts_df <- na.omit(ts_df)
# Remove the "Year" column
ts_df <- ts_df[-c(1)]

# Parameter ranges to use
to_analyze <- c(colnames(ts_df), "Multivariate")
alphas <- list(1, 2)
k_list <- list(1, 2, 3, 4, "NULL")
sizes <- list(5, 6, 7, 8, 9, 10)

# This df will hold the changepoints
changepoints_df <- data.frame(feature = factor(), alpha=factor(), k=factor(), min_size=factor(), pos = numeric())

# Iterate through each feature we need to analyze (the multivariate analysis will be performed
# in the final iteration)
for (feat in to_analyze)
{
  mat <- 0
  # Check for multivariate
  if (feat == "Multivariate")
  {
    mat <- as.matrix(ts_df)
  } else {
    # If univariate, get the feature we need
    mat <- matrix(c(ts_df[[feat]]), nrow=69) 
  }
  # Iterate through the parameter settings
  for (a_val in alphas)
  {
    for (k_val in k_list)
    {
      for (s_val in sizes)
      {
        # Check for NULL. R doesn't appreciate NULL when iterating/storing info so 
        # I have to convert it to a string  
        k_to_use <- k_val
        if (is.character(k_val))
        {
          k_to_use <- NULL
        }
        # Changepoint detection
        cpts <- e.divisive(mat, sig.lvl = 0.05, R = 199, k = k_to_use, min.size = s_val, alpha = a_val)
        points <- cpts$estimates
        # Remove the first and last values (the first and last positions are always changepoints with this algorithm)
        points <- points[-c(1, length(points))]
        # Store information (changepoints + parameter settings used)
        for (point in points){
          info <- data.frame(feature=feat, alpha=a_val, k=k_val, min_size=s_val, pos = point)
          changepoints_df = rbind(changepoints_df, info)
        }
      }
    }
  }
}

# Save .csv
write.csv(changepoints_df, changepoints_csv_name, row.names = FALSE)
